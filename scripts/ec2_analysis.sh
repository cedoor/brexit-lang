ENV_FILE_PATH="$1"

# shellcheck disable=SC1090
source "$ENV_FILE_PATH"

# Convert one-space separeted strings in array.
EC2_HOSTS=($EC2_HOSTS)

ssh -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
    wget -q https://github.com/cedoor/brexit-lang/archive/master.zip
    unzip -q master.zip
    rm -fr master.zip brexit-lang
    mv brexit-lang-master brexit-lang
    pip3 install --user -q -r brexit-lang/requirements.txt
EOF

scp -r -i "$IDENTITY_FILE_PATH" "$DATA_PATH" "ubuntu@${EC2_HOSTS[0]}:/home/ubuntu"
scp -i "$IDENTITY_FILE_PATH" "$ENV_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}:/home/ubuntu/brexit-lang"

ssh -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
    hdfs dfs -put ~/data /
    ./spark/bin/spark-submit brexit-lang/scripts/analysis_3.py
EOF