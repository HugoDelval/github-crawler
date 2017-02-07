FROM debian:latest

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-flask python3-pip
RUN pip3 install grequests
RUN mkdir /app
ADD . /app/
