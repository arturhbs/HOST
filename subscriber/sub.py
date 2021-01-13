import sys
import time
import json
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np
import statistics
import pandas as pd
import seaborn as sns


# Dataframe to get all data (function = read_message)
dfMetricsProcesses = pd.DataFrame(columns=['Process', 'CountSteps', 'QtyTopic', 'CpuTimePID','DiskUsage','MemInfo','ProcessNumber'])

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#") # Show every message
    client.subscribe([('cpuTimeAvg',0),('cpuTimePIDAvg',0),('memVirtualAvg',0),('memInfoAvg',0),('diskUsageAvg',0)],qos=1)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    message = msg.payload.decode('UTF-8')
    messageSplit = message.split(sep=',')
    processId = int(messageSplit[0])
    qtyTopic = float(messageSplit[1])
    qtyLoop = float(messageSplit[2])
    cpuTimePID = float(messageSplit[3])
    diskUsage = float(messageSplit[4])
    memInfo = float(messageSplit[5])
    read_message(processId,qtyTopic,qtyLoop,cpuTimePID,diskUsage,memInfo)

# Identify message recieved
def read_message(processId,qtyTopic,qtyLoop,cpuTimePID,diskUsage,memInfo):

    # Get last dataframe's row position
    countRows =len(dfMetricsProcesses.index)
    dfMetricsProcesses.loc[countRows] = [processId,qtyTopic,qtyLoop,cpuTimePID,diskUsage,memInfo,0]
    
    # Verify how many process are executing at same time
    # countRows plus one because dataframe starts with 0
    # if countRows < 360:
    #     dfMetricsProcesses.loc[countRows]['ProcessNumber'] = 8
    # elif countRows < 585:
    #     dfMetricsProcesses.loc[countRows]['ProcessNumber'] = 5
    # elif countRows < 720:
    #     dfMetricsProcesses.loc[countRows]['ProcessNumber'] = 3
    # elif countRows < 810:
    #     dfMetricsProcesses.loc[countRows]['ProcessNumber'] = 2
    # elif countRows < 855:
    #     dfMetricsProcesses.loc[countRows]['ProcessNumber'] = 1


    # print(dfMetricsProcesses)    
    print(countRows)
    if len(dfMetricsProcesses.index) == 225 :
        create_graph_csv(dfMetricsProcesses)
    

    # 125 get all metrics from 5 publisher processes running at same time
    # if len(dfMetricsProcesses.index) == 125:
    #     old_create_graph_csv(dfMetricsProcesses)

# Create line chart   
def line_chart(df, nameImage):
    plt.clf()
    sns.set(style = "whitegrid")
    snsLinePlot = sns.lineplot(x="CountSteps", y=nameImage, 
                                hue='QtyTopic', style="QtyTopic",legend="full",data=df)

    snsLinePlot.set_xlabel("CountSteps")
    snsLinePlot.set_ylabel(nameImage)
    snsLinePlot.set_title('Average Time Process Per Publisher')
    snsLinePlot.legend(loc='center right', bbox_to_anchor=(1.25, 0.5), ncol=1, title='Process')

    snsLinePlot.figure.savefig('../data/graphics/subscriber/lineChart_'+nameImage+'.png')
    plt.clf()

def transform_data_for_graph(dfMetricsProcesses):
    # Average of all values pivoting qtyloop as  the main metric for each process
    dfMetricsProcessesAvg = dfMetricsProcesses.groupby(['CountSteps','QtyTopic'],as_index=False).mean()
        
    # Create csv file with all values
    dfMetricsProcessesAvg.to_csv(r'../data/csv/subscriber/MetricsProcessesAvg.csv',index=False)
    dfMetricsProcesses.to_csv(r'../data/csv/subscriber/MetricsProcesses.csv',index=False)
    
    # Splitting dataframe by metric name
    # dfCpuTimeAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','CpuTime']]
    dfCpuTimePIDAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','CpuTimePID']]
    dfDiskUsageAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','DiskUsage']]
    dfMemInfoAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','MemInfo']]
    # dfMemVirtualAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','MemVirtual']]
    
    # Writting dataframe's csv
    # dfCpuTimeAvg.to_csv(r'../data/csv/subscriber/CpuTimeAvg.csv',index=False)
    dfCpuTimePIDAvg.to_csv(r'../data/csv/subscriber/CpuTimePIDAvg.csv',index=False)
    dfDiskUsageAvg.to_csv(r'../data/csv/subscriber/DiskUsageAvg.csv',index=False)
    dfMemInfoAvg.to_csv(r'../data/csv/subscriber/MemInfoAvg.csv',index=False)
    # dfMemVirtualAvg.to_csv(r'../data/csv/subscriber/MemVirtualAvg.csv',index=False)
  
    return dfMetricsProcessesAvg,  dfCpuTimePIDAvg,  dfMemInfoAvg, dfDiskUsageAvg
    
