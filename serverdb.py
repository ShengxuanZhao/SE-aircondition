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

swps=0.01
mwps=0.02
wind=0.01

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
	print(cmd)
	try:
		dbcur.execute(cmd)
		db.commit()
		print(cmd,"执行成功")
	except:
		db.rollback()
		print(cmd,"执行失败")
	return

#创建hotel表，记录所有房间当前情况
def createtablehotel(db,dbcur):
	cmd="create table if not exists hotel("
	cmd=cmd+"roomid varchar(8) not null,switch varchar(1),"
	cmd=cmd+"temperature decimal(4,2),wind varchar(1),cost decimal(7,2),"
	cmd=cmd+"primary key(roomid)"
	cmd=cmd+");"
	excutecmd(db,dbcur,cmd)

#为每个新出现的房间建表，表格名称为room+房间号
def createtableroom(db,dbcur,roomid):
	cmd="SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_NAME='"+roomid+"'"
	try:
		dbcur.execute(cmd)
		db.commit()
	except:
		db.rollback()
	a=dbcur.fetchone()

	#the room not exists
	if a[0]==0:
		cmd="create table if not exists "
		cmd=cmd+roomid
		cmd=cmd+" (time datetime not null,"
		cmd=cmd+"switch varchar(1),cur_t decimal(4,2),tar_t decimal(4,2),"
		#cmd=cmd+"w_speed varchar(1),cur_cost decimal(7,2),primary key(time));"
		cmd=cmd+"w_speed varchar(1),cur_cost decimal(7,2));"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()

		cmd="insert into "+roomid+" values"
		cmd=cmd+"(now(),0,26.00,26.00,0,0);"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback() 
		cmd="insert into hotel values('"+roomid+"',0,26.00,0,0);"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		print(cmd)
	
#将消息内容（调节请求或当前状态）存入房间表格
def writerecordroom(db,dbcur,roomid,s):
	s=s.rstrip()
	s=s.split(" ") 
	a=s[0]
	print("type:"+a)
	b=s[1:]
	print(b)
	if a=='0':#请求报文
		cmd="select cur_t,cur_cost from "+roomid+" order by time desc limit 1;"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		t,c=dbcur.fetchone()
		print(t,c)
		t=float(t)
		c=float(c)
		b.insert(1,t)
		b.insert(4,c)
		cmd="insert into "+roomid+" values(now()"
		for i in b:
			cmd=cmd+","+str(i) 
		cmd=cmd+");"
		#time.sleep(1)
		try:
			dbcur.execute(cmd)
			db.commit()
			#print("okokok")
		except:
			db.rollback()
			#traceback.print_exc()#同时执行导致时间主键值一样，无法插入
		print(cmd) 

		(result,ct,tt)=cmpcurrentt(db,dbcur,roomid)
		if result==1:#设置目标温度与当前温度一致
			msg=str("U "+str(roomid)+" 0 "+str(ct)+" "+str(b[3])+" "+str(b[4]))
			print(msg)
			return msg
		else:#未达到目标温度，未在调节
			msg=str("C "+str(roomid)+" 1 "+str(tt)+" "+str(b[3])+" "+str(b[4]))
			print(msg)
			return msg


	#current state
	if a=='1':#通告报文
		signal=b[1]
		print("signal:"+signal)
		b=b[0:1]

		if signal=='C':#周期通告
			cmd="select switch,tar_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
			try:
				dbcur.execute(cmd)
				db.commit()
			except:
				db.rollback()
			c,d,e,f=dbcur.fetchone()
			print(c,d,e,f)
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
			try:
				dbcur.execute(cmd)
				db.commit()
			except:
				db.rollback()
			print(cmd)
			(result,ct,tt)=cmpcurrentt(db,dbcur,roomid)
			if result==1:#通过调节到达目标温度
				msg=str("A "+str(roomid)+" 0 "+str(ct)+" "+str(e)+" "+str(f))
				print(msg)
				return msg
			else:#未达到目标温度，未在调节
				msg=str("C "+str(roomid)+" 1 "+str(ct)+" "+str(e)+" "+str(f))
				print(msg)
				return msg

			
		if signal=='D':#开始调度
			cmd="select switch,cur_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
			try:
				dbcur.execute(cmd)
				db.commit()
			except:
				db.rollback()
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
			try:
				dbcur.execute(cmd)
				db.commit()
			except:
				db.rollback()
			print(cmd)
			(result,ct,tt)=cmpcurrentt(db,dbcur,roomid)
			if result==1:#设置目标温度与当前温度一致
				msg=str("U "+str(roomid)+" 0 "+str(ct)+" "+str(e)+" "+str(f))
				print(msg)
				return msg
			else:#未达到目标温度，未在调节
				msg=str("C "+str(roomid)+" 1 "+str(tt)+" "+str(e)+" "+str(f))
				print(msg)
				return msg

