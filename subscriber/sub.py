import sys
import time
import json
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np

take_time = []
take_count = []

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#") # Show every message
    client.subscribe([("count", 0),('time', 0)],qos=1)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    message = msg.payload.decode('UTF-8')
    message = float(message)
    read_message(msg.topic,message)

# Identify message recieved
def read_message(topic,msg):
    if topic == 'time':
        take_time.append(msg)
    if topic == 'count':
        take_count.append(msg)
    lastTopic = topic    
    check_valeus(take_time, take_count, lastTopic)

def check_valeus(take_time, take_count, lastTopic):
    print(len(take_time))
    if len(take_time)%5 == 0 and lastTopic == 'time':
        axY = []
        for i in range(len(take_time)):
            axY.append(i+1)
        # axY = np.arrange(len(take_time))
        axX = take_time
        graphic(axY,axX)

# Create bar chart
def graphic(Y,X):
    
    fig, ax = plt.subplots()
    rects = ax.bar(Y, X)
    ax.set_title('Time process per publisher')
    ax.set_ylabel('Time')    
    ax.set_xlabel('Quantity of topics')
    
    # Make some labels.
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.01*height,
                '%d' % int(height),
                ha='center', va='bottom')

    plt.savefig('../data/count.png')

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