import sys
import os
import json
import time
from time import process_time, perf_counter # if use perf_counter will calculate time with sleep time 
import paho.mqtt.client as mqtt
import pandas as pd
import psutil
import statistics
import matplotlib.pyplot as plt 
import seaborn as sns
from pathlib import Path

cpuTimeArray = []
cpuTimePIDArray = []
memVirtualArray = []
memInfoArray = []
diskUsageArray = []
averageMetricsArrayGraph = []
totalMetricsArrayGraph = []
axX = []


# Initialize constants
def reset_constants_arrays():
    cpuTimeArray.clear()
    cpuTimePIDArray.clear()
    memVirtualArray.clear()
    memInfoArray.clear()
    diskUsageArray.clear()

# Take the average from values caught in metrics
def get_average_metrics_values():
    dictAverageMetrics = {'cpuTimeArray':None, 'cpuTimePIDArray':None,  'memVirtualArray':None,  'memInfoArray':None, 'diskUsageArray':None}
    dictAverageMetrics['cpuTimeArray'] = statistics.mean(cpuTimeArray)
    dictAverageMetrics['cpuTimePIDArray'] = statistics.mean(cpuTimePIDArray)
    dictAverageMetrics['memVirtualArray'] = statistics.mean(memVirtualArray)
    dictAverageMetrics['memInfoArray'] = statistics.mean(memInfoArray)
    dictAverageMetrics['diskUsageArray'] = statistics.mean(diskUsageArray)
    
    return dictAverageMetrics

# Get all values caught in metrics
def get_all_metrics_values():
    
    dictTotalMetrics = {'cpuTimeArray':None, 'cpuTimePIDArray':None,  'memVirtualArray':None,  'memInfoArray':None, 'diskUsageArray':None}
    dictTotalMetrics['cpuTimeArray'] = cpuTimeArray[:]
    dictTotalMetrics['cpuTimePIDArray'] = cpuTimePIDArray[:]
    dictTotalMetrics['memVirtualArray'] = memVirtualArray[:]
    dictTotalMetrics['memInfoArray'] = memInfoArray[:]
    dictTotalMetrics['diskUsageArray'] = diskUsageArray[:]

    return dictTotalMetrics

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
def send_metrics(client):
    # print(averageMetricsArrayGraph)
    client.loop_start()
    for i in range(5):
        try:
            # Send cpuTime metric
            waitForPublisher = client.publish('cpuTimeAvg', str(averageMetricsArrayGraph[i]['cpuTimeArray']) + ',' + str(i), qos=1)
            waitForPublisher.wait_for_publish()
           
            # Send cpuTimePID metric
            waitForPublisher = client.publish('cpuTimePIDAvg', str(averageMetricsArrayGraph[i]['cpuTimePIDArray']) + ',' + str(i), qos=1,retain=False) 
            waitForPublisher.wait_for_publish()

            # Send memVirtual metric
            waitForPublisher = client.publish('memVirtualAvg', str(averageMetricsArrayGraph[i]['memVirtualArray']) + ',' + str(i), qos=1)
            waitForPublisher.wait_for_publish()

            # Send memInfo metric
            waitForPublisher = client.publish('memInfoAvg', str(averageMetricsArrayGraph[i]['memInfoArray']) + ',' + str(i), qos=1)
            waitForPublisher.wait_for_publish()

            # Send diskUsage metric
            waitForPublisher = client.publish('diskUsageAvg', str(averageMetricsArrayGraph[i]['diskUsageArray']) + ',' + str(i), qos=1)
            waitForPublisher.wait_for_publish()

        except ErrorSendingMessage:
            print("Value i that got error was: ", i)

# Sent value of quantity publications for the graph
def pipeline_metrics(quantity,client):
    count_message(quantity, client)
    # get values for axes X in graphs
    axX.append(quantity)
    averageMetrics = get_average_metrics_values()
    averageMetricsArrayGraph.append(averageMetrics)
    totalMetrics = get_all_metrics_values()
    totalMetricsArrayGraph.append(totalMetrics)
    reset_constants_arrays()

# Run the main code with metrics chosen
def run_main_code(client):
    # Call pipeline fuction with fibonacci's number
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

