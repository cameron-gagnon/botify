#!/bin/bash

truncate_file() {
    if [[ ! -e $1 ]]; then
        echo "File $1 doesn't exist. Not truncating..."
        return
    fi

    tail -n 5000 $1 > ${1}.bak
    mv ${1}.bak $1
}

set -e echo "Starting botify"

echo `pkill -f botify`

truncate_file debug.log
truncate_file error.log

source venv/bin/activate
nohup python ./main.py 2>&1 &
deactivate

echo "Started botify"

ps aux | grep -v grep | grep botify
