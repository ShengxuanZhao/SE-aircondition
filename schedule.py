from socketserver import BaseRequestHandler,ThreadingTCPServer,ForkingTCPServer
import threading
import modulefinder
import send
import schedule
import ast
import json
import core
import types
"""
class user:
    def __init__(self,room,address):
        self.room=room
        self.address=address

    def daily(self,message):
        dailyreport=self.room+" "+message[1]
        #send to vicky
        send.sock.sendall(dailyreport)
        roominfo=send.sock.recv()

        #send to client
        s=send.socket.socket((self.address,core.PORT))
        recv=s.recv()
        repost={'switch','temperture','wind','cost'}
        times=recv.find(" ")
        for i in range(len(recv)):
           if recv[i].isspace()==False:
                 temp=temp+recv[i]
           else:
               temp=" "
               times=times-1

           if times==4:
                 repost['switch']=0
           if times == 3:
                 repost['temperture']=temp
           if times == 2:
               repost['wind'] = temp
           if times == 1:
               repost['cost'] = temp
        repost=json.loads(repost)
        s.request.sendall(repost)
"""

#加时间控制
class Handler(BaseRequestHandler):

    def handle(self):
        address, pid = self.client_address
        #self.request.sendall('welcomehey!'.encode('utf-8'))
        print('%s connected!' % address)
        self.request.sendall('{welcome!}'.encode('utf-8'))
        #self.request.sendall('aloha'.encode('utf-8'))
        i=0
        while True:
            data = self.request.recv(core.BUF_SIZE)
            #print('%s connected!' % address)
           # self.request.sendall('aloha'.encode('utf-8'))
            #data=json.dumps(data)
            if len(data)>0:
                print('receive=',data.decode('utf-8'))
                print("\n")
                if isinstance(data, bytes):
                    self.request.sendall('{YEP}'.encode('utf-8'))
                else:
                    self.request.sendall('{wrong format! invalid request!}'.encode('utf-8'))
                    #break
            else: continue

#so time for scheduling

            if data['type']==0:
                    i=i+1
                    self.room=data['room']
                    if core.i>=3:
                        if min(core.servicelist[0]['wind'], core.servicelist[1]['wind'], core.servicelist[2]['wind'], data['wind'])==data['wind']:
                            core.waitlist.append(data)
                            core.waitlist = sorted(core.waitlist, key=lambda e: e.__getitem__('wind'), reverse=True)
                            self.request.sendall('Please wait patiently~'.encode('utf-8'))
                        else: #oust one
                            minwind=data['wind']
                            minnum=0
                            for a in range(core.servicelist):
                             if minwind>core.servicelist[a]['wind']:
                                 minnum=a
                            core.servicelist.append(data)
                            core.waitlist.append(core.servicelist[minnum])
                            core.servicelist.remove(core.servicelist[minnum])
                            self.request.sendall('start!'.encode('utf-8'))
                    if core.i<3:
                        core.servicelist.append(data)
                        #cur_thread = threading.current_thread()
                        #response = '{}:{}'.format(cur_thread.ident,data)
                        self.request.sendall('start!'.encode('utf-8'))
                        print('send:','response')
                        core.i=core.i+1
           
            else:
                   if data['type']==1:
                       i=i-1
                       dailyreport = str(self.room) +" "+"1"+ " " + str(data['temperature'])
                       # send to vicky
                       send.sockdb.sendall(dailyreport)
                       roominfo = send.sockdb.recv()

                       # send to client

                       recv = self.request.recv()
                       repost = {'switch', 'temperture', 'wind', 'cost'}
                       times = recv.find(" ")
                       if recv[0]=='A' or recv[0]=='L':
                           for a in range(len(core.servicelist)):
                              if core.servilist[a]['room']==self.room:
                               core.servicelist.remove(core.servilist[a])
                               break

                           if recv[0]=='L':
                                self.request.close()

                       else:
                           if recv[0]=='U':
                               for a in range(len(core.waitlist)):
                                   if core.waitlist[a]['room'] == self.room:
                                       core.waitlist.remove(core.waitlist[a])

                       for i in range(len(recv)):
                           if recv[i].isspace() == False:
                               temp = temp + recv[i]
                           else:
                               temp = " "
                               times = times - 1

                           if times == 4:
                               repost['switch'] = 0
                           if times == 3:
                               repost['temperture'] = temp
                           if times == 2:
                               repost['wind'] = temp
                           if times == 1:
                               repost['cost'] = temp
                       repost = json.loads(repost)
                       self.request.sendall(repost)

                   else:
                       self.request.sendall('unvalid request!'.encode('utf-8'))

    def changeRR(self):
        core.waitlist.append(core.servicelist[0],core.servicelist[1],core.servicelist[2])
        core.servicelist.remove(core.servicelist[0],core.servicelist[1],core.servicelist[2])
        core.waitlist= sorted(core.waitlist, key=lambda e: e.__getitem__('wind'), reverse=True)
        core.servicelist.append(core.waitlist[0],core.waitlist[1],core.waitlist[2])
