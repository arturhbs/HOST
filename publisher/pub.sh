#!/bin/sh

pip install paho-mqtt
apk add install mosquitto 
apk add mosquitto-clients
python -u pub.py