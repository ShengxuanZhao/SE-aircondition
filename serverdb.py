import os
import pymysql
import time
import datetime
import json
import types 
import socket
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time, threading

swps=1
mwps=2
wind=0.01
mode=1#运行模式默认为制冷，0为制热
# cost=rate*wind_of_room ps
updatelock=threading.Lock()
mainlock=threading.Lock()

#登陆数据库，选择数据库
def connectdatabase():
	#print("请输入服务器端数据库登陆密码：")
	#psw=input()
	#print("请选择数据库：")
	#dbname=input()
	db=pymysql.connect("localhost","root","Vi97@xuan&cky","aircondition")
	dbcur=db.cursor()
	return (dbcur,db)

#执行传入数据库的指令cmd
def excutecmd(db,dbcur,cmd):
	try:
		dbcur.execute(cmd)
		db.commit()
		#print(cmd,"执行成功")
	except:
		db.rollback()
		print(cmd,"执行失败")
		traceback.print_exc()
	return(db,dbcur)

#创建hotel表，记录所有房间当前情况
def createtablehotel(db,dbcur):
	cmd="create table if not exists hotel("
	cmd=cmd+"roomid varchar(8) not null,switch varchar(1),"
	#cmd=cmd+"temperature decimal(4,2),wind varchar(1),cost decimal(7,2),"
	cmd=cmd+"temperature decimal(4,2),wind varchar(1),cost decimal(7,2)"
	#cmd=cmd+"primary key(roomid)"
	cmd=cmd+");"
	(db,dbcur)=excutecmd(db,dbcur,cmd)
	return

#为每个新出现的房间建表，表格名称为room+房间号
def createtableroom(db,dbcur,roomid):
	cmd="SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_NAME='"+roomid+"'"
	(db,dbcur)=excutecmd(db,dbcur,cmd)
	a=dbcur.fetchone()

	#the room not exists
	if a[0]==0:
		cmd="create table if not exists "
		cmd=cmd+roomid
		cmd=cmd+" (time datetime not null,"
		cmd=cmd+"switch varchar(1),cur_t decimal(4,2),tar_t decimal(4,2),"
		#cmd=cmd+"w_speed varchar(1),cur_cost decimal(7,2),primary key(time));"
		cmd=cmd+"w_speed varchar(1),cur_cost decimal(7,2));"
		(db,dbcur)=excutecmd(db,dbcur,cmd)

		cmd="insert into "+roomid+" values"
		cmd=cmd+"(now(),0,26.00,26.00,0,0);"
		(db,dbcur)=excutecmd(db,dbcur,cmd)
		cmd="insert into hotel values('"+roomid+"',0,26.00,0,0);"
		(db,dbcur)=excutecmd(db,dbcur,cmd)
	return
	
