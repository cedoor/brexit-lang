#
# EC2 setup script.
#

# Get the parameter (path of .env file).
ENV_FILE_PATH="$1"

# Set current script position path.
SCRIPT_PATH=$(dirname "$(readlink -f "$0")")

# External scripts.
source "$SCRIPT_PATH/colors.sh"
source "$SCRIPT_PATH/utils.sh"
source "$ENV_FILE_PATH"

# Convert one-space separeted strings in array.
EC2_HOSTS=($EC2_HOSTS)

installSystemPackages() {
    # Create .hushlogin file to silent welcome host message.
    touch /tmp/.hushlogin
    scp -o StrictHostKeyChecking=no -q -i "$IDENTITY_FILE_PATH" /tmp/.hushlogin "ubuntu@$EC2_HOST:/home/ubuntu/"

    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
        sudo apt-get -qq -o Dpkg::Use-Pty=0 update
        sudo apt-get -qq -y -o Dpkg::Use-Pty=0 upgrade
        sudo apt-get -qq -y -o Dpkg::Use-Pty=0 install openjdk-8-jdk python3-pip unzip
        pip3 install -q --user numpy
EOF
}

installHadoop() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
        wget -q https://www-us.apache.org/dist/hadoop/common/hadoop-2.7.7/hadoop-2.7.7.tar.gz
        tar zxf hadoop-2.7.7.tar.gz
        rm -fr hadoop-2.7.7.tar.gz* hadoop
        mv hadoop-2.7.7 hadoop
        echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> .bash_profile
        echo "export PATH=\$PATH:\$JAVA_HOME/bin" >> .bash_profile
        echo "export HADOOP_HOME=/home/ubuntu/hadoop" >> .bash_profile
        echo "export PATH=\$PATH:/home/ubuntu/hadoop/bin" >> .bash_profile
        echo "export HADOOP_CONF_DIR=/home/ubuntu/hadoop/etc/hadoop" >> .bash_profile
EOF
}

installSpark() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
        wget -q http://mirror.nohup.it/apache/spark/spark-2.3.4/spark-2.3.4-bin-hadoop2.7.tgz
        tar xzf spark-2.3.4-bin-hadoop2.7.tgz
        rm -fr spark-2.3.4-bin-hadoop2.7.tgz* spark
        mv spark-2.3.4-bin-hadoop2.7 spark
        cp spark/conf/spark-env.sh.template spark/conf/spark-env.sh
        echo "export SPARK_MASTER_HOST=${EC2_HOSTS[0]}" >> spark/conf/spark-env.sh
        echo "export HADOOP_CONF_DIR=/home/ubuntu/hadoop/etc/hadoop" >> spark/conf/spark-env.sh
        echo "export PYSPARK_PYTHON=python3" >> ~/.bash_profile
EOF
}

configureHadoop() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
        cp \$HADOOP_CONF_DIR/mapred-site.xml.template \$HADOOP_CONF_DIR/mapred-site.xml
        sed -i "25s/.*/export JAVA_HOME=\/usr\/lib\/jvm\/java-8-openjdk-amd64/" \$HADOOP_CONF_DIR/hadoop-env.sh
        echo "<configuration><property><name>fs.defaultFS</name><value>hdfs://$EC2_HOST:9000/</value></property></configuration>" > \$HADOOP_CONF_DIR/core-site.xml
        echo "<configuration><property><name>yarn.nodemanager.aux-services</name><value>mapreduce_shuffle</value></property><property><name>yarn.resourcemanager.hostname</name><value>$EC2_HOST</value></property></configuration>" > \$HADOOP_CONF_DIR/yarn-site.xml
        echo "<configuration><property><name>mapreduce.jobtracker.address</name><value>$EC2_HOST:54311</value></property><property><name>mapreduce.framework.name</name><value>yarn</value></property></configuration>" > \$HADOOP_CONF_DIR/mapred-site.xml
EOF
}

configureMaster() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
        echo "<configuration ><property><name>dfs.replication</name><value>3</value></property><property><name>dfs.namenode.name.dir</name><value>file:///home/ubuntu/hadoop/data/hdfs/namenode</value></property></configuration>" > \$HADOOP_CONF_DIR/hdfs-site.xml
        mkdir -p \$HADOOP_HOME/data/hdfs/namenode
        rm -f \$HADOOP_CONF_DIR/slaves \$HADOOP_CONF_DIR/masters
        echo "$EC2_HOST" >> \$HADOOP_CONF_DIR/masters
        echo "${EC2_HOSTS[@]:1}" | tr " " "\n" > \$HADOOP_CONF_DIR/slaves
        ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa 2> /dev/null <<< y > /dev/null
        cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
        echo "Host *" >> ~/.ssh/config
        echo "StrictHostKeyChecking no" >> ~/.ssh/config
EOF

    ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" "cat ~/.ssh/id_rsa.pub" > /tmp/id_rsa.pub
}

configureSlave() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
        echo "<configuration ><property><name>dfs.replication</name><value>3</value></property><property><name>dfs.datanode.data.dir</name><value>file:///home/ubuntu/hadoop/data/hdfs/datanode</value></property></configuration>" > \$HADOOP_CONF_DIR/hdfs-site.xml
        mkdir -p \$HADOOP_HOME/data/hdfs/datanode
EOF
    ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" "cat >> ~/.ssh/authorized_keys" < /tmp/id_rsa.pub
}

startMaster () {
  ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
      hdfs namenode -format
      \$HADOOP_HOME/sbin/start-dfs.sh
      \$HADOOP_HOME/sbin/start-yarn.sh
      \$HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver
      bash spark/sbin/start-master.sh
EOF
}

startSlaves () {
    for EC2_HOST in "${EC2_HOSTS[@]:1}"; do
        ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
            bash spark/sbin/start-slave.sh "spark://${EC2_HOSTS[0]}:7077" &> /dev/null
EOF
    done
}

echo -e "\n───────────────▄▄───▐█
───▄▄▄───▄██▄──█▀───█─▄
─▄██▀█▌─██▄▄──▐█▀▄─▐█▀
▐█▀▀▌───▄▀▌─▌─█─▌──▌─▌
▌▀▄─▐──▀▄─▐▄─▐▄▐▄─▐▄─▐▄
\n${TEXT_PRIMARY}♦ EC2 cluster setup${NC}"

for i in "${!EC2_HOSTS[@]}"; do
    EC2_HOST=${EC2_HOSTS[$i]}

    echo -e "\nHost ${TEXT_WARNING}$EC2_HOST${NC} setup:"

    progress installSystemPackages "Installing system packages"

    progress installHadoop "Installing Hadoop"

    progress installSpark "Installing Spark"

    progress configureHadoop "Hadoop configuration"

    if [ "$i" = "0" ]; then
        progress configureMaster "Master node configuration"
    fi

    if [ "$i" != "0" ]; then
        progress configureSlave "Slave node configuration"
    fi
done

progress startMaster "Running master"

progress startSlaves "Running slaves"

echo -e "\n${TEXT_SUCCESS}EC2 cluster setup completed!${NC}\n"