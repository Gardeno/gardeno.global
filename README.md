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
    

http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html



# Some important commands

```
python manage.py collectstatic --noinput
```

```
python manage.py migrate
```

# Colors

Green
#5DFDCB

Orange
#FF8E72

Grey
#D9E5D6

Blue
#00A7E1

Yellow
#EDDEA4