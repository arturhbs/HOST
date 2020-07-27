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

def reset_constants_arrays():
    cpuTimeArray = []
    cpuTimePIDArray = []
    memVirtualArray = []
    memInfoArray = []
    diskUsageArray = []
# take the first and last value to see the range of metrics returned
def first_last_value_metric():
    dictFirstLastValues = {'cpuTimeArray':[] 'cpuTimePIDArray':[]  'memVirtualArray':[]  'memInfoArray':[] 'diskUsageArray':[]}
    cpuTimeArray.sort()
    dictFirstLastValues['cpuTimeArray'].append(cpuTimeArray[0])
    dictFirstLastValues['cpuTimeArray'].append(cpuTimeArray[-1])
    cpuTimePIDArray.sort()
    dictFirstLastValues['cpuTimePIDArray'].append(cpuTimePIDArray[0])
    dictFirstLastValues['cpuTimePIDArray'].append(cpuTimePIDArray[-1])
    memVirtualArray.sort()
    dictFirstLastValues['memVirtualArray'].append(memVirtualArray[0])
    dictFirstLastValues['memVirtualArray'].append(memVirtualArray[-1])
    memInfoArray.sort()
    dictFirstLastValues['memInfoArray'].append(memInfoArray[0])
    dictFirstLastValues['memInfoArray'].append(memInfoArray[-1])
    diskUsageArray.sort()
    dictFirstLastValues['diskUsageArray'].append(diskUsageArray[0])
    dictFirstLastValues['diskUsageArray'].append(diskUsageArray[-1])

    return dictFirstLastValues
# Take the average from values caught in metrics
def average_metrics():

# Sent value of quantity publications for the graph
def count_publications(client):
    count_message(8, client)
    reset_constants_arrays()
    count_message(13,client)
    reset_constants_arrays()
    count_message(21,client)
    reset_constants_arrays()
    count_message(34,client)
    reset_constants_arrays()
    count_message(55,client)

def count_message(quantity, client):
    i=0
    timeStart = perf_counter()
    while True:
        declare_metrics()
        time.sleep(1)
        i+=1
        message=str(i)
        if i <=quantity:
            client.publish('count',message)
        else:
            break
    first, last = first_last_value_metric()
    average_metrics()        
    timeEnd = perf_counter()
    timeTotal = timeEnd - timeStart
    client.publish('time',timeTotal)

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

def main(args):
    # Read config file passed as argument
    config = read_config_file(args)
    # Connection with client paho.mqtt api
    client = mqtt.Client()
    client.connect(config['hostIP'], config['port'], config['keepAlive'])
    # Declaring all metrics
    declare_metrics()
    # Metrics about quantity of publications
    count_publications(client)

    # End client mqtt
    
    print('\n\n####################################')
    client.disconnect()

if __name__ == "__main__":
    time.sleep(4)
    args = sys.argv 
    main(args)    