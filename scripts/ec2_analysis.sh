#
# EC2 analysis script.
#

# Get the parameter (path of .env file).
ENV_FILE_PATH="$1"

# Set current script position path.
SCRIPT_PATH=$(dirname "$(readlink -f "$0")")

# External scripts.
source "$SCRIPT_PATH/utils.sh"
source "$ENV_FILE_PATH"

# Convert one-space separeted strings in array.
EC2_HOSTS=($EC2_HOSTS)

installBrexitLang() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
        wget -q https://github.com/cedoor/brexit-lang/archive/master.zip
        unzip -q master.zip
        rm -fr master.zip brexit-lang
        mv brexit-lang-master brexit-lang
        pip3 install --user -q -r brexit-lang/requirements.txt
EOF
}

uploadData() {
    scp -q -r -i "$IDENTITY_FILE_PATH" "$DATA_PATH" "ubuntu@${EC2_HOSTS[0]}:/home/ubuntu"
    scp -q -i "$IDENTITY_FILE_PATH" "$ENV_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}:/home/ubuntu/brexit-lang"
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
        hdfs dfs -put ~/data /
EOF
}

startAnalysis() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
        ./spark/bin/spark-submit brexit-lang/scripts/analysis.py
EOF
}

echo -e "\n───────────────▄▄───▐█
───▄▄▄───▄██▄──█▀───█─▄
─▄██▀█▌─██▄▄──▐█▀▄─▐█▀
▐█▀▀▌───▄▀▌─▌─█─▌──▌─▌
▌▀▄─▐──▀▄─▐▄─▐▄▐▄─▐▄─▐▄
\n${TEXT_PRIMARY}♦ EC2 cluster analysis${NC}"

progress installBrexitLang "Installing BrexitLang from repository"

progress uploadData "Uploding analysis data"

progress startAnalysis "Running analysis"

echo -e "\n${TEXT_SUCCESS}EC2 cluster analysis completed!${NC}\n"