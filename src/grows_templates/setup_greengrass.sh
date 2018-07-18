#!/usr/bin/env bash

echo "$(date) - Setting up" >> /home/pi/setup.log

wget -O /home/pi/greengrass-linux-armv7l-1.5.0.tar.gz https://d1q3pnw6jn9hrp.cloudfront.net/raspberrypi/greengrass-linux-armv7l-1.5.0.tar.gz

echo "$(date) - Downloaded Greengrass file" >> /home/pi/setup.log

tar -xzvf /home/pi/greengrass-linux-armv7l-1.5.0.tar.gz -C /

echo '[REPLACE_CERT_PEM]' > /greengrass/certs/cert.pem
echo '[REPLACE_PRIVATE_KEY]' > /greengrass/certs/private.key
echo '[REPLACE_PUBLIC_KEY]' > /greengrass/certs/public.key

echo "$(date) - Wrote certs" >> /home/pi/setup.log

wget -O /greengrass/certs/root.ca.pem http://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem

echo "$(date) - Downloaded root" >> /home/pi/setup.log

echo -e '{"coreThing":{"caPath":"root.ca.pem","certPath":"cert.pem","keyPath":"private.key","thingArn":"[THING_ARN_HERE]","iotHost":"[AWS_IOT_CUSTOM_ENDPOINT]","ggHost":"greengrass.iot.[AWS_REGION_HERE].amazonaws.com"},"runtime":{"cgroup":{"useSystemd":"yes"}},"managedRespawn":false}' > /greengrass/config/config.json

echo "$(date) - Wrote config" >> /home/pi/setup.log

echo "-----" >> /home/pi/setup.log

/greengrass/ggc/core/greengrassd start

echo -e '#!/usr/bin/env bash\n/greengrass/ggc/core/greengrassd start' > /boot/PiBakery/everyBoot.sh