#将消息内容（调节请求或当前状态）存入房间表格
def writerecordroom(db,dbcur,roomid,s):
	s=s.rstrip()
	s=s.split(" ") 
	a=s[0]
	print("报文类型：",a)
	b=s[1:]
	print("报文内容：",b)
	if a=='0':#请求报文
		cmd="select cur_t,cur_cost from "+roomid+" order by time desc limit 1;"
		(db,dbcur)=excutecmd(db,dbcur,cmd)
		t,c=dbcur.fetchone()
		t=float(t)
		c=float(c)
		b.insert(1,t)
		b.insert(4,c)
		tt=int(b[1])
		print("目标温度为：",tt,"		判断调节目标是否在当前模式范围内")
		if vaildtargett(tt):
			pass
		else:#调节目标不在当前服务模式的调节范围内
			msg=str("U "+str(roomid)+" 1 "+str(ct)+" "+str(b[3])+" "+str(b[4]))
			print(msg,"调节目标不在当前服务模式的调节范围内")
			return msg

		cmd="insert into "+roomid+" values(now()"
		for i in b:
			cmd=cmd+","+str(i) 
		cmd=cmd+");"
		#time.sleep(1)
		(db,dbcur)=excutecmd(db,dbcur,cmd)
			#traceback.print_exc()#同时执行导致时间主键值一样，无法插入

		(result,ct,tt)=cmpcurrentt(db,dbcur,roomid)
		if result==1:#设置目标温度与当前温度一致
			roomid=roomid[4:]
			# 将风速改为0
			msg=str("U "+str(roomid)+" 1 "+str(ct)+" "+str(b[3])+" "+str(b[4]))
			print(msg,"设置目标温度与当前温度一致")
			return msg
		else:#未达到目标温度，未在调节
			roomid=roomid[4:]
			msg=str("C "+str(roomid)+" 1 "+str(tt)+" "+str(b[3])+" "+str(b[4]))
			print(msg)
			return msg


	#current state
	if a=='1':#通告报文
		signal=b[1]
		print("标志内容：",signal)
		b=b[0:1]

		if signal=='C':#周期通告
			cmd="select switch,tar_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
			(db,dbcur)=excutecmd(db,dbcur,cmd)
			c,d,e,f=dbcur.fetchone()
			#print(c,d,e,f)
			c=int(c)
			d=float(d)
			e=int(e)
			f=float(f)
			b.insert(0,c) 
			b.insert(2,d)
			b.insert(3,e)
			b.insert(4,f+wind*e)#开始计算温度调节 
			#print(c,d,e)
			#cmda="insert into hotel values(now()"
			cmd="insert into "+roomid+" values(now()"
			for i in b:
				cmd=cmd+","+str(i)
			cmd=cmd+");"
			#time.sleep(1)
			(db,dbcur)=excutecmd(db,dbcur,cmd)
			(result,ct,tt)=cmpcurrentt(db,dbcur,roomid)
			if result==1:#通过调节到达目标温度
				roomid=roomid[4:]
				msg=str("A "+str(roomid)+" 0 "+str(ct)+" "+str(e)+" "+str(f))
				print(msg)
				return msg
			else:#未达到目标温度，未在调节
				roomid=roomid[4:]
				msg=str("C "+str(roomid)+" 1 "+str(ct)+" "+str(e)+" "+str(f))
				print(msg)
				return msg

			
		if signal=='D':#开始调度
			cmd="select switch,cur_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
			(db,dbcur)=excutecmd(db,dbcur,cmd)
			c,d,e,f=dbcur.fetchone()
			c=int(c)
			d=float(d)
			e=int(e)
			f=float(f)
			b.insert(0,c) 
			b.insert(1,d)
			b.insert(3,e)
			b.insert(4,f+wind*e)#开始计算温度调节 
			#print(c,d,e)
			#cmda="insert into hotel values(now()"
			cmd="insert into "+roomid+" values(now()"
			for i in b:
				cmd=cmd+","+str(i)
			cmd=cmd+");"
			#time.sleep(1)
			(db,dbcur)=excutecmd(db,dbcur,cmd)
			(result,ct,tt)=cmpcurrentt(db,dbcur,roomid)
			if result==1:#设置目标温度与当前温度一致
				roomid=roomid[4:]
				msg=str("U "+str(roomid)+" 0 "+str(ct)+" "+str(e)+" "+str(f))
				print(msg)
				return msg
			else:#未达到目标温度，未在调节
				roomid=roomid[4:]
				msg=str("C "+str(roomid)+" 1 "+str(tt)+" "+str(e)+" "+str(f))
				print(msg)
				return msg

		if signal=='W':


#比较房间内当前温度和目标温度，是否达到
def cmpcurrentt(db,dbcur,roomid):
	cmd="select cur_t,tar_t from "+roomid+" order by time desc limit 1;"
	(db,dbcur)=excutecmd(db,dbcur,cmd)
	ct,tt=dbcur.fetchone()
	ct=float(ct)
	tt=float(tt)

	print("ct=",ct,"	tt=",tt)
	if ct==tt:#已到达温度
		print("房间"+roomid+"已达目标温度")
		return(1,ct,tt)
	else:#未到达温度
		print("房间"+roomid+"未达目标温度")
		return(0,ct,tt)
		#client.sendall(bytes("A "+roomid,encoding='utf-8'))

#判断调节目标是否在当前模式范围内
def vaildtargett(tt):
	if mode==1:
		if tt>=16 and tt<=25:
			return True
		else:
			return False
	else:
		if mode==0:
			if tt>=27 and tt<=30:
				return True
			else:
				return False


#周期性将所有房间最新信息更新到总表格中
start_time=datetime.now()
def update(db,dbcur):
	start_time=datetime.now()
	while(1):
		updatelock.acquire()
		try:
			current_time=datetime.now()
			if (current_time-start_time).seconds>=1:
				print("最近更新时间：",start_time)
				currentcost(db,dbcur)
				cmd="select roomid from hotel;"
				(db,dbcur)=excutecmd(db,dbcur,cmd)
				roomlist=dbcur.fetchall()
				#print(roomlist)
				l=[]
				for i in roomlist:
					for j in i:
						l.append(str(j))
				for roomid in l:
					cmd="select switch,cur_t,tar_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
					(db,dbcur)=excutecmd(db,dbcur,cmd)
					s,ct,tt,ws,cc=dbcur.fetchone()
					s=int(s)
					ct=float(ct)
					tt=float(tt)
					ws=int(ws)
					cc=float(cc)

					cmd="update hotel set switch="+str(s)
					cmd=cmd+",temperature="+str(ct)
					cmd=cmd+",wind="+str(ws)
					cmd=cmd+",cost="+str(cc)
					cmd=cmd+" where roomid='"+roomid+"';"
					#print("update",cmd)
					start_time=current_time	
		finally:
			updatelock.release()

