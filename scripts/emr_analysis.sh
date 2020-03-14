echo -e "\nDownloading scripts..."

ENV_FILE_PATH="$1"

source "$ENV_FILE_PATH"

ssh -i "$IDENTITY_FILE_PATH" "$EMR_HOST" << EOF
rm -fr *
wget -q https://github.com/cedoor/brexit-lang/archive/master.zip
unzip -q master.zip
pip-3.6 install --user -q -r brexit-lang-master/requirements.txt
echo "export PYSPARK_PYTHON=python3" >> ~/.bash_profile
mkdir data
EOF

echo -e "\nMoving json data and .env file..."

scp -r -i "$IDENTITY_FILE_PATH" "$DATA_PATH" "$EMR_HOST:/home/hadoop"
scp -i "$IDENTITY_FILE_PATH" "$ENV_FILE_PATH" "$EMR_HOST:/home/hadoop/brexit-lang-master"

echo -e "\nRunning analysis..."

ssh -i "$IDENTITY_FILE_PATH" "$EMR_HOST" << EOF
hdfs dfs -put ~/data /
python3 brexit-lang-master/scripts/analysis_1.py
spark-submit brexit-lang-master/scripts/analysis_2.py
spark-submit brexit-lang-master/scripts/analysis_3.py
EOF