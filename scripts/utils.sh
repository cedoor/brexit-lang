#
# General utilities.
#

# Color codes.
TEXT_PRIMARY='\033[1;34m'
TEXT_WARNING='\033[0;33m'
TEXT_ERROR='\033[1;31m'
TEXT_INFO='\033[1;37m'
TEXT_SUCCESS='\033[0;32m'
NC='\033[0m' # No Color

spinner() {
    MESSAGE=${1}
    echo
    while :; do
        for s in / - \\ \|; do
            echo -ne "\r${MESSAGE}:${TEXT_SUCCESS} ${s} ${NC}"
            sleep .1
        done
    done
}

progress() {
    # Run asynchronous function & save its pid
    spinner "$2" &
    SPINNER_PID=$!
    # Fake waiting
    sleep .5
    # do something
    $1 "$3" "$4"
    # Kill the spinner function
    disown ${SPINNER_PID}
    kill ${SPINNER_PID}
    echo -ne "\r$2:${TEXT_SUCCESS} 100% ${NC}\n"
}