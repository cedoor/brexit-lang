ENV_FILE_PATH="$1"

# shellcheck disable=SC1090
source "$ENV_FILE_PATH"

# Convert one-space separeted strings in array.
EC2_HOSTS=($EC2_HOSTS)

for i in "${!EC2_HOSTS[@]}"; do
    EC2_HOST=${EC2_HOSTS[$i]}

    ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
    sudo apt update
    sudo apt dist-upgrade -y
    sudo apt install openjdk-8-jdk python3-pip unzip -y
    pip3 install --user numpy
EOF

ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
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

ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
    wget -q http://mirror.nohup.it/apache/spark/spark-2.3.4/spark-2.3.4-bin-hadoop2.7.tgz
    tar xzf spark-2.3.4-bin-hadoop2.7.tgz
    rm -fr spark-2.3.4-bin-hadoop2.7.tgz* spark
    mv spark-2.3.4-bin-hadoop2.7 spark
    echo "export SPARK_MASTER_HOST=${EC2_HOSTS[0]}" >> spark/conf/spark-env.sh
    echo "export HADOOP_CONF_DIR=/home/ubuntu/hadoop/etc/hadoop" >> spark/conf/spark-env.sh
    echo "export PYSPARK_PYTHON=python3" >> ~/.bash_profile
    cp spark/conf/spark-env.sh.template spark/conf/spark-env.sh
EOF

ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
    cp \$HADOOP_CONF_DIR/mapred-site.xml.template \$HADOOP_CONF_DIR/mapred-site.xml
    sed -i "25s/.*/export JAVA_HOME=\/usr\/lib\/jvm\/java-8-openjdk-amd64/" \$HADOOP_CONF_DIR/hadoop-env.sh
    echo "<configuration><property><name>fs.defaultFS</name><value>hdfs://$EC2_HOST:9000/</value></property></configuration>" > \$HADOOP_CONF_DIR/core-site.xml
    echo "<configuration><property><name>yarn.nodemanager.aux-services</name><value>mapreduce_shuffle</value></property><property><name>yarn.resourcemanager.hostname</name><value>$EC2_HOST</value></property></configuration>" > \$HADOOP_CONF_DIR/yarn-site.xml
    echo "<configuration><property><name>mapreduce.jobtracker.address</name><value>$EC2_HOST:54311</value></property><property><name>mapreduce.framework.name</name><value>yarn</value></property></configuration>" > \$HADOOP_CONF_DIR/mapred-site.xml
EOF

    if [ "$i" = "0" ]; then
        ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
    echo "<configuration ><property><name>dfs.replication</name><value>3</value></property><property><name>dfs.namenode.name.dir</name><value>file:///home/ubuntu/hadoop/data/hdfs/namenode</value></property></configuration>" > \$HADOOP_CONF_DIR/hdfs-site.xml
    mkdir -p \$HADOOP_HOME/data/hdfs/namenode
    rm -f \$HADOOP_CONF_DIR/slaves \$HADOOP_CONF_DIR/masters
    echo "$EC2_HOST" >> \$HADOOP_CONF_DIR/masters
    echo "${EC2_HOSTS[@]:1}" | tr " " "\n" > \$HADOOP_CONF_DIR/slaves
    ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa 2>/dev/null <<< y >/dev/null
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
EOF
        ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" 'cat ~/.ssh/id_rsa.pub' > /tmp/id_rsa.pub
    fi

    if [ "$i" != "0" ]; then
        ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
    echo "<configuration ><property><name>dfs.replication</name><value>3</value></property><property><name>dfs.datanode.data.dir</name><value>file:///home/ubuntu/hadoop/data/hdfs/datanode</value></property></configuration>" > \$HADOOP_CONF_DIR/hdfs-site.xml
    mkdir -p \$HADOOP_HOME/data/hdfs/datanode
EOF
        ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" 'cat >> ~/.ssh/authorized_keys' < /tmp/id_rsa.pub
    fi
done

# TODO: add hosts in know host ssh file.
ssh -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
    hdfs namenode -format
    \$HADOOP_HOME/sbin/start-dfs.sh
    \$HADOOP_HOME/sbin/start-yarn.sh
    \$HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver

    bash spark/sbin/start-master.sh
EOF

for EC2_HOST in "${EC2_HOSTS[@]:1}"; do
  ssh -i "$IDENTITY_FILE_PATH" "ubuntu@$EC2_HOST" << EOF
    bash spark/sbin/start-slave.sh "spark://${EC2_HOSTS[0]}:7077"
EOF
done