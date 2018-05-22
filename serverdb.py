import os
import pymysql
import time
import datetime
import json
import types 
import socket
from datetime import datetime

swps=0.01
mwps=0.02
wind=0.01

#use the database named aircondition
def connectdatabase():
	#print("Please input the password of the database:")
	#psw=input()
	#print(aaa)
	db=pymysql.connect("localhost","root","Vi97@xuan&cky","aircondition")
	dbcur=db.cursor()
	return (dbcur,db)

#create table to record all the room state
def createtablehotel(db,dbcur):
	cmd="create table if not exists hotel("
	cmd=cmd+"roomid varchar(8) not null,switch varchar(1),"
	cmd=cmd+"temperature decimal(4,2),wind varchar(1),cost decimal(7,2),"
	cmd=cmd+"primary key(roomid)"
	cmd=cmd+");"
	try:
		dbcur.execute(cmd)
		db.commit()
	except:
		db.rollback()

def createtableroom(db,dbcur,roomid):
	cmd="SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_NAME='"+roomid+"'"
	try:
		dbcur.execute(cmd)
		db.commit()
	except:
		db.rollback()
	a=dbcur.fetchone()
	#print(a[0])
	#the room not exists
	if a[0]==0:
		cmd="create table if not exists "
		cmd=cmd+roomid
		cmd=cmd+" (time datetime not null,"
		cmd=cmd+"switch varchar(1),cur_t decimal(4,2),tar_t decimal(4,2),"
		cmd=cmd+"w_speed varchar(1),cur_cost decimal(7,2),primary key(time));"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
			#print(cmd)

		cmd="insert into "+roomid+" values"
		cmd=cmd+"(now(),0,26,26,0,0);"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback() 
		cmd="insert into hotel values('"+roomid+"',0,26,0,0);"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		print(cmd)
	

def writerecordroom(db,dbcur,roomid,s):
	s=s.split(" ") 
	a=s[0]
	print(a)
	b=s[1:]
	if a=='0':
		cmd="select cur_t from "+roomid+" order by time asc limit 1;"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		c=dbcur.fetchone()
		print(c[0])
		b.insert(1,c[0])
		cmd="insert into "+roomid+" values(now()"
		for i in b:
			cmd=cmd+","+str(i) 
		cmd=cmd+");"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		print(cmd) 

	#current state
	if a=='1':
		cmd="select switch,tar_t,w_speed,cur_cost from "+roomid+" order by time desc limit 1;"
		dbcur.execute(cmd)
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		c,d,e,f=dbcur.fetchone()
		e=int(e)
		f=float(f)
		b.insert(0,c) 
		b.insert(2,d)
		b.insert(3,e)
		b.insert(4,f+wind*e)
		print(c,d,e)
		#cmda="insert into hotel values(now()"
		cmd="insert into "+roomid+" values(now()"
		for i in b:
			cmd=cmd+","+str(i)
		cmd=cmd+");"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		print(cmd)
		currentcost(db,dbcur,roomid)



def writerecordhotel(db,dbcur,roomid):
	cmd="insert into hotel values("
	cmd=cmd+roomid+","
	cmd=cmd+");"
	dbcur.execute(cmd)


def currentt():
	cmd="selest cur_t  from hotel;"
	dbcur.execute(cmd)
	rows=dbcur.fetchall()
	result=""
	
	for r in rows:
		result


def currentcost(db,dbcur,roomid):
	cmd="select * from "+roomid+";"
	try:
		dbcur.execute(cmd)
		db.commit()
	except:
		db.rollback()
	a=dbcur.fetchone()
	print(a)



if __name__=='__main__':
	print("Start the server at {}".format(datetime.now()))
	address = ('localhost', 1138)
	max_size = 1024
	
	#data = client.recv(max_size)

	#input the price for each kind of wind
	(dbcur,db)=connectdatabase()
	
	createtablehotel(db,dbcur)
	createtableroom(db,dbcur,"abc")
	

	while(1):
		server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		server.bind(address)
		server.listen(5)
		client,addr = server.accept()
		res_bytes = client.recv(max_size)
		print(res_bytes)
		res_str = str(res_bytes, encoding='utf-8')

		writerecordroom(db,dbcur,"abc",res_str)
		client.sendall(bytes("got it",encoding='utf-8'))
		client.close()
		server.close()


	
	#writerecordroom(db,dbcur,"abc","0 1 28 1 1")
	#writerecordroom(db,dbcur,"abc","1 26.4")

	
