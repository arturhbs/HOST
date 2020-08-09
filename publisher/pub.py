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
   
    return dictFirstLastValues

# Take the average from values caught in metrics
def get_average_metrics_values():
    dictAverageMetrics = {'cpuTimeArray':None, 'cpuTimePIDArray':None,  'memVirtualArray':None,  'memInfoArray':None, 'diskUsageArray':None}
    dictAverageMetrics['cpuTimeArray'] = statistics.mean(cpuTimeArray)
    dictAverageMetrics['cpuTimePIDArray'] = statistics.mean(cpuTimePIDArray)
    dictAverageMetrics['memVirtualArray'] = statistics.mean(memVirtualArray)
    dictAverageMetrics['memInfoArray'] = statistics.mean(memInfoArray)
    dictAverageMetrics['diskUsageArray'] = statistics.mean(diskUsageArray)
    
    return dictAverageMetrics
    
# Get all metrics
def get_metrics():
    p = psutil.Process()
    # CPU time of all computer;
    # cpu_time = Return system CPU times as a named tuple. Every attribute represents the seconds the CPU has spent in the given mode;
    # [0]=user; [1]=system; [2]=idle;
    cpuTime = psutil.cpu_times()
    cpuTimeArray.append(cpuTime[0]+cpuTime[1]+cpuTime[2])

    # CPU time of the specific process;
    #user: time spent in user mode; system: time spent in kernel mode.
    # [0]=user; [1]=system;
    cpuTimePID = p.cpu_times()
    cpuTimePIDArray.append(cpuTimePID[0]+cpuTimePID[1])
    
    #memVirtual = append the virtual memory (not just the process like in memInfo, but all computer); 
    # [0]=total;[1]=available;[2]=percent;[3]=used;[4]=used;[5]=free;....
    memVirtual = psutil.virtual_memory()
    memVirtualArray.append(memVirtual[3])

    # rss: aka “Resident Set Size”, this is the non-swapped physical memory a process has used. On UNIX it matches “top“‘s RES column). On Windows this is an alias for wset field and it matches “Mem Usage” column of taskmgr.exe.
    # vms: aka “Virtual Memory Size”, this is the total amount of virtual memory used by the process. On UNIX it matches “top“‘s VIRT column. On Windows this is an alias for pagefile field and it matches “Mem Usage” “VM Size” column of taskmgr.exe.
    # [0]=rss; [1]=vms
    memInfo = p.memory_info()
    memInfoArray.append(memInfo[0]+ memInfo[1])
    
    # diskUsage = append the used disk value; 
    # [0] = total ; [1]=used; [2]=free,[4]=percent
    diskUsage = psutil.disk_usage('../')
    diskUsageArray.append(diskUsage[1])

# Send all metrics to subscribe
def send_metrics(lowerHighestMetrics, averageMetrics,client):

    # Send cpuTime metric
    client.publish('cpuTime_lowerMetric',lowerHighestMetrics['cpuTimeArray'][0])
    client.publish('cpuTime_highestMetric',lowerHighestMetrics['cpuTimeArray'][1])
    client.publish('cpuTime_averageMetric', averageMetrics['cpuTimeArray'])

    # Send cpuTimePID metric
    client.publish('cpuTimePID_lowerMetric',lowerHighestMetrics['cpuTimePIDArray'][0])
    client.publish('cpuTimePID_highestMetric',lowerHighestMetrics['cpuTimePIDArray'][1])
    client.publish('cpuTimePID_averageMetric', averageMetrics['cpuTimePIDArray'])

    # Send memVirtual metric
    client.publish('memVirtual_lowerMetric',lowerHighestMetrics['memVirtualArray'][0])
    client.publish('memVirtual_highestMetric',lowerHighestMetrics['memVirtualArray'][1])
    client.publish('memVirtual_averageMetric', averageMetrics['memVirtualArray'])

    # Send memInfo metric
    client.publish('memInfo_lowerMetric',lowerHighestMetrics['memInfoArray'][0])
    client.publish('memInfo_highestMetric',lowerHighestMetrics['memInfoArray'][1])
    client.publish('memInfo_averageMetric', averageMetrics['memInfoArray'])

    # Send diskUsage metric
    client.publish('diskUsage_lowerMetric',lowerHighestMetrics['diskUsageArray'][0])
    client.publish('diskUsage_highestMetric',lowerHighestMetrics['diskUsageArray'][1])
    client.publish('diskUsage_averageMetric', averageMetrics['diskUsageArray'])

# Sent value of quantity publications for the graph
def pipeline_metrics(quantity,client):
    count_message(quantity, client)
    lowerHighestMetrics = get_lowest_highest_metrics_values()
    averageMetrics = get_average_metrics_values()
    send_metrics(lowerHighestMetrics,averageMetrics,client)
    reset_constants_arrays()

# Run the main code with metrics chosen
def run_main_code(client):
    pipeline_metrics(8,client)
    pipeline_metrics(13,client)
    pipeline_metrics(21,client)
    pipeline_metrics(34,client)
    pipeline_metrics(55,client)

# main code
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
    run_main_code(client)

    # End client mqtt
    
    print('\n\nEND ####################################')
    client.disconnect()

if __name__ == "__main__":
    time.sleep(4)
    args = sys.argv 
    main(args)    