def create_graph_csv(dfMetricsProcesses):
    dfMetricsProcessesAvg,  dfCpuTimePIDAvg,  dfMemInfoAvg, dfDiskUsageAvg = transform_data_for_graph(dfMetricsProcesses)

    # line_chart(dfCpuTimeAvg, 'CpuTime')
    line_chart( dfCpuTimePIDAvg, 'CpuTimePID')
    line_chart( dfDiskUsageAvg, 'DiskUsage')
    line_chart( dfMemInfoAvg, 'MemInfo')
    # line_chart( dfMemVirtualAvg, 'MemVirtual')

def new_line_chart(df, nameImage):
    plt.clf()
    sns.set(style = "whitegrid")
    snsLinePlot = sns.lineplot(x="CountSteps", y=nameImage,markers=["o", "o","o","o","o"], 
                                hue='ProcessNumber', style="ProcessNumber",legend="full",palette=["C0", "C1", "C2", "C3","C4"],data=df)

    snsLinePlot.set_xlabel("CountSteps")
    snsLinePlot.set_ylabel(nameImage)
    snsLinePlot.set_title('Average Time Process Per Publisher')
    snsLinePlot.legend(loc='center right', bbox_to_anchor=(1.25, 0.5), ncol=1, title='Process')

    snsLinePlot.figure.savefig('../data/graphics/subscriber/lineChart_'+nameImage+'.png')
    plt.clf()

def new_transform_data_for_graph(dfMetricsProcesses):
    # Average of all values pivoting qtyloop as  the main metric for each process
    dfMetricsProcessesAvg = dfMetricsProcesses.groupby(['CountSteps','ProcessNumber'],as_index=False).mean()
        
    # Create csv file with all values
    dfMetricsProcessesAvg.to_csv(r'../data/csv/subscriber/MetricsProcessesAvg.csv',index=False)
    dfMetricsProcesses.to_csv(r'../data/csv/subscriber/MetricsProcesses.csv',index=False)
    
    # Splitting dataframe by metric name
    # dfCpuTimeAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','CpuTime']]
    dfCpuTimePIDAvg = dfMetricsProcessesAvg[['CountSteps','ProcessNumber','CpuTimePID']]
    dfDiskUsageAvg = dfMetricsProcessesAvg[['CountSteps','ProcessNumber','DiskUsage']]
    dfMemInfoAvg = dfMetricsProcessesAvg[['CountSteps','ProcessNumber','MemInfo']]
    # dfMemVirtualAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','MemVirtual']]
    
    # # Writting dataframe's csv
    # dfCpuTimeAvg.to_csv(r'../data/csv/subscriber/CpuTimeAvg.csv',index=False)
    dfCpuTimePIDAvg.to_csv(r'../data/csv/subscriber/CpuTimePIDAvg.csv',index=False)
    dfDiskUsageAvg.to_csv(r'../data/csv/subscriber/DiskUsageAvg.csv',index=False)
    dfMemInfoAvg.to_csv(r'../data/csv/subscriber/MemInfoAvg.csv',index=False)
    # dfMemVirtualAvg.to_csv(r'../data/csv/subscriber/MemVirtualAvg.csv',index=False)
  
    return dfMetricsProcessesAvg,  dfCpuTimePIDAvg, dfMemInfoAvg, dfDiskUsageAvg
    
def new_create_graph_csv(dfMetricsProcesses):
    dfMetricsProcessesAvg,  dfCpuTimePIDAvg,  dfMemInfoAvg, dfDiskUsageAvg = transform_data_for_graph(dfMetricsProcesses)
    # line_chart(dfCpuTimeAvg, 'CpuTime')
    line_chart( dfCpuTimePIDAvg, 'CpuTimePID')
    line_chart( dfDiskUsageAvg, 'DiskUsage')
    line_chart( dfMemInfoAvg, 'MemInfo')
    print("\nACABOUU")
    # line_chart( dfMemVirtualAvg, 'MemVirtual')


# Read config file that are argurments to modify some parts of the code by the user
def Read_Config_File(args):
    with open(args[1], 'r') as file:
        config = json.load(file)
    return config['subscriber']

def main(args):
    # Read config file passed as argument
    config = Read_Config_File(args)
    # Connection with client paho.mqtt api  
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config['hostIP'], config['port'], config['keepAlive'])
    client.loop_forever()

if __name__ == "__main__":
    args = sys.argv 
    main(args)