import sys
import json
import time
from time import process_time, perf_counter # if use perf_counter will calculate time with sleep time 
import paho.mqtt.client as mqtt
import pandas as pd
import psutil
import statistics
import matplotlib.pyplot as plt 
import seaborn as sns


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
    cpuTimeArray = []
    cpuTimePIDArray = []
    memVirtualArray = []
    memInfoArray = []
    diskUsageArray = []

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
    dictTotalMetrics['cpuTimeArray'] = cpuTimeArray
    dictTotalMetrics['cpuTimePIDArray'] = cpuTimePIDArray
    dictTotalMetrics['memVirtualArray'] = memVirtualArray
    dictTotalMetrics['memInfoArray'] = memInfoArray
    dictTotalMetrics['diskUsageArray'] = diskUsageArray
    
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
def send_metrics(averageMetrics,client):
    # Send cpuTime metric
    client.publish('cpuTime_averageMetric', averageMetrics['cpuTimeArray'])

    # Send cpuTimePID metric
    client.publish('cpuTimePID_averageMetric', averageMetrics['cpuTimePIDArray'])

    # Send memVirtual metric
    client.publish('memVirtual_averageMetric', averageMetrics['memVirtualArray'])

    # Send memInfo metric
    client.publish('memInfo_averageMetric', averageMetrics['memInfoArray'])

    # Send diskUsage metric
    client.publish('diskUsage_averageMetric', averageMetrics['diskUsageArray'])

# Sent value of quantity publications for the graph
def pipeline_metrics(quantity,client):
    count_message(quantity, client)
    # get values for axes X in graphs
    axX.append(quantity)
    averageMetrics = get_average_metrics_values()
    averageMetricsArrayGraph.append(averageMetrics)
    totalMetrics = get_all_metrics_values()
    totalMetricsArrayGraph.append(totalMetrics)
    send_metrics(averageMetrics,client)
    reset_constants_arrays()

# Run the main code with metrics chosen
def run_main_code(client):
    client.publish('reset_count','reset')
    pipeline_metrics(8,client)
    
    client.publish('reset_count','reset')
    pipeline_metrics(13,client)
    
    client.publish('reset_count','reset')
    pipeline_metrics(21,client)
    
    client.publish('reset_count','reset')
    pipeline_metrics(34,client)
    
    client.publish('reset_count','reset')
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

# Bar chart with average metric values
def bar_chart(yMinInterval,yMaxInterval,Y,X,nameImage):
    
    fig, ax = plt.subplots()
    rects = ax.bar(X, Y)
    ax.set_title('Time process per publisher')
    ax.set_ylabel('Time')    
    ax.set_xlabel('Quantity of topics')
    
    ax.set_ylim([yMinInterval*0.995,yMaxInterval*1.005])
    
    # Make some labels.
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.00001*height,
                '%.2f' % float(height),
                ha='center', va='bottom')

    plt.savefig('../data/barChart_'+nameImage+'.png')

# Line chart with average metric values
def line_chart(Y,X, nameImage):
    plt.clf()
    df = pd.DataFrame(list(zip(X , Y)), columns =['Fibonacci','value']) 
    df['Metric'] = 'value'
    sns.set(style = "whitegrid")
    snsLinePlot = sns.lineplot(x="Fibonacci", y="value",
                   markers=True,   style='Metric' ,data=df).set_title('Time process per publisher '+nameImage)

    snsLinePlot.figure.savefig('../data/lineChart_'+nameImage+'.png')
    plt.clf()

# Boxplot chart with average metric values
def boxPlot_chart(Y,X, nameImage):
    plt.clf()
    df = pd.DataFrame(list(zip(X , Y)), columns =['Fibonacci','Metric']) 
    df = df.explode('Metric')
    print("NAME IMAGE")
    print(nameImage)
    print("\n\ndf")
    print(df)
    sns.set(style = "whitegrid")
    snsBoxPlot = sns.boxplot(x="Fibonacci", y="Metric",data=df).set_title('Time process per publisher '+nameImage)
    snsBoxPlot.figure.savefig('../data/boxPlotChart_'+nameImage+'.png')
    plt.clf()

# Create all graphs necessary, calling functions of charts
def create_graphs():
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
    
    # Get all values for interval y axis
    sortArrMinMax = cpuTimeAverage
    sortArrMinMax.sort()
    minCpuTimeAvg = sortArrMinMax[0]
    maxCpuTimeAvg = sortArrMinMax[-1]
    sortArrMinMax = cpuTimePIDAverage
    sortArrMinMax.sort()
    minCpuTimePIDAvg = sortArrMinMax[0]
    maxCpuTimePIDAvg = sortArrMinMax[-1]
    sortArrMinMax = memVirtualAverage
    sortArrMinMax.sort()
    minMemVirtualAvg = sortArrMinMax[0]
    maxMemVirtualAvg = sortArrMinMax[-1]
    sortArrMinMax = memInfoAverage
    sortArrMinMax.sort()
    minMemInfoAvg = sortArrMinMax[0]
    maxMemInfoAvg = sortArrMinMax[-1]
    sortArrMinMax = diskUsageAverage
    sortArrMinMax.sort()
    minDiskUsageAvg = sortArrMinMax[0]
    maxDiskUsageAvg = sortArrMinMax[-1]
    
    # Call function to create a bar chart
    bar_chart(minCpuTimeAvg,maxCpuTimeAvg,cpuTimeAverage,axX, 'CpuTimeAverage')
    bar_chart(minCpuTimePIDAvg,maxCpuTimePIDAvg,cpuTimePIDAverage,axX, 'CpuTimePIDAverage')
    bar_chart(minMemVirtualAvg,maxMemVirtualAvg,memVirtualAverage,axX, 'MemVirtualAverage')
    bar_chart(minMemInfoAvg,maxMemInfoAvg,memInfoAverage,axX, 'MemInfoAverage')
    bar_chart(minDiskUsageAvg,maxDiskUsageAvg,diskUsageAverage,axX, 'DiskUsageAverage')

    
    # Call function to create a line chart
    line_chart(cpuTimeAverage,axX , 'CpuTimeAverage')
    line_chart(cpuTimePIDAverage,axX, 'CpuTimePIDAverage')
    line_chart(memVirtualAverage,axX, 'MemVirtualAverage')
    line_chart(memInfoAverage,axX, 'MemInfoAverage')
    line_chart(diskUsageAverage,axX, 'DiskUsageAverage')
    
    # Call function to create a box plot chart
    boxPlot_chart(cpuTimeTotalMetrics,axX , 'CpuTimeTotalMetrics')
    boxPlot_chart(cpuTimePIDTotalMetrics,axX, 'CpuTimePIDTotalMetrics')
    boxPlot_chart(memVirtualTotalMetrics,axX, 'MemVirtualTotalMetrics')
    boxPlot_chart(memInfoTotalMetrics,axX, 'MemInfoTotalMetrics')
    boxPlot_chart(diskUsageTotalMetrics,axX, 'DiskUsageTotalMetrics')

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

    # Create graph
    create_graphs()

    # End client mqtt
    
    print('\n\nEND ####################################')
    client.disconnect()

if __name__ == "__main__":
    time.sleep(4)
    args = sys.argv 
    main(args)    