#比较房间内当前温度和目标温度，是否达到
def cmpcurrentt(db,dbcur,roomid):
	cmd="select cur_t,tar_t from "+roomid+" order by time desc limit 1;"
	try:
		dbcur.execute(cmd)
		db.commit()
	except: 
		db.rollback()
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

#周期性将所有房间最新信息更新到总表格中
def update(db,dbcur):
	cmd="select roomid from hotel;"
	try:
		dbcur.execute(cmd)
		db.commit()
	except: 
		db.rollback()
	roomlist=dbcur.fetchall()
	print(roomlist)
	l=[]
	for i in roomlist:
		for j in i:
			l.append(str(j))
	print(l)
	for roomid in l:
		cmd="select switch,cur_t,tar_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
		try:
			dbcur.execute(cmd)
			db.commit()
		except: 
			db.rollback()
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
		cmd=cmd+" where roomid="+roomid+";"
		#print(cmd)
	return

#计算当前处于服务队列的房间单位时间内的cost
#当前未用到
def currentcost(db,dbcur):
	cmd="select roomid from hotel where switch=1;"
	try:
		dbcur.execute(cmd)
		db.commit()
	except: 
		db.rollback()
	roomlist=dbcur.fetchall()
	print("当前开启空调的房间号：")
	print(roomlist)
	l=[]
	for i in roomlist:
		for j in i:
			l.append(str(j))
	print(l)
	for roomid in l:
		cmd="select time from "+roomid+" order by time desc limit 1;"
		try:
			dbcur.execute(cmd)
			db.commit()
		except: 
			db.rollback()

		cmd="select switch,cur_t,tar_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
		try:
			dbcur.execute(cmd)
			db.commit()
		except: 
			db.rollback()
		s,ct,tt,ws,cc=dbcur.fetchone()
		s=int(s)
		ct=float(ct)
		tt=float(tt)
		ws=int(ws)
		cc=float(cc)


		cmd="insert into "+roomid+" values(now(),"
		cmd=cmd+str(s)+","+str(ct)+","+str(tt)+","+str(ws)+","+str(cc)+");"

		cmd="update hotel set switch="+str(s)
		cmd=cmd+",temperature="+str(ct)
		cmd=cmd+",wind="+str(ws)
		cmd=cmd+",cost="+str(cc)
		cmd=cmd+" where roomid="+roomid+";"
		print(cmd)
	return





	cmd="select roomid from hotel where wind=1;"
	try:
		dbcur.execute(cmd)
		db.commit()
	except:
		db.rollback()
	roomlist=dbcur.fetchall()
	rl=[]
	for i in roomlist:
		for j in i:
			rl.append(j)

	for i in rl:
		(reach,cur_temp)=currentt(db,dbcur,i)
		if reach==1:
			#回传温度已达目标温度
			pass
		else:
			#继续放在服务队列
			pass

	#print(roomlist)
	#print(rl)


#获取报文第一项房间号
def getroomid(s):
	s=s.split(" ")
	roomid=s[0]
	s=s[1:]
	print("roomid:"+roomid)
	temps=""
	for i in s:
		temps=temps+str(i)+" "

	print("msg:"+temps)
	return (str(roomid),temps)

#打印某一房间的详单
def detailedlist(db,dbcur,roomid):
	cmd="select * from "+roomid+";"
	try:
		dbcur.execute(cmd)
		db.commit()
	except:
		db.rollback()
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


if __name__=='__main__':
	print("Start the server at {}".format(datetime.now()))
	address = ('localhost',9017)
	max_size = 1024

	#input the price for each kind of wind
	(dbcur,db)=connectdatabase()
	createtablehotel(db,dbcur)
	#currentcost(db,dbcur)	
	#detailedlist(db,dbcur,"roomabc")
	server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	server.bind(address)
	server.listen(1)

	while(1):
		client,addr = server.accept()
		while(1):
			update(db,dbcur)
			res_bytes = client.recv(max_size)
			#print("aaaa")
			if not res_bytes:
				break
			res_str = str(res_bytes, encoding='utf-8')
			print("message:"+res_str)
			(roomid,msg)=getroomid(res_str)
			createtableroom(db,dbcur,roomid)
			smsg=writerecordroom(db,dbcur,roomid,msg)
			client.sendall(bytes(smsg,encoding='utf-8'))

	client.close()
	server.close()
	#currentcost(db,dbcur)
	
	#writerecordroom(db,dbcur,"abc","0 1 28 1 1")
	#writerecordroom(db,dbcur,"abc","1 26.4")

	
