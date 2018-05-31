# Running locally

0) Install `docker-compose`: https://docs.docker.com/compose/

1) Run `docker-compose`:

```
docker-compose build
docker-compose up
```

# To apply migrations

```
docker-compose run web migrate
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
