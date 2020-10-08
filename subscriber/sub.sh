#!/bin/sh


pip install paho-mqtt==1.5.1
pip install -U setuptools
pip install matplotlib
pip install pandas
pip install seaborn
python -u sub.py ../config/config.json