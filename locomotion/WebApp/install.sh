#!/bin/bash

sudo chmod +x server.py
sudo ln -s server.py /usr/local/bin/server.py
sudo ln -s rover.service /etc/systemd/system/rover.service
sudo systemctl daemon-reload
sudo systemctl start rover.service