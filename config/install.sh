#!/bin/bash

#== FILL IN THESE VALUES ==#
service_name="botify"
description="Song request website that receives !sr from stroopc's chatbot"
#==========================#

if [[ $UID != 0 ]]; then
    echo "Please run this script with sudo"
    echo "sudo $0 $*"
    exit 1
fi

username=$(logname)
filename="${service_name}.service"

# clear file again before we create it
rm $filename

echo "[Unit]" >> $filename
echo "Description=$description" >> $filename
echo "" >> $filename
echo "[Install]" >> $filename
echo "WantedBy=multi-user.target" >> $filename
echo "" >> $filename
echo "[Service]" >> $filename
echo "User=$username" >> $filename
echo "Type=forking" >> $filename
echo "WorkingDirectory=/home/$username/src/$service_name" >> $filename
echo "ExecStart=/home/$username/src/$service_name/run.sh" >> $filename
echo "Restart=always" >> $filename
echo "RestartSec=3" >> $filename

cp $filename /etc/systemd/system/$filename

sudo systemctl enable $service_name
sudo systemctl start $service_name
