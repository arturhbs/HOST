import os

print("Starting mosquitto_sub")
os.system('mosquitto_sub -h 172.17.0.1 -t test')
