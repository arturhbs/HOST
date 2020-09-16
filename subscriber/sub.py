import sys
import time
import json
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np
import statistics
import pandas as pd
import seaborn as sns



metricAvg = {'cpuTimeAvg_0':[],'cpuTimeAvg_1':[],'cpuTimeAvg_2':[],'cpuTimeAvg_3':[],'cpuTimeAvg_4':[],
            'cpuTimePIDAvg_0':[] ,'cpuTimePIDAvg_1':[],'cpuTimePIDAvg_2':[],'cpuTimePIDAvg_3':[],'cpuTimePIDAvg_4':[],
            'memVirtualAvg_0':[],'memVirtualAvg_1':[],'memVirtualAvg_2':[],'memVirtualAvg_3':[],'memVirtualAvg_4':[] ,
            'memInfoAvg_0':[],'memInfoAvg_1':[],'memInfoAvg_2':[],'memInfoAvg_3':[],'memInfoAvg_4':[],
            'diskUsageAvg_0':[],'diskUsageAvg_1':[],'diskUsageAvg_2':[],'diskUsageAvg_3':[],'diskUsageAvg_4':[] }

finished = 0


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#") # Show every message
    client.subscribe([('finished',0),('cpuTimeAvg',0),('cpuTimePIDAvg',0),('memVirtualAvg',0),('memInfoAvg',0),('diskUsageAvg',0)],qos=1)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    message = msg.payload.decode('UTF-8')
    messageSplit = message.split(sep=',')
    messageMetric = float(messageSplit[0])
    messageIndex = int(messageSplit[1])
    read_message(msg.topic,messageMetric,messageIndex)

# Identify message recieved
def read_message(topic,msgMetric,msgIndex):
    print('topic = ', topic)
    print('msg index', msgIndex)
    if topic == 'cpuTimeAvg':
        # Get metric for 8 loops
        if msgIndex == 0:
            metricAvg['cpuTimeAvg_0'].append(msgMetric)
            
        # Get metric for 13 loops
        elif msgIndex == 1:   
            metricAvg['cpuTimeAvg_1'].append(msgMetric)

        # Get metric for 21 loops
        elif msgIndex == 2:   
            metricAvg['cpuTimeAvg_2'].append(msgMetric)
            
        # Get metric for 34 loops
        elif msgIndex == 3:   
            metricAvg['cpuTimeAvg_3'].append(msgMetric)
            
        # Get metric for 55 loops
        elif msgIndex == 4:   
            metricAvg['cpuTimeAvg_4'].append(msgMetric)
            
    elif topic == 'cpuTimePIDAvg':
        # Get metric for 8 loops
        if msgIndex == 0:
            metricAvg['cpuTimePIDAvg_0'].append(msgMetric)
            
        # Get metric for 13 loops
        elif msgIndex == 1:   
            metricAvg['cpuTimePIDAvg_1'].append(msgMetric)

        # Get metric for 21 loops
        elif msgIndex == 2:   
            metricAvg['cpuTimePIDAvg_2'].append(msgMetric)
            
        # Get metric for 34 loops
        elif msgIndex == 3:   
            metricAvg['cpuTimePIDAvg_3'].append(msgMetric)

        # Get metric for 55 loops
        elif msgIndex == 4:   
            metricAvg['cpuTimePIDAvg_4'].append(msgMetric)
            
    elif topic == 'memVirtualAvg':
        if msgIndex == 0:
            metricAvg['memVirtualAvg_0'].append(msgMetric)
            
        elif msgIndex == 1:   
            metricAvg['memVirtualAvg_1'].append(msgMetric)
            
        elif msgIndex == 2:   
            metricAvg['memVirtualAvg_2'].append(msgMetric)
            
        elif msgIndex == 3:   
            metricAvg['memVirtualAvg_3'].append(msgMetric)
            
        elif msgIndex == 4:   
            metricAvg['memVirtualAvg_4'].append(msgMetric)
            
    elif topic == 'memInfoAvg':
        if msgIndex == 0:
            metricAvg['memInfoAvg_0'].append(msgMetric)
            
        elif msgIndex == 1:   
            metricAvg['memInfoAvg_1'].append(msgMetric)
            
        elif msgIndex == 2:   
            metricAvg['memInfoAvg_2'].append(msgMetric)
            
        elif msgIndex == 3:   
            metricAvg['memInfoAvg_3'].append(msgMetric)
            
        elif msgIndex == 4:   
            metricAvg['memInfoAvg_4'].append(msgMetric)
            
    elif topic == 'diskUsageAvg':
        if msgIndex == 0:
            metricAvg['diskUsageAvg_0'].append(msgMetric)
            
        elif msgIndex == 1:   
            metricAvg['diskUsageAvg_1'].append(msgMetric)
            
        elif msgIndex == 2:   
            metricAvg['diskUsageAvg_2'].append(msgMetric)
            
        elif msgIndex == 3:   
            metricAvg['diskUsageAvg_3'].append(msgMetric)
            
        elif msgIndex == 4:   
            metricAvg['diskUsageAvg_4'].append(msgMetric)
 
    # print("finished = ", finished)
    # if topic == 'finished':
    #     finished += 1
    print('LEN == ',len(metricAvg['diskUsageAvg_3']))
    if(len(metricAvg['diskUsageAvg_3']) == 3 ):
        create_graph()
    # if nameMetricIndex ==  'diskUsageAvg_4':
    #     print("tamanho disk4: ",len(metric))
    # if len(metric) == 5 :
    # create_graph()

def line_chart(X,Y, nameImage):
    plt.clf()
    df = pd.DataFrame(list(zip(X , Y)), columns =['Fibonacci','value']) 
    df['Metric'] = 'value'
    sns.set(style = "whitegrid")
    snsLinePlot = sns.lineplot(x="Fibonacci", y="value",
                   markers=True,   style='Metric' ,data=df).set_title(nameImage)

    snsLinePlot.figure.savefig('../data/subscriber/lineChart_'+nameImage+'.png')
    plt.clf()

def transform_data_for_graph():
    cpuTimeArray = []
    cpuTimePIDArray = []
    memVirtualArray = []
    memInfoArray = []
    diskUsageArray = []

    print("metricAVG = ")
    print(metricAvg)
    for metric in metricAvg :
        if len(metricAvg[metric]) != 0 :
            metricAvg[metric] = statistics.mean(metricAvg[metric])
                    
    print(metricAvg)
    fibonacci = ['8','13','21','34','55']
    for i in range(3):
        j = str(i)
        cpuTimeArray.append(metricAvg['cpuTimeAvg_'+j])
        cpuTimePIDArray.append(metricAvg['cpuTimePIDAvg_'+j])
        memVirtualArray.append(metricAvg['memVirtualAvg_'+j])
        memInfoArray.append(metricAvg['memInfoAvg_'+j])
        diskUsageArray.append(metricAvg['diskUsageAvg_'+j])

    return fibonacci,cpuTimeArray,cpuTimePIDArray,memInfoArray,memVirtualArray,diskUsageArray
    
def create_graph():
    print('*********************')
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