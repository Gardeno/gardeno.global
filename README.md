# Running locally

0) Install `docker-compose`: https://docs.docker.com/compose/

1) Run `docker-compose`:

```
docker-compose build
docker-compose up
```

# Deployment instructions

0) Install pip and virtualenv (instructions are for Ubuntu 16.04)

```
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install virtualenv
```

1) Setup virtualenv

```
virtualenv -p python3 venv
```

2) Source virtualenv

```
source venv/bin/activate
```

3) Install requirements

```
pip install -r requirements.txt
```

4) Copy local settings file

```
cp gardeno/settings_env.example.prod.py gardeno/settings_env.py
```

5) Setup uwsgi / Django / Nginx using the following steps:

    1) Install uwsgi system-wide
    
        ```
        sudo pip3 install uwsgi
        ```
    
    2) Edit `rc.local` to include the following command:
    
        ```
        /usr/local/bin/uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data --daemonize /var/log/uwsgi-emperor.log
        ```
        
6) Link the gardeno uwsgi file with:

```
sudo ln -s /home/ubuntu/gardeno/config/uwsgi/gardeno.global.ini /etc/uwsgi/vassals/gardeno.global.ini 
```
    
7) Test that uwsgi pulls in the config file with:

```
/usr/local/bin/uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data
```

8) Link the gardeno nginx file and reload nginx with:

```
sudo ln -s /home/ubuntu/gardeno/config/nginx/gardeno.global /etc/nginx/sites-enabled/gardeno.global
sudo /etc/init.d/nginx restart
```


# Some important commands

```
python manage.py collectstatic --noinput
```

```
python manage.py migrate
```

# Colors

Red
#FF7276

Orange
#F4B223

Blue
#57B6B2

Green
#79DEA8

Light Green
#d0f4de

Dark Green
#2c3c44
