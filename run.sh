#!/bin/sh

echo "Killing any previous botifies..."

echo `pkill python3.5`

echo "Starting botify"
sleep 2
nohup ./main.py  &
sleep 2
echo "Started botify"
