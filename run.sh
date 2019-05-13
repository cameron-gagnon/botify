#!/bin/sh

echo "Killing any previous botifies..."

echo `pkill botify/main.py`

echo "Starting botify"
nohup python3.5 ./main.py  &
sleep 2
echo "Started botify"
