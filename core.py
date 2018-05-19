import json
import socket
import threading
from threading import Thread, Semaphore
import time
import types
import datetime
#import psutil
#need：1.json 2.compare and fetch
#question 1。统一1秒？

def tcplink(connect, addr):
    while True:
        print('Accept new connection from %s:%s...' % addr)

        #connect.send(json.dump('Welcome!\r\n'))
        jsondata = connect.recv(1024)#receieve
        print(jsondata)
        data = json.loads(jsondata)#decode
        print("this is:"+data)
        connect.send(json.dump(('Hello,room %s' % data['room'].decode('utf-8')).encode('utf-8')))#feedback
        time.sleep(1)
        #if not data or data.decode('utf-8') == 'exit':

        print("Device: %s, Data: %s, Size: %s" % (addr[0], data.decode('utf-8'), len(data)))

        if data['type']==1:
            #give vicky
            connect.send(json.dump(
                ('ok' % data['room'].decode('utf-8')).encode(
                    'utf-8')))  # feedback
        else:
          if sem.acquire():
            #get from vicky
            if data['switch']==0:
                #send 详单
                connect.send(json.dump(
                    ('ok' % data['room'].decode('utf-8')).encode(
                        'utf-8')))  # feedback
            else:
                temperturenow=0#get from vicky
                if data['temperature']==temperturenow:
                    data['wind']=0
                    #send to vicky and user
                    connect.send(json.dump(('Hello,room %s,your room has reach the room temperature' % data['room'].decode('utf-8')).encode('utf-8')))  # feedback
                else:
                    connect.send(json.dump(('Hello,room %s your request is responsed' % data['room'].decode('utf-8')).encode('utf-8')))  # feedback
            sem.release()
          else:
             connect.send(json.dump(('Sorry,room %s, please wait for a second because of a queue' % data['room'].decode('utf-8')).encode('utf-8')))  # feedback

    connect.close()
    print('Connection from %s:%s closed' % addr)


ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ser.bind(('192.168.43.20', 12345))

ser.listen(1)   # 监听连接 如果有超过5个连接请求，从第6个开始不会被accept

sem=Semaphore(3)    #设置计数器的值为3
print('Server is running...')       # 打印运行提示


while True:
    sock, addr = ser.accept()
    print('Accept a sock,addr is:', sock,addr)
    pthread = threading.Thread(target=tcplink, args=(sock, addr))   #多线程处理socket连接,调度算法FCFS
    pthread.start()

