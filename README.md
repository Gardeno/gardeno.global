# Running locally

0) Install `docker-compose`: https://docs.docker.com/compose/

1) Run `docker-compose`:

```
docker-compose build
docker-compose up
```

# To apply migrations

```
docker-compose run web python3 manage.py migrate
```

# Some important commands

```
docker-compose run web python3 manage.py collectstatic --noinput
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


# To recreate containers / volumes

```
docker system prune -a
```

# Running in production

```
docker-compose -f docker-compose.yml -f production.yml up -d
```

To deploy, use the following:

```
docker-compose build web
docker-compose up --no-deps -d web
```