#计算当前处于服务队列的房间单位时间内的cost
def currentcost(db,dbcur):
	cmd="select roomid from hotel where switch=1;"
	(db,dbcur)=excutecmd(db,dbcur,cmd)
	roomlist=dbcur.fetchall()
	print("当前开启空调的房间号：")
	#print(roomlist)
	l=[]
	for i in roomlist:
		for j in i:
			l.append(str(j))
	print(l)
	for roomid in l:
		cmd="select time from "+roomid+" order by time desc limit 1;"
		(db,dbcur)=excutecmd(db,dbcur,cmd)

		cmd="select switch,cur_t,tar_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
		(db,dbcur)=excutecmd(db,dbcur,cmd)
		s,ct,tt,ws,cc=dbcur.fetchone()
		s=int(s)
		ct=float(ct)
		tt=float(tt)
		ws=int(ws)
		cc=float(cc)+wind*ws
		print(roomid,":",cc)


		cmd="insert into "+roomid+" values(now(),"
		cmd=cmd+str(s)+","+str(ct)+","+str(tt)+","+str(ws)+","+str(cc)+");"
		excutecmd(db,dbcur,cmd)
		print(cmd)

		cmd="update hotel set switch="+str(s)
		cmd=cmd+",temperature="+str(ct)
		cmd=cmd+",wind="+str(ws)
		cmd=cmd+",cost="+str(cc)
		cmd=cmd+" where roomid="+roomid+";"
		excutecmd(db,dbcur,cmd)
		print(cmd)
	return


#获取报文第一项房间号，将全数字转化为Room+数字，回传前去掉Room
def getroomid(s):
	s=s.split(" ")
	roomid="Room"+s[0]
	s=s[1:]
	print("roomid:"+roomid)
	temps=""
	for i in s:
		temps=temps+str(i)+" "

	print("msg:"+temps)
	return (str(roomid),temps)

#打印某一房间的详单，在关闭空调的指令发出后打印详单
def detailedlist(db,dbcur,roomid):
	cmd="select * from "+roomid+";"
	(db,dbcur)=excutecmd(db,dbcur,cmd)
	dl=dbcur.fetchall()#detailedlist
	l=[]
	ll=[]
	for i in dl:
		for j in i:
			ll.append(j)
		l.append(ll)
		ll=[]

	print("时间				",end='		')
	print("开关",end='		')
	print("实际温度",end='		')
	print("目标温度",end='		')
	print("风速",end='		')
	print("金额",end='		')
	print("\n")

	for a in l:
		for b in a:
			print(b,end='		')
		print("\n")


# 执行收发报文
def mainthread(server,max_size):
	while(1):
		#updatelock.acquire()
		#try:
			client,addr = server.accept()
			while(1):
				#update(db,dbcur)
				res_bytes = client.recv(max_size)
				if not res_bytes:
					break
				res_str = str(res_bytes, encoding='utf-8')
				print("message:"+res_str)
				(roomid,msg)=getroomid(res_str)
				createtableroom(db,dbcur,roomid)
				smsg=writerecordroom(db,dbcur,roomid,msg)
				print("返回消息:"+smsg)
				client.sendall(bytes(smsg,encoding='utf-8'))
		#finally:
		#	updatelock.release()

	client.close()
	server.close()


def setpara():
	global mode
	mode=input("请设置空调运行模式（1-制冷，0-制热）：")

	

if __name__=='__main__':
	print("Start the server at {}".format(datetime.now()))
	address = ('10.213.27.207',7020)
	max_size = 1024

	(dbcur,db)=connectdatabase()
	createtablehotel(db,dbcur)
	server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	server.bind(address)
	server.listen(5)
	print("after listen")


	tupdate=threading.Thread(target=update, args=(db,dbcur,))
	pthread=threading.Thread(target=mainthread, args=(server,max_size,))

	pthread.start()
	tupdate.start()
	pthread.join()
	tupdate.join()

	
