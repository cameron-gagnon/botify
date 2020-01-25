#!/bin/bash

echo "Starting botify"

source venv/bin/activate
nohup python ./main.py 2>&1 &
deactivate

echo "Started botify"
