#!/usr/bin/env bash

# This file gets executed as the root user every single time the device boots
# The variable SENSOR_URL gets replaced before serving to the device.

echo "$(date) - Updating." >> /home/pi/setup.log

echo "$(date) - Downloading environment file from [SENSOR_URL]environment/" >> /home/pi/setup.log

sudo -u pi curl "[SENSOR_URL]environment/" --output /home/pi/gardeno/.env >> /home/pi/setup.log 2>&1

echo "$(date) - Downloading requirements from [SENSOR_URL]requirements/" >> /home/pi/setup.log

sudo -u pi curl "[SENSOR_URL]requirements/" --output /home/pi/gardeno/requirements.txt >> /home/pi/setup.log 2>&1

echo "$(date) - Downloading executable from [SENSOR_URL]executable/" >> /home/pi/setup.log

sudo -u pi curl "[SENSOR_URL]executable/" --output /home/pi/gardeno/main.py >> /home/pi/setup.log 2>&1
sudo -u pi chmod +x /home/pi/gardeno/main.py >> /home/pi/setup.log 2>&1

echo "$(date) - Downloading OpenVPN config from [SENSOR_URL]vpn_config/" >> /home/pi/setup.log

sudo -u pi curl "[SENSOR_URL]vpn_config/" --output /home/pi/gardeno/sensor.ovpn >> /home/pi/setup.log 2>&1

echo "$(date) - Installing requirements." >> /home/pi/setup.log

sudo -u pi /home/pi/gardeno/venv/bin/pip install -r /home/pi/gardeno/requirements.txt >> /home/pi/setup.log 2>&1

echo "$(date) - Restarting service." >> /home/pi/setup.log

service supervisor restart gardeno >> /home/pi/setup.log 2>&1

echo "$(date) - Finished updating." >> /home/pi/setup.log
