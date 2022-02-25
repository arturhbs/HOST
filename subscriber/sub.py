import sys
import time
import json
import paho.mqtt.client as mqtt # version 1.6.1
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
    if len(dfMetricsProcesses.index) == 225 :
        create_graph_csv(dfMetricsProcesses)
    
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
    dfCpuTimePIDAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','CpuTimePID']]
    dfDiskUsageAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','DiskUsage']]
    dfMemInfoAvg = dfMetricsProcessesAvg[['CountSteps','QtyTopic','MemInfo']]
    
    # Writting dataframe's csv
    dfCpuTimePIDAvg.to_csv(r'../data/csv/subscriber/CpuTimePIDAvg.csv',index=False)
    dfDiskUsageAvg.to_csv(r'../data/csv/subscriber/DiskUsageAvg.csv',index=False)
    dfMemInfoAvg.to_csv(r'../data/csv/subscriber/MemInfoAvg.csv',index=False)
  
    return dfMetricsProcessesAvg,  dfCpuTimePIDAvg,  dfMemInfoAvg, dfDiskUsageAvg
    
def create_graph_csv(dfMetricsProcesses):
    dfMetricsProcessesAvg,  dfCpuTimePIDAvg,  dfMemInfoAvg, dfDiskUsageAvg = transform_data_for_graph(dfMetricsProcesses)

    line_chart( dfCpuTimePIDAvg, 'CpuTimePID')
    line_chart( dfDiskUsageAvg, 'DiskUsage')
    line_chart( dfMemInfoAvg, 'MemInfo')
    
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