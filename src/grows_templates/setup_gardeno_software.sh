#!/usr/bin/env bash

echo "$(date) - Setting up" >> /home/pi/setup.log

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{}' \
  [STARTED_SETUP_URL]

apt-get update

apt-get install -y autossh htop telnet supervisor

echo "SENSOR_URL=\"[SENSOR_URL]\"" >> /etc/environment

curl [MAIN_EXECUTABLE_DOWNLOAD_URL] --output /home/pi/gardeno.py
chmod +x /home/pi/gardeno.py
#chown pi:pi /home/pi/gardeno.py

IFS='' read -r -d '' SupervisorConfiguration <<"EOF"
[program:gardeno]
command = /home/pi/gardeno.py
directory = /home/pi
user = pi
autostart = true
autorestart = true
stdout_logfile = /var/log/supervisor/gardeno.log
stderr_logfile = /var/log/supervisor/gardeno.log
EOF

echo $SupervisorConfiguration > /etc/supervisor/conf.d/gardeno.conf

service supervisor restart

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{}' \
  [FINISHED_SETUP_URL]

echo -e '#!/usr/bin/env bash\n# Update script will be here potentially' > /boot/PiBakery/everyBoot.sh

