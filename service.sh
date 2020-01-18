#!/bin/bash

if [ "$1" = 'start' ];
then
    sudo systemctl enable botify.service
    sudo systemctl start botify.service
elif [ "$1" = 'stop' ];
then
    sudo systemctl disable botify.service
    sudo systemctl start botify.service
fi
