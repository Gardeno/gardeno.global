#!/usr/bin/env bash

# This file gets executed by the root user only a single time (when a newly flashed Rpi boots for the first time)

echo "$(date) - Setting up" >> /home/pi/setup.log

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{}' \
  [STARTED_SETUP_URL]

apt-get update

echo "$(date) - Installing dependencies" >> /home/pi/setup.log

apt-get install -y autossh htop telnet supervisor
pip install virtualenv

mkdir /home/pi/gardeno

virtualenv -p python3.4 /home/pi/gardeno/venv/

echo "SENSOR_URL=\"[SENSOR_URL]\"" >> /etc/environment

echo "$(date) - Downloading executable" >> /home/pi/setup.log

curl [MAIN_EXECUTABLE_DOWNLOAD_URL] --output /home/pi/gardeno/main.py
chmod +x /home/pi/gardeno/main.py
chown -R pi:pi /home/pi/gardeno/

IFS='' read -r -d '' SupervisorConfiguration <<"EOF"
[program:gardeno]
command = /home/pi/gardeno/venv/bin/python /home/pi/gardeno/main.py
directory = /home/pi/gardeno
user = pi
autorestart = true
stdout_logfile = /var/log/supervisor/gardeno.log
stderr_logfile = /var/log/supervisor/gardeno.log
EOF

echo "${SupervisorConfiguration}" > /etc/supervisor/conf.d/gardeno.conf

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{}' \
  [FINISHED_SETUP_URL]

echo -e '#!/usr/bin/env bash\ncurl [UPDATE_URL] | bash' > /boot/PiBakery/everyBoot.sh

echo "$(date) - Finished setting up. Rebooting." >> /home/pi/setup.log

reboot
