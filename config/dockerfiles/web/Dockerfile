FROM library/python:3.6.4-jessie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin postgresql-client supervisor nginx vim
RUN pip3 install --upgrade pip

RUN pip3 install uwsgi

# Code setup

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD ./src/requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD ./src /code/

# uwsgi setup

RUN mkdir /conf
COPY config/uwsgi/gardeno.global.ini /conf/gardeno.global.ini

# Nginx setup

COPY config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY config/nginx/server_config.conf /etc/nginx/server_config.conf
COPY config/nginx/gardeno.global /etc/nginx/sites-enabled
RUN rm /etc/nginx/sites-enabled/default

# Supervisord setup

COPY config/supervisord/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV GDAL_LIBRARY_PATH /usr/lib/ogdi/libgdal.so

CMD ["/usr/bin/supervisord"]