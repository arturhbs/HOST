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
import uuid
from pathlib import Path
import math  
import threading

# Send all metrics to subscribe
def send_metrics(client, dfAllMetricsAvg, idThread):

    # Run thread in background to look if the publish was effective
    client.loop_start()
    # Loop for all the five loop metrics
    for index, row in dfAllMetricsAvg.iterrows():
        waitForPublisher = client.publish('cpuTimeAvg', idThread +','+str(row['CountSteps'])+  ','+str(row['QtyTopic']) + ',' +str(row['CpuTimePID'])+  ',' +str(row['DiskUsage'])+  ','+str(row['MemInfo']), qos=1)
        waitForPublisher.wait_for_publish()
        
    # Send cpuTime metric

# Get all metrics
def get_metrics(qtyLoop,qtyTopics,dfAllMetrics):
    p = psutil.Process()
    # CPU time of all computer;
    # cpu_time = Return system CPU times as a named tuple. Every attribute represents the seconds the CPU has spent in the given mode;
    # [0]=user; [1]=system; [2]=idle;
    # cpuTime = psutil.cpu_times()
    # cpuTimeValue = cpuTime[0]+cpuTime[1]+cpuTime[2]

    # CPU time of the specific process;
    #user: time spent in user mode; system: time spent in kernel mode.
    # [0]=user; [1]=system;
    cpuTimePID = p.cpu_times()
    cpuTimePIDAValue = cpuTimePID[0]+cpuTimePID[1]
 
    # diskUsage = append the used disk value; 
    # [0] = total ; [1]=used; [2]=free,[3]=percent
    diskUsage = psutil.disk_usage('../')
    diskUsageValue = diskUsage[1]
    
    # rss: aka “Resident Set Size”, this is the non-swapped physical memory a process has used. On UNIX it matches “top“‘s RES column). On Windows this is an alias for wset field and it matches “Mem Usage” column of taskmgr.exe.
    # vms: aka “Virtual Memory Size”, this is the total amount of virtual memory used by the process. On UNIX it matches “top“‘s VIRT column. On Windows this is an alias for pagefile field and it matches “Mem Usage” “VM Size” column of taskmgr.exe.
    # [0]=rss; [1]=vms
    memInfo = p.memory_info()
    memInfoValue = memInfo[0]+ memInfo[1]
    
    #memVirtual = append the virtual memory (not just the process like in memInfo, but all computer); 
    # [0]=total;[1]=available;[2]=percent;[3]=used;[4]=used;[5]=free;....
    # memVirtual = psutil.virtual_memory()
    # memVirtualValue = memVirtual[3]

    countRows =len(dfAllMetrics.index)
    dfAllMetrics.loc[countRows] = [qtyTopics,qtyLoop,cpuTimePIDAValue,diskUsageValue,memInfoValue]

# Run the main code with metrics chosen
def run_main_code(client,dfAllMetrics):
    # Call pipeline fuction with fibonacci's number 
    # Parameters for pipeline_metrics: qty for loop; client mqtt, qty of topics to send
    fibonacciQtyTopics = [1,2,3,5,8,13,21,34,55]
    fibonacciCountSteps = [2,4,8,16,32]
    
    for j in fibonacciQtyTopics:
        for i in fibonacciCountSteps:
            count_message_n_topics(client,j,i,dfAllMetrics)

# main code
def count_message_n_topics(client, qtyTopics, qtyLoop,dfAllMetrics ):
    for i in range(qtyLoop) :
        get_metrics(qtyLoop,qtyTopics,dfAllMetrics)
        time.sleep(1)
        message=str(i)

        # simulate sening diferent topics
        for j in range(qtyTopics):
            randomTopic = str(uuid.uuid4())
            wait = client.publish(randomTopic,message)
            wait.wait_for_publish()
       
        get_metrics(qtyLoop,qtyTopics,dfAllMetrics)

# Line chart with average metric values
def line_chart(df, nameImage, idThread):

    plt.clf()
    
    # Create csv file with the dataframe name
    df.to_csv(r'../data/csv/publisher/'+idThread+'/linechart_'+ nameImage +'_' +  idThread +'.csv',index=False)

    # set color to each lineplot
    sns.set(style = "whitegrid")
    snsLinePlot = sns.lineplot(x="CountSteps", y=nameImage, 
                                 hue='QtyTopic', style="QtyTopic",legend="full",data=df)
   
    snsLinePlot.set_xlabel("CountSteps")
    snsLinePlot.set_ylabel(nameImage + 'Average')
    snsLinePlot.set_title('Average Time Process Per Publisher')
    snsLinePlot.legend(loc='center right', bbox_to_anchor=(1, 0.5), ncol=1, title='Topics')
    # sns.color_palette("Paired")

    snsLinePlot.figure.savefig('../data/graphics/publisher/'+idThread +'/lineChart_'+nameImage+'Average.png',bbox_inches='tight')
    plt.clf()

# Boxplot chart with average metric values
def boxPlot_chart(df,nameImage, idThread):
    plt.clf()
   
    # Create csv file with the dataframe name 
    df.to_csv(r'../data/csv/publisher/'+idThread+'/boxplot_'+ nameImage +'_' + idThread +'.csv',index=False)

    sns.set(style = "whitegrid")
    snsBoxPlot = sns.catplot(x="CountSteps", y=nameImage,col="QtyTopic",
                                data=df,  kind="box", height=4, aspect=.7)
    snsBoxPlot.set(ylabel = nameImage+'TotalMetrics')
    snsBoxPlot.savefig('../data/graphics/publisher/'+idThread +'/boxPlotChart_'+nameImage+'TotalMetrics.png')
    plt.clf()

# Create all graphs necessary, calling functions of charts and inside that functions are the csv creation due to the complete dataframe of each graph
def create_graphs_csv(idThread,dfAllMetrics,dfAllMetricsAvg):
  
    # Create directory with the id of the publisher
    Path("../data/csv/publisher/"+idThread).mkdir(parents=True, exist_ok=True)
    Path("../data/graphics/publisher/"+idThread).mkdir(parents=True, exist_ok=True)

    # Crete csv with all metrics and average of all metrics making a grupby of Topics
    dfAllMetrics.to_csv(r'../data/csv/publisher/'+idThread+'/AllMetrics.csv',index=False)
    dfAllMetricsAvg.to_csv(r'../data/csv/publisher/'+idThread+'/AllMetricsAvg.csv',index=False)

    # dfCpuTime = dfAllMetrics[['QtyTopic','CountSteps','CpuTime']]
    dfCpuTimePID = dfAllMetrics[['QtyTopic','CountSteps','CpuTimePID']]
    dfDiskUsage = dfAllMetrics[['QtyTopic','CountSteps','DiskUsage']]
    dfMemInfo = dfAllMetrics[['QtyTopic','CountSteps','MemInfo']]
    # dfMemVirtual = dfAllMetrics[['QtyTopic','CountSteps','MemVirtual']]

    # Boxplot chart creation with all values ​​obtained
    # boxPlot_chart(dfCpuTime,'CpuTime', idThread)
    boxPlot_chart(dfCpuTimePID,'CpuTimePID', idThread)
    boxPlot_chart(dfDiskUsage,'DiskUsage', idThread)
    boxPlot_chart(dfMemInfo,'MemInfo', idThread)
    # boxPlot_chart(dfMemVirtual,'MemVirtual', idThread)

    # Crete csv with the average of all metrics

    # dfCpuTimeAvg = dfAllMetricsAvg[['CountSteps','QtyTopic','CpuTime']]
    dfCpuTimePIDAvg = dfAllMetricsAvg[['CountSteps','QtyTopic','CpuTimePID']]
    dfDiskUsageAvg = dfAllMetricsAvg[['CountSteps','QtyTopic','DiskUsage']]
    dfMemInfoAvg = dfAllMetricsAvg[['CountSteps','QtyTopic','MemInfo']]
    # dfMemVirtualAvg = dfAllMetricsAvg[['CountSteps','QtyTopic','MemVirtual']]
 

    # # Line chart creation with the average of all values ​​obtained
    # line_chart(dfCpuTimeAvg,'CpuTime', idThread)
    line_chart(dfCpuTimePIDAvg,'CpuTimePID', idThread)
    line_chart(dfDiskUsageAvg,'DiskUsage', idThread)
    line_chart(dfMemInfoAvg,'MemInfo', idThread)
    # line_chart(dfMemVirtualAvg,'MemVirtual', idThread)
    
    # # Call function to create a box plot chart

# Read config file that user can modify 
def read_config_file(args):
    with open(args[1], 'r') as file:
        config = json.load(file)
    return config['publisher']

def main(args):
    # Get thread id for name process of the publisher
    print("**** THREAD ID *****")
    idThread = threading.get_ident()
    idThread = str(idThread)
    print(idThread)
    # Read config file passed as argument
    config = read_config_file(args)
    
    # Connection with client paho.mqtt api
    client = mqtt.Client()
    client.connect(config['hostIP'], config['port'], config['keepAlive'])

    # Creating a dataframe to get all metrics    
    dfAllMetrics = pd.DataFrame(columns=['QtyTopic','CountSteps', 'CpuTimePID', 'DiskUsage', 'MemInfo'])

    # Metrics about quantity of publications
    run_main_code(client,dfAllMetrics)

    # Creating Avg by quantity of topics
    dfAllMetricsAvg = dfAllMetrics.groupby(['QtyTopic','CountSteps'],as_index=False).mean()
    
    # Create graphs and csv with metrics
    create_graphs_csv(idThread,dfAllMetrics,dfAllMetricsAvg)

    # Send metrics to subscriber
    send_metrics(client, dfAllMetricsAvg, idThread)
    
    # End client mqtt
    client.disconnect()
    print("\n####### Finalizou ######\nProcess id: ", idThread)

if __name__ == "__main__":
    # See total duration of the process
    timeStart = perf_counter()
    time.sleep(4)
    args = sys.argv 
    main(args)    
    timeEnd = perf_counter()
    timeTotal = timeEnd - timeStart
    print("Process duration: ", timeTotal/60," minutes")