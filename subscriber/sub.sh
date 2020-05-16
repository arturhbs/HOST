#!/bin/sh

apk add install mosquitto 
apk add mosquitto-clients
python -u sub.py