#!/usr/bin/env bash

# This file gets executed as the root user every single time the device boots

echo "$(date) - Updating." >> /home/pi/setup.log

echo "$(date) - Downloading requirements." >> /home/pi/setup.log

echo "${SENSOR_URL}requirements/"

sudo -u pi curl "${SENSOR_URL}requirements/" --output /home/pi/gardeno/requirements.txt

echo "$(date) - Downloading executable." >> /home/pi/setup.log

sudo -u pi curl "${SENSOR_URL}executable/" --output /home/pi/gardeno/main.py
sudo -u pi chmod +x /home/pi/gardeno/main.py

sudo -u pi /home/pi/gardeno/venv/bin/pip install -r /home/pi/gardeno/requirements.txt

service supervisor restart gardeno

echo "$(date) - Finished updating." >> /home/pi/setup.log