# Line chart with average metric values
def line_chart(Y,X, nameImage, id_pub):

    plt.clf()
    df = pd.DataFrame(list(zip(X , Y)), columns =['Fibonacci','value']) 
    df['Metric'] = 'value'
    sns.set(style = "whitegrid")
    snsLinePlot = sns.lineplot(x="Fibonacci", y="value",
                   markers=True,   style='Metric' ,data=df).set_title('Time process per publisher '+nameImage)

    snsLinePlot.figure.savefig('../data/publisher/'+id_pub +'/lineChart_'+nameImage+'.png')
    plt.clf()

# Boxplot chart with average metric values
def boxPlot_chart(Y,X, nameImage, id_pub):
    plt.clf()

    df = pd.DataFrame(list(zip(X , Y)), columns =['Fibonacci','Metric']) 
    df = df.explode('Metric')

    sns.set(style = "whitegrid")
    snsBoxPlot = sns.boxplot(x="Fibonacci", y="Metric",data=df).set_title('Time process per publisher '+nameImage)
    # snsBoxPlot = sns.boxplot(x=df["Metric"]).set_title('Time process per publisher '+nameImage)
    snsBoxPlot.figure.savefig('../data/publisher/'+id_pub +'/boxPlotChart_'+nameImage+'.png')
    plt.clf()

# Create all graphs necessary, calling functions of charts
def create_graphs(id_pub):
    cpuTimeAverage = []
    cpuTimePIDAverage = []
    memVirtualAverage = []
    memInfoAverage = []
    diskUsageAverage = []
    cpuTimeTotalMetrics = []
    cpuTimePIDTotalMetrics = []
    memVirtualTotalMetrics = []
    memInfoTotalMetrics = []
    diskUsageTotalMetrics = []
   
    for i in averageMetricsArrayGraph:
        cpuTimeAverage.append(i['cpuTimeArray'])
        cpuTimePIDAverage.append(i['cpuTimePIDArray'])
        memVirtualAverage.append(i['memVirtualArray'])
        memInfoAverage.append(i['memInfoArray'])
        diskUsageAverage.append(i['diskUsageArray'])
    
    for i in totalMetricsArrayGraph:
        cpuTimeTotalMetrics.append(i['cpuTimeArray'])
        cpuTimePIDTotalMetrics.append(i['cpuTimePIDArray'])
        memVirtualTotalMetrics.append(i['memVirtualArray'])
        memInfoTotalMetrics.append(i['memInfoArray'])
        diskUsageTotalMetrics.append(i['diskUsageArray'])
    
    # Create directory with the id of the publisher
    Path("../data/publisher/"+id_pub).mkdir(parents=True, exist_ok=True)
    
    # Call function to create a line chart
    line_chart(cpuTimeAverage,axX , 'CpuTimeAverage', id_pub)
    line_chart(cpuTimePIDAverage,axX, 'CpuTimePIDAverage',id_pub)
    line_chart(memVirtualAverage,axX, 'MemVirtualAverage', id_pub)
    line_chart(memInfoAverage,axX, 'MemInfoAverage', id_pub)
    line_chart(diskUsageAverage,axX, 'DiskUsageAverage', id_pub)
    
    # Call function to create a box plot chart
    boxPlot_chart(cpuTimeTotalMetrics,axX , 'CpuTimeTotalMetrics', id_pub)
    boxPlot_chart(cpuTimePIDTotalMetrics,axX, 'CpuTimePIDTotalMetrics', id_pub)
    boxPlot_chart(memVirtualTotalMetrics,axX, 'MemVirtualTotalMetrics', id_pub)
    boxPlot_chart(memInfoTotalMetrics,axX, 'MemInfoTotalMetrics', id_pub)
    boxPlot_chart(diskUsageTotalMetrics,axX, 'DiskUsageTotalMetrics', id_pub)

# Read config file that user can modify 
def read_config_file(args):
    with open(args[1], 'r') as file:
        config = json.load(file)
    return config['publisher']

def main(args):
    # Get id for publisher
    print("**** ID *****")
    print(os.getpid())
    id_pub = str(os.getpid())
    
    # Read config file passed as argument
    config = read_config_file(args)
    
    # Connection with client paho.mqtt api
    client = mqtt.Client()
    client.connect(config['hostIP'], config['port'], config['keepAlive'])
    
    # Declaring all metrics
    get_metrics()

    # Metrics about quantity of publicationsX
    run_main_code(client)

    # Create graph
    create_graphs(id_pub)

    # Send metrics to subscriber
    send_metrics(client)
    
    print("####### Vai desconectar ######")
    # End client mqtt
    client.disconnect()

if __name__ == "__main__":
    time.sleep(4)
    args = sys.argv 
    main(args)    