# if use perf_counter will calculate time with sleep time 
from time import process_time, perf_counter
import time
import paho.mqtt.client as mqtt

host_ip = '172.17.0.1'
port = 1883
keepalive = 20


client = mqtt.Client()
client.connect(host_ip, port, keepalive)
time_start = perf_counter()

i=0
while True:
    time.sleep(1)
    i+=1
    message=str(i)
    if i <=10:
        client.publish('count',message)
    else:
        break


time_end = perf_counter()

time_total = time_end - time_start
client.publish('time',time_total)
client.disconnect()

print("Time start: ", time_start)
print("Time end: ", time_end)
print("Time in seconds: ", time_total)


