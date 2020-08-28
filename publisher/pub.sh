#!/bin/sh

pip install paho-mqtt
pip install psutil
pip install matplotlib
pip install pandas
pip install seaborn
python -u pub.py ../config/config.json

