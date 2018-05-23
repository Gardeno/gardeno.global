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