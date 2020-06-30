import sys
import json
import time
from time import process_time, perf_counter # if use perf_counter will calculate time with sleep time 
import paho.mqtt.client as mqtt
import psutil

def count_publications(client):
    count_message(8, client)
    count_message(13,client)
    count_message(21,client)
    count_message(34,client)
    count_message(55,client)

def count_message(quantity, client):
    i=0
    timeStart = perf_counter()
    cpuTime = psutil.cpu_times()
    print('start_time: ')
    print(timeStart)
    print('\nCPU_Time: ')
    print(cpuTime)
    print('\n\n####################################')
    while True:
        time.sleep(1)
        i+=1
        message=str(i)
        if i <=quantity:
            client.publish('count',message)
        else:
            break
    timeEnd = perf_counter()
    timeTotal = timeEnd - timeStart
    client.publish('time',timeTotal)

def read_config_file(args):
    with open(args[1], 'r') as file:
        config = json.load(file)
    return config['publisher']

def main(args):
    # Read config file passed as argument
    config = read_config_file(args)
    # Connection with client paho.mqtt api
    client = mqtt.Client()
    client.connect(config['hostIP'], config['port'], config['keepAlive'])
    # Metrics about quantity of publications
    count_publications(client)
    # End client mqtt
    client.disconnect()

if __name__ == "__main__":
    cpuTime = psutil.cpu_times()
    print('\nCPU_Time: ')
    print(cpuTime)
    print('\n\n####################################')
    time.sleep(40)
    cpuTime = psutil.cpu_times()
    print('\nCPU_Time: ')
    print(cpuTime)
    print('\n\n####################################')
    args = sys.argv 
    main(args)    