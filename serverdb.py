import os
import pymysql

#use the database named aircondition
def connectdatabase():
	#print("Please input the password of the database:")
	#psw=input()
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
	#cmd="drop table if exists "+roomid+";"
	#dbcur.execute(cmd)
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
	#print(cmd)
	

def writerecordroom(db,dbcur,roomid,s):
	s=s.split(" ")
	a=s[0]
	b=s[1:]
	if a=='0':
		cmd="select cur_t from "+roomid+" order by time asce limit 1;"
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		c=dbcur.fetchone()
		b.insert(1,c)
		cmd="insert into "+roomid+" values(now()"
		for i in b:
			cmd=cmd+","+str(i)
		cmd=cmd+");"

	else:
		cmd="select switch,tar_t,w_speed from "+roomid+" order by time asc limit 1;"
		dbcur.execute(cmd)
		try:
			dbcur.execute(cmd)
			db.commit()
		except:
			db.rollback()
		c,d,e=dbcur.fetchone()
		b.insert(0,c) 
		b.insert(2,d)
		b.insert(3,e)
		cmd="insert into hotel values(now()"
		for i in b:
			cmd=cmd+","+str(i)
		cmd=cmd+");"
	print(cmd)
	dbcur.execute(cmd)


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


#def currentcost():



if __name__=='__main__':
	(dbcur,db)=connectdatabase()

	createtablehotel(db,dbcur)
	createtableroom(db,dbcur,"abc")
	writerecordroom(db,dbcur,"abc","0 1 28 1 1")

