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
docker container ls
docker container rm CONTAINER_WEB_ID
docker container rm CONTAINER_DB_ID
docker volume ls
docker volume rm VOLUME_WEB_ID
docker volume rm VOLUME_DB_ID
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