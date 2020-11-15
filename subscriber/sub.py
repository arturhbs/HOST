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
dfMetricsProcesses = pd.DataFrame(columns=['PROCESS', 'QTYLOOP', 'METRIC', 'VALUE'])

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
    messageValue = float(messageSplit[0])
    qtyLoop = int(messageSplit[1])
    messageId = int(messageSplit[2])
    read_message(msg.topic,messageValue,qtyLoop,messageId)

# Identify message recieved
def read_message(msgMetric,msgValue,qtyLoop, msgId):
    # print('topic = ', topic)
    # print('msg index', qtyLoop)
    # print('msg id', msgId)

    # Get last dataframe's row position
    countRows =len(dfMetricsProcesses.index)

    dfMetricsProcesses.loc[countRows] = [msgId,qtyLoop,msgMetric,msgValue]

    # 125 get all metrics from 5 publisher processes
    if len(dfMetricsProcesses.index) == 125:
        create_graph(dfMetricsProcesses)
    #     create_graph()
   
def line_chart(df, nameImage):
    plt.clf()
    # sns.set(style = "whitegrid")
    # snsLinePlot = sns.lineplot(x="Fibonacci", y="value",
    #                markers=True,   style='Metric' ,data=df)

    # snsLinePlot.set_xlabel("QtyLoop")
    # snsLinePlot.set_ylabel(nameImage)
    # snsLinePlot.set_title('Average Time Process Per Publisher')
    sns.set(style = "whitegrid")
    snsLinePlot = sns.lineplot(x="QTYLOOP", y="VALUE",markers=["o", "o","o","o","o"], 
                                hue='PROCESS', style="PROCESS",legend="full",palette=["C0", "C1", "C2", "C3","C4"],data=df)

    snsLinePlot.set_xlabel("QtyLoop")
    snsLinePlot.set_ylabel(nameImage)
    snsLinePlot.set_title('Average Time Process Per Publisher')
    snsLinePlot.legend(loc='center right', bbox_to_anchor=(1.25, 0.5), ncol=1, title='Process')

    snsLinePlot.figure.savefig('../data/graphics/subscriber/lineChart_'+nameImage+'.png')
    plt.clf()

def transform_data_for_graph(dfMetricsProcesses):
    # Create csv file with all values
    dfMetricsProcesses.to_csv(r'../data/csv/subscriber/AllValuesDataframe.csv',index=False)
    
    # Splitting dataframe by metric name
    dfCpuTimeAvg = dfMetricsProcesses.loc[dfMetricsProcesses['METRIC'] == 'cpuTimeAvg' ]
    dfCpuTimePIDAvg = dfMetricsProcesses.loc[dfMetricsProcesses['METRIC'] == 'cpuTimeAvg' ]
    dfMemVirtualAvg = dfMetricsProcesses.loc[dfMetricsProcesses['METRIC'] == 'memVirtualAvg' ]
    dfMemInfoAvg = dfMetricsProcesses.loc[dfMetricsProcesses['METRIC'] == 'memInfoAvg' ]
    dfDiskUsageAvg = dfMetricsProcesses.loc[dfMetricsProcesses['METRIC'] == 'diskUsageAvg' ]
    
    # Writting dataframe's csv
    dfCpuTimeAvg.to_csv(r'../data/csv/subscriber/CpuTimeAvg.csv',index=False)
    dfCpuTimePIDAvg.to_csv(r'../data/csv/subscriber/CpuTimePIDAvg.csv',index=False)
    dfMemVirtualAvg.to_csv(r'../data/csv/subscriber/MemVirtualAvg.csv',index=False)
    dfMemInfoAvg.to_csv(r'../data/csv/subscriber/MemInfoAvg.csv',index=False)
    dfDiskUsageAvg.to_csv(r'../data/csv/subscriber/DiskUsageAvg.csv',index=False)

    return dfCpuTimeAvg, dfCpuTimePIDAvg, dfMemVirtualAvg, dfMemInfoAvg, dfDiskUsageAvg
    
def create_graph(dfMetricsProcesses):
    dfCpuTimeAvg, dfCpuTimePIDAvg, dfMemVirtualAvg, dfMemInfoAvg, dfDiskUsageAvg = transform_data_for_graph(dfMetricsProcesses)
       
    line_chart(dfCpuTimeAvg, 'cpuTime')
    line_chart( dfCpuTimePIDAvg, 'cpuTimePID')
    line_chart( dfMemVirtualAvg, 'memVirtual')
    line_chart( dfMemInfoAvg, 'memInfo')
    line_chart( dfDiskUsageAvg, 'diskUsage')

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