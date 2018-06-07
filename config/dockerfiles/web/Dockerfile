FROM library/python:3.6.4-jessie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin postgresql-client
RUN pip3 install --upgrade pip

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD ./src/requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD ./src /code/

ENV GDAL_LIBRARY_PATH /usr/lib/ogdi/libgdal.so