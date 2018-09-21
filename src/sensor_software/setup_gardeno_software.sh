#!/usr/bin/env bash

# This file gets executed by the root user only a single time (when a newly flashed Rpi boots for the first time)

echo "$(date) - Setting up" >> /home/pi/setup.log

apt-get update >> /home/pi/setup.log 2>&1

echo "$(date) - Installing dependencies" >> /home/pi/setup.log

apt-get install -y htop telnet supervisor openvpn >> /home/pi/setup.log 2>&1
pip install virtualenv >> /home/pi/setup.log 2>&1

mkdir /home/pi/gardeno >> /home/pi/setup.log 2>&1
chown pi:pi /home/pi/gardeno >> /home/pi/setup.log 2>&1

echo "$(date) - Creating virtualenv" >> /home/pi/setup.log

sudo -u pi virtualenv -p python3 /home/pi/gardeno/venv/ >> /home/pi/setup.log 2>&1

echo "$(date) - Creating helper files and cleaning up directories" >> /home/pi/setup.log

echo "tail -f /var/log/supervisor/gardeno.log" > /home/pi/logs.sh && chmod +x /home/pi/logs.sh
echo "service supervisor restart gardeno" > /home/pi/restart.sh && chmod +x /home/pi/restart.sh
echo "service supervisor stop gardeno" > /home/pi/stop.sh && chmod +x /home/pi/stop.sh
echo "service supervisor start gardeno" > /home/pi/start.sh && chmod +x /home/pi/start.sh

# The following directories only exist because of rpi-update I think but not really sure

cd /home/pi && rm -rf {Desktop,Documents,Downloads,Music,Pictures,Public,Templates,Videos,python_games}

echo "$(date) - Setting up supervisor" >> /home/pi/setup.log

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

curl [FINISHED_SETUP_URL] >> /home/pi/setup.log 2>&1

echo -e '#!/usr/bin/env bash\ncurl [UPDATE_URL] | bash' > /boot/PiBakery/everyBoot.sh

echo "$(date) - Finished setting up. Rebooting." >> /home/pi/setup.log

reboot
