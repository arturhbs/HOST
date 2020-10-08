#!/bin/sh

pip install paho-mqtt==1.5.1
pip install psutil
pip install matplotlib
pip install pandas
pip install seaborn
python -u pub.py ../config/config.json

