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

Obs: Get inside the codes at app directory and confirm if the host ip is correct

### 3- Running code with docker 
Execute commands below to run publish's code and subscribe's code, respectively:

```
$ docker run -d --name pub -v $(pwd)/app/publish.py:/app/code.py arturhbs/mqtt-python
```
```
$ docker run -d --name sub -v $(pwd)/app/subscribe.py:/app/code.py arturhbs/mqtt-python
```

## Debug mode
For access debug mode run follow code to see publisher's debug:

```
$ docker logs -f pub
```
Or use follow command to see subscribe's debug

```
$ docker logs -f sub
```