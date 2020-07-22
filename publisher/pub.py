import sys
import json
import time
from time import process_time, perf_counter # if use perf_counter will calculate time with sleep time 
import paho.mqtt.client as mqtt
import psutil

cpuTimeArray = []
cpuTimePIDArray = []
memVirtualArray = []
memInfoArray = []
diskUsageArray = []

def count_publications(client):
    count_message(8, client)
    count_message(13,client)
    count_message(21,client)
    count_message(34,client)
    count_message(55,client)

def count_message(quantity, client):
    i=0
    while True:
        declare_metrics()
        time.sleep(1)
        i+=1
        message=str(i)
        if i <=quantity:
            client.publish('count',message)
        else:
            break
    timeEnd = perf_counter()

def read_config_file(args):
    with open(args[1], 'r') as file:
        config = json.load(file)
    return config['publisher']

def declare_metrics():
    p = psutil.Process()
    cpuTime = psutil.cpu_times()
    cpuTimeArray.append(cpuTime)
    cpuTimePID = p.cpu_times()
    cpuTimePIDArray.append(cpuTimePIDArray)
    memVirtual = psutil.virtual_memory()
    memVirtualArray.append(memVirtual)
    memInfo = p.memory_info()
    memInfoArray.append(memInfo)
    diskUsage = psutil.disk_usage('../')
    diskUsageArray.append(diskUsage)
    print("CPU TIME PID ARRAY :")
    print(cpuTimeArray)
    return cpuTime, cpuTimePID, memVirtual, memInfo, diskUsage

def main(args):
    # Read config file passed as argument
    config = read_config_file(args)
    # Connection with client paho.mqtt api
    client = mqtt.Client()
    client.connect(config['hostIP'], config['port'], config['keepAlive'])
    # Declaring all metrics
    timeStart = perf_counter()
    declare_metrics()
    # Metrics about quantity of publications
    timeEnd = count_publications(10,client)

    timeTotal = timeEnd - timeStart
    client.publish('time',timeTotal)
    # End client mqtt
    
    print('\n\n####################################')
    client.disconnect()

if __name__ == "__main__":
    time.sleep(4)
    args = sys.argv 
    main(args)    