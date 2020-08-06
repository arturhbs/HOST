import sys
import json
import time
from time import process_time, perf_counter # if use perf_counter will calculate time with sleep time 
import paho.mqtt.client as mqtt
import psutil
import statistics 

cpuTimeArray = []
cpuTimePIDArray = []
memVirtualArray = []
memInfoArray = []
diskUsageArray = []

# Initialize constants
def reset_constants_arrays():
    cpuTimeArray = []
    cpuTimePIDArray = []
    memVirtualArray = []
    memInfoArray = []
    diskUsageArray = []

# take the lowest and highest value to see the range of metrics returned
def get_lowest_highest_metrics_values():
    dictFirstLastValues = {'cpuTimeArray':[], 'cpuTimePIDArray':[],  'memVirtualArray':[],  'memInfoArray':[], 'diskUsageArray':[]}
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

    print('\nDICT first and last METRICS :')
    print(dictFirstLastValues['cpuTimeArray'])
    print('\nDICT first and last METRICS : ')
    print(dictFirstLastValues['cpuTimePIDArray'])
    print('\nDICT first and last METRICS : ')
    print(dictFirstLastValues['memVirtualArray'])
    print('\nDICT first and last METRICS : ')
    print(dictFirstLastValues['memInfoArray'])
    print('\nDICT first and last METRICS : ')
    print(dictFirstLastValues['diskUsageArray'])
   
    return dictFirstLastValues

# Take the average from values caught in metrics
def get_average_metrics_values():
    dictAverageMetrics = {'cpuTimeArray':None, 'cpuTimePIDArray':None,  'memVirtualArray':None,  'memInfoArray':None, 'diskUsageArray':None}
    dictAverageMetrics['cpuTimeArray'] = statistics.mean(cpuTimeArray)
    # dictAverageMetrics['cpuTimePIDArray'] = statistics.mean(cpuTimePIDArray)
    dictAverageMetrics['memVirtualArray'] = statistics.mean(memVirtualArray)
    # dictAverageMetrics['memInfoArray'] = statistics.mean(memInfoArray)
    dictAverageMetrics['diskUsageArray'] = statistics.mean(diskUsageArray)
    print('\n\nDICT AVERAGE METRICS : ')
    print(dictAverageMetrics)
    return dictAverageMetrics
    
# Sent value of quantity publications for the graph
def count_publications(client):
    count_message(8, client)
    get_lowest_highest_metrics_values()
    get_average_metrics_values()
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
        get_metrics()
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

# Get all metrics
def get_metrics():
    p = psutil.Process()
    #cpu_time = Return system CPU times as a named tuple. Every attribute represents the seconds the CPU has spent in the given mode;
    # [0]=user; [1]=system; [2]=idle;
    cpuTime = psutil.cpu_times()
    cpuTimeArray.append(cpuTime[0]+cpuTime[1]+cpuTime[2])

    cpuTimePID = p.cpu_times()
    cpuTimePIDArray.append(cpuTimePIDArray)
    
    #memVirtual = append the virtual memory; 
    # [0]=total;[1]=available;[2]=percent;[3]=used;[4]=used;[5]=free;....
    memVirtual = psutil.virtual_memory()
    memVirtualArray.append(memVirtual[3])

    memInfo = p.memory_info()
    memInfoArray.append(memInfo)
    # diskUsage = append the used disk value; 
    # [0] = total ; [1]=used; [2]=free,[4]=percent
    diskUsage = psutil.disk_usage('../')
    diskUsageArray.append(diskUsage[1])

# Read config file that user can modify 
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
    # Declaring all metrics
    get_metrics()
    # Metrics about quantity of publications
    count_publications(client)

    # End client mqtt
    
    print('\n\n####################################')
    client.disconnect()

if __name__ == "__main__":
    time.sleep(4)
    args = sys.argv 
    main(args)    