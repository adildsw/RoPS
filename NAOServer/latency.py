import requests
from time import time

sum=0
for i in range (0,1000):
    latency = 0.3 + float(requests.get("http://192.168.86.178:5000/latency?time={}".format(time())).text)
    sum+=latency
    print (latency)
    
# print (sum/1000)
