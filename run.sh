#!/bin/bash

echo "Killing any previous botifies..."

echo `pkill python`

echo "Starting botify"
sleep 2
source venv/bin/activate
nohup python ./main.py 2>&1 &
deactivate
sleep 2
echo "Started botify"
