#
# Analysis script.
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

startAnalysis() {
    ssh -T -o StrictHostKeyChecking=no -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}" << EOF
        ./spark/bin/spark-submit --master "spark://${EC2_HOSTS[0]}:7077" brexit-lang/scripts/analysis.py
EOF
    scp -q -i "$IDENTITY_FILE_PATH" "ubuntu@${EC2_HOSTS[0]}:/home/ubuntu/analysis_results.json" "$HOME/Downloads"
}

echo -e "\n───────────────▄▄───▐█
───▄▄▄───▄██▄──█▀───█─▄
─▄██▀█▌─██▄▄──▐█▀▄─▐█▀
▐█▀▀▌───▄▀▌─▌─█─▌──▌─▌
▌▀▄─▐──▀▄─▐▄─▐▄▐▄─▐▄─▐▄
\n${TEXT_PRIMARY}♦ Brexit language analysis${NC}"

echo -e "\n• Running analysis:"
startAnalysis

echo -e "\n${TEXT_SUCCESS}Brexit language analysis completed, you can find the results in \"~/Downloads/analysis_results.json\" file${NC}\n"