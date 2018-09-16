#!/usr/bin/env bash

# This file gets executed as the root user every single time the device boots
# The variable SENSOR_URL gets replaced before serving to the device.

echo "$(date) - Updating." >> /home/pi/setup.log

echo "$(date) - Downloading requirements from ${SENSOR_URL}requirements/." >> /home/pi/setup.log

sudo -u pi curl "${SENSOR_URL}requirements/" --output /home/pi/gardeno/requirements.txt

echo "$(date) - Downloading executable from ${SENSOR_URL}executable/." >> /home/pi/setup.log

sudo -u pi curl "${SENSOR_URL}executable/" --output /home/pi/gardeno/main.py
sudo -u pi chmod +x /home/pi/gardeno/main.py

echo "$(date) - Installing requirements." >> /home/pi/setup.log

sudo -u pi /home/pi/gardeno/venv/bin/pip install -r /home/pi/gardeno/requirements.txt

echo "$(date) - Restarting service." >> /home/pi/setup.log

service supervisor restart gardeno

echo "$(date) - Finished updating." >> /home/pi/setup.log
