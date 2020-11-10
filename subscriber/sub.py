import sys
import time
import json
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np
import statistics
import pandas as pd
import seaborn as sns



metricAvg = {'cpuTimeAvg_ax0':[],'cpuTimeAvg_ax1':[],'cpuTimeAvg_ax2':[],'cpuTimeAvg_ax3':[],'cpuTimeAvg_ax4':[],
            'cpuTimePIDAvg_ax0':[] ,'cpuTimePIDAvg_ax1':[],'cpuTimePIDAvg_ax2':[],'cpuTimePIDAvg_ax3':[],'cpuTimePIDAvg_ax4':[],
            'memVirtualAvg_ax0':[],'memVirtualAvg_ax1':[],'memVirtualAvg_ax2':[],'memVirtualAvg_ax3':[],'memVirtualAvg_ax4':[] ,
            'memInfoAvg_ax0':[],'memInfoAvg_ax1':[],'memInfoAvg_ax2':[],'memInfoAvg_ax3':[],'memInfoAvg_ax4':[],
            'diskUsageAvg_ax0':[],'diskUsageAvg_ax1':[],'diskUsageAvg_ax2':[],'diskUsageAvg_ax3':[],'diskUsageAvg_ax4':[] }


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
    messageMetric = float(messageSplit[0])
    messageIndex = int(messageSplit[1])
    messageId = int(messageSplit[2])
    read_message(msg.topic,messageMetric,messageIndex,messageId)

# Identify message recieved
def read_message(topic,msgMetric,msgIndex, msgId):
    print('topic = ', topic)
    print('msg index', msgIndex)
    print('msg id', msgId)
    
    if topic == 'cpuTimeAvg':
        # Get metric for 1 topics
        if msgIndex == 0:
            metricAvg['cpuTimeAvg_ax0'].append(msgMetric)
            
        # Get metric for 2 topics
        elif msgIndex == 1:   
            metricAvg['cpuTimeAvg_ax1'].append(msgMetric)

        # Get metric for 3 topics
        elif msgIndex == 2:   
            metricAvg['cpuTimeAvg_ax2'].append(msgMetric)
            
        # Get metric for 5 topics
        elif msgIndex == 3:   
            metricAvg['cpuTimeAvg_ax3'].append(msgMetric)
            
        # Get metric for 8 topics
        elif msgIndex == 4:   
            metricAvg['cpuTimeAvg_ax4'].append(msgMetric)
            
    elif topic == 'cpuTimePIDAvg':
        # Get metric for 1 topics
        if msgIndex == 0:
            metricAvg['cpuTimePIDAvg_ax0'].append(msgMetric)
            
        # Get metric for 2 topics
        elif msgIndex == 1:   
            metricAvg['cpuTimePIDAvg_ax1'].append(msgMetric)

        # Get metric for 3 topics
        elif msgIndex == 2:   
            metricAvg['cpuTimePIDAvg_ax2'].append(msgMetric)
            
        # Get metric for 5 topics
        elif msgIndex == 3:   
            metricAvg['cpuTimePIDAvg_ax3'].append(msgMetric)

        # Get metric for 8 topics
        elif msgIndex == 4:   
            metricAvg['cpuTimePIDAvg_ax4'].append(msgMetric)
            
    elif topic == 'memVirtualAvg':
        if msgIndex == 0:
            metricAvg['memVirtualAvg_ax0'].append(msgMetric)
            
        elif msgIndex == 1:   
            metricAvg['memVirtualAvg_ax1'].append(msgMetric)
            
        elif msgIndex == 2:   
            metricAvg['memVirtualAvg_ax2'].append(msgMetric)
            
        elif msgIndex == 3:   
            metricAvg['memVirtualAvg_ax3'].append(msgMetric)
            
        elif msgIndex == 4:   
            metricAvg['memVirtualAvg_ax4'].append(msgMetric)
            
    elif topic == 'memInfoAvg':
        if msgIndex == 0:
            metricAvg['memInfoAvg_ax0'].append(msgMetric)
            
        elif msgIndex == 1:   
            metricAvg['memInfoAvg_ax1'].append(msgMetric)
            
        elif msgIndex == 2:   
            metricAvg['memInfoAvg_ax2'].append(msgMetric)
            
        elif msgIndex == 3:   
            metricAvg['memInfoAvg_ax3'].append(msgMetric)
            
        elif msgIndex == 4:   
            metricAvg['memInfoAvg_ax4'].append(msgMetric)
            
    elif topic == 'diskUsageAvg':
        if msgIndex == 0:
            metricAvg['diskUsageAvg_ax0'].append(msgMetric)
            
        elif msgIndex == 1:   
            metricAvg['diskUsageAvg_ax1'].append(msgMetric)
            
        elif msgIndex == 2:   
            metricAvg['diskUsageAvg_ax2'].append(msgMetric)
            
        elif msgIndex == 3:   
            metricAvg['diskUsageAvg_ax3'].append(msgMetric)
            
        elif msgIndex == 4:   
            metricAvg['diskUsageAvg_ax4'].append(msgMetric)

    print("\n####################\n LEN diskusage == ",len(metricAvg['diskUsageAvg_ax4']))
    if(len(metricAvg['diskUsageAvg_ax4']) == 5 ):
        create_graph()
   
def line_chart(X,Y, nameImage):
    plt.clf()
    df = pd.DataFrame(list(zip(X , Y)), columns =['Fibonacci','value']) 
    print("\ndf = \n",df)
    # df = df.groupby(['Fibonacci'],as_index=False).mean()
    df['Metric'] = 'value'
    # Create csv file
    df.to_csv(r'../data/csv/subscriber/linechart_'+nameImage+'.csv',index=False)

    sns.set(style = "whitegrid")
    snsLinePlot = sns.lineplot(x="Fibonacci", y="value",
                   markers=True,   style='Metric' ,data=df)

    snsLinePlot.set_xlabel("QtyLoop")
    snsLinePlot.set_ylabel(nameImage)
    snsLinePlot.set_title('Average Time Process Per Publisher')

    snsLinePlot.figure.savefig('../data/graphics/subscriber/lineChart_'+nameImage+'.png')
    plt.clf()

def transform_data_for_graph():
    print(metricAvg)
    cpuTimeArray = []
    cpuTimePIDArray = []
    memVirtualArray = []
    memInfoArray = []
    diskUsageArray = []

    for metric in metricAvg :
        if len(metricAvg[metric]) != 0 :
            metricAvg[metric] = statistics.mean(metricAvg[metric])
                    
    fibonacci = ['1','2','3','5','8']
    for i in range(5):
        i = str(i)
        cpuTimeArray.append(metricAvg['cpuTimeAvg_ax'+i])
        cpuTimePIDArray.append(metricAvg['cpuTimePIDAvg_ax'+i])
        memVirtualArray.append(metricAvg['memVirtualAvg_ax'+i])
        memInfoArray.append(metricAvg['memInfoAvg_ax'+i])
        diskUsageArray.append(metricAvg['diskUsageAvg_ax'+i])

    return fibonacci,cpuTimeArray,cpuTimePIDArray,memInfoArray,memVirtualArray,diskUsageArray
    
def create_graph():
    fibonacci,cpuTimeArray,cpuTimePIDArray,memInfoArray,memVirtualArray,diskUsageArray = transform_data_for_graph()
    
    line_chart(fibonacci, cpuTimeArray, 'cpuTime')
    line_chart(fibonacci, cpuTimePIDArray, 'cpuTimePID')
    line_chart(fibonacci, memInfoArray, 'memVirtual')
    line_chart(fibonacci, memVirtualArray, 'memInfo')
    line_chart(fibonacci, diskUsageArray, 'diskUsage')

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