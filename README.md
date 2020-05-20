# MQTT-python

## Introduction

Create a MQTT with subscribers and publishers that can communicate using Mosquitto as a broker and docker for python files.

## How to get it work
Some steps you need to follow to get it worked 

### 1- Get docker image
```
$ docker pull arturhbs/mqtt-python:latest
```

### 2- Get code source

```
$ git clone https://github.com/arturhbs/MQTT-python.git
```
```
$ cd MQTT-python
```

### 3- Running code with docker 
Execute commands below to run publish's and subscribe's code, respectively:

```
$ docker-compose up -d --scale publisher=5 --scale subscriber=2
```

It is possible to change the number of how many services it will work as your wish.

If need to run more than 20 services simultaneously and it gets an error, it is recommended to try:

```
export DOCKER_CLIENT_TIMEOUT=120
export COMPOSE_HTTP_TIMEOUT=120
```

Other solution is to restart Docker and increase Docker CPU and memory

## Debug mode
For access debug mode run follow code to see publisher's debug:

```
$ docker-compose logs -f 
```