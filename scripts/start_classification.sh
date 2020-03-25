#
# Classification script.
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

startClassification() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
        ./spark/bin/spark-submit --master "spark://${EC2_HOSTS[0]}:7077" brexit-lang/scripts/analysis.py
EOF
    scp -q -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}:/home/ubuntu/classification_results.json" "$HOME/Downloads"
}

echo -e "\n───────────────▄▄───▐█
───▄▄▄───▄██▄──█▀───█─▄
─▄██▀█▌─██▄▄──▐█▀▄─▐█▀
▐█▀▀▌───▄▀▌─▌─█─▌──▌─▌
▌▀▄─▐──▀▄─▐▄─▐▄▐▄─▐▄─▐▄
\n${TEXT_PRIMARY}♦ Brexit language classification${NC}"

echo -e "\n• Running classification:"
startClassification

echo -e "\n${TEXT_SUCCESS}Brexit language classification completed, results saved on \"classification_results.json\" file!${NC}\n"