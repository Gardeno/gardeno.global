# Running locally

0) Install `docker-compose`: https://docs.docker.com/compose/

1) Run `docker-compose`:

```
docker-compose build
docker-compose up
ngrok start --config config/ngrok.yml gardeno
```

# To apply migrations (locally)

```
docker-compose run web python3 manage.py makemigrations
docker-compose run web python3 manage.py migrate
docker-compose run web python3 manage.py loaddata /fixtures/users.json
docker-compose run web python3 manage.py loaddata /fixtures/safety.json
docker-compose run web python3 manage.py loaddata /fixtures/launch_signups.json
docker-compose run web python3 manage.py loaddata /fixtures/grows.json
```

# Some important commands (locally)

```
docker-compose run web python3 manage.py collectstatic --noinput
```

# To install new dependencies

```
docker exec -it gardenoglobal_web_1 pip3 install raven
docker exec -it gardenoglobal_web_1 pip3 freeze > src/requirements.txt
docker-compose build && docker-compose up
```

# To recreate containers / volumes

```
docker system prune -a
```

# To deploy

Copy `.env.example` to `deployment/DESIRED_ENVIRONMENT/.env`

Run `./deploy.sh`

# Running locally against a development database

After running `./deploy.sh` once (to tag the web image appropriately) run this:

```
docker run -it -p 8001:80 gardeno.global
```

To install fixtures against a development database

```
docker run -it -v $PWD/fixtures:/code/fixtures gardeno.global python3 manage.py loaddata fixtures/users.json
docker run -it -v $PWD/fixtures:/code/fixtures gardeno.global python3 manage.py loaddata fixtures/grows.json
```

To install database migrations against a development database

```
docker run -it gardeno.global python3 manage.py migrate
docker run -it gardeno.global python3 manage.py collectstatic
```

To install fixtures in production:

```
docker run -it -v $PWD/fixtures:/code/fixtures gardenoglobal_web python3 manage.py loaddata fixtures/events.json
docker run -it -v $PWD/fixtures:/code/fixtures gardenoglobal_web python3 manage.py loaddata fixtures/orders.json
docker run -it -v $PWD/fixtures:/code/fixtures gardenoglobal_web python3 manage.py loaddata fixtures/salads.json
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

# Running the scheduler

Run `rq-scheduler` to make sure jobs get in the queue:

```
docker-compose run web rqscheduler --host redis -i 5
```

Run `rq worker` to execute the jobs:

```
docker-compose run web rq worker -u redis://redis:6379
```

View queues at:

```
http://localhost:8001/admin/queues/
```

# Production

```
docker-compose -f docker-compose-production-jobs.yml run web rqscheduler --host gardeno.ujsafd.0001.usw2.cache.amazonaws.com -i 5
docker-compose -f docker-compose-production-jobs.yml run web rq worker -u redis://gardeno.ujsafd.0001.usw2.cache.amazonaws.com:6379
https://gardeno.global/admin/queues/

```