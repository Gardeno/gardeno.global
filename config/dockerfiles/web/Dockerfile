FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y software-properties-common htop

RUN add-apt-repository -y ppa:ubuntugis/ppa
RUN apt-get update
RUN apt-get install -y gdal-bin python-gdal python3-gdal python3-pip
RUN pip3 install --upgrade pip

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD ./src/requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD ./src /code/