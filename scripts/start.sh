echo -e "\nDownload scripts"

ssh -i "$1" "$2" << EOF
rm -fr *
wget -q https://github.com/cedoor/brexit-lang/archive/master.zip
unzip -q master.zip
pip-3.6 install --user -q -r brexit-lang-master/requirements.txt
echo "export PYSPARK_PYTHON=python3" >> ~/.bash_profile
mkdir data
EOF

echo -e "\nMove data and .env"

scp -r -i "$1" "$3" "$2:/home/hadoop"
scp -i "$1" "$4" "$2:/home/hadoop/brexit-lang-master"

echo -e "\nRun analysis"

ssh -i "$1" "$2" << EOF
hdfs dfs -put ~/data/* /data
python3 brexit-lang-master/scripts/analysis_1.py
spark-submit brexit-lang-master/scripts/analysis_2.py
spark-submit brexit-lang-master/scripts/analysis_3.py
EOF