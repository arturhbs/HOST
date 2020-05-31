# if use perf_counter will calculate time with sleep time 
import sys
import json
import time
from time import process_time, perf_counter
import paho.mqtt.client as mqtt

def Count_Message(client):
    i=0
    while True:
        time.sleep(1)
        i+=1
        message=str(i)
        if i <=10:
            client.publish('count',message)
        else:
            break

def Read_Config_File(args):
    with open(args[1], 'r') as file:
        config = json.load(file)
    return config['publisher']

def main(args):
    # Read config file passed as argument
    config = Read_Config_File(args)
    # Connection with client paho.mqtt api
    client = mqtt.Client()
    client.connect(config['hostIP'], config['port'], config['keepAlive'])
    # Start time count
    timeStart = perf_counter()
    Count_Message(client)
    timeEnd = perf_counter()
    timeTotal = timeEnd - timeStart
    client.publish('time',timeTotal)
    client.disconnect()
    print("Time start: ", timeStart)
    print("Time end: ", timeEnd)
    print("Time in seconds: ", timeTotal)

if __name__ == "__main__":
    args = sys.argv 
    main(args)    