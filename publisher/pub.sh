#!/bin/sh

pip install paho-mqtt
pip install psutil
python -u pub.py ./config/config.json

