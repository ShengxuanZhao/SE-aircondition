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
import core

wind = 0.01
mode = 1  # 运行模式默认为制冷，0为制热
# cost=rate*wind_of_room ps
_D_CURS_ = {}  # 当前开关
_D_CURT_ = {}  # 当前温度
_D_TART_ = {}  # 目标温度
_D_CURC_ = {}  # 当前花费
_D_WIND_ = {}  # 当前风速
_D_TARW_ = {}  # 目标风速

windagain = []
updatelock = threading.Lock()
mainlock = threading.Lock()


class dbfunc():

    def __init__(self):
        (self.dbcur, self.db) = self.connectdatabase()
        self.createtablehotel()

        # 登陆数据库，选择数据库

    def connectdatabase(self):
        db = pymysql.connect("localhost", "root", "123456", "airconditioner")
        dbcur = db.cursor()
        return (dbcur, db)

    # 执行传入数据库的指令cmd
    def excutecmd(self, cmd):
        db = self.db
        dbcur = self.dbcur
        # print("正在执行：",cmd)
        try:
            dbcur.execute(cmd)
            db.commit()
            print(cmd, "执行成功")
        except:
            db.rollback()
            print(cmd, "执行失败")
        # traceback.print_exc()
        return (db, dbcur)

    # 创建hotel表，记录所有房间当前情况
    def createtablehotel(self):
        db = self.db
        dbcur = self.dbcur
        cmd = "create table if not exists hotel(roomid varchar(8) not null,switch varchar(1),temperature decimal(4,2),wind varchar(1),cost decimal(7,2));"
        (db, dbcur) = self.excutecmd(cmd)
        return

    # 为每个新出现的房间建表，表格名称为room+房间号
    # 初始参数为开机时房间回传的数据
    # 即传来第一条请求报文的时候，创建房间
    def createtableroom(self, db, dbcur, roomid, b):
        print("hello here")
        global mode
        global _D_CURS_
        global _D_CURT_
        global _D_TART_
        global _D_CURC_
        global _D_WIND_
        global _D_TARW_
        cmd = "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_NAME='" + roomid + "';"
        (db, dbcur) = self.excutecmd(cmd)
        a = dbcur.fetchone()
        print(roomid, "create")
        # 该房间还不存在，需要创建
        if int(a[0]) == 0:
            print("该房间还不存在，需要创建")
            cmd = "create table if not exists "
            cmd = cmd + roomid
            cmd = cmd + " (time datetime not null,"
            cmd = cmd + "switch varchar(1),cur_t decimal(4,2),tar_t decimal(4,2),"
            # cmd=cmd+"w_speed varchar(1),cur_cost decimal(7,2),primary key(time));"
            cmd = cmd + "w_speed varchar(1),cur_cost decimal(7,2));"
            (db, dbcur) = self.excutecmd(cmd)
            cmd = "insert into " + roomid + " values"
            cmd = cmd + "(now()," + str(int(b[0])) + ",26.00," + str(float(b[1])) + "," + str(int(b[2])) + ",0);"
            (db, dbcur) = self.excutecmd(cmd)
            print(cmd)
            cmd = "insert into hotel values('" + roomid + "'," + str(int(b[0])) + ",26.00," + str(int(b[2])) + ",0);"
            (db, dbcur) = self.excutecmd(cmd)
            print(cmd)
            _D_CURS_[roomid] = int(b[0])
            _D_CURT_[roomid] = 26.00
            _D_TART_[roomid] = float(b[1])
            _D_CURC_[roomid] = 0
            _D_WIND_[roomid] = int(b[2])
            _D_TARW_[roomid] = _D_WIND_[roomid]
        return

    # 将消息内容（调节请求或当前状态）存入房间表格
    def writerecordroom(self, db, dbcur, roomid, s):
        global windagain
        global _D_CURS_
        global _D_CURT_
        global _D_TART_
        global _D_CURC_
        global _D_WIND_
        global _D_TARW_
        """
        if roomid in windagain:
            temproomid = roomid[4:]
            msg = str(
                "0 " + str(temproomid) + " 1 " + str(float(_D_TART_[roomid])) + " " + str(_D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
            print(msg, "该房间需要回温")
            windagain.remove(roomid)
            # 先处理新的传入报文，再将是否回送风的信息传回，有问题####################
            self.writerecordroom( db, dbcur, roomid, s)
            return msg
        """

        s = s.rstrip()
        s = s.split(" ")
        a = s[0]
        print("报文类型：", a)
        b = s[1:]
        print("报文内容：", b)
        self.createtableroom(db, dbcur, roomid, b)  # b=[switch,tar_t,wind]
        if a == '0':  # 请求报文
            # 判断房间是否已经创建
            cmd = "select cur_t,cur_cost from " + roomid + " order by time desc limit 1;"
            (db, dbcur) = self.excutecmd(cmd)
            t, c = dbcur.fetchone()
            t = float(t)
            c = float(c)
            _D_CURS_[roomid] = int(b[0])
            _D_CURT_[roomid] = round(float(t), 2)
            #_D_CURC_[roomid] = c + _D_CURC_[roomid]
            #_D_CURC_[roomid] = _D_CURC_[roomid]
            _D_WIND_[roomid] = int(b[2])
            _D_TART_[roomid] = round(float(b[1]), 2)
            _D_TARW_[roomid] = _D_WIND_[roomid]
            b.insert(1, t)
            b.insert(4, c)
            tt = float(b[2])

            if b[0] == 0:  # 关闭空调的请求
                print(roomid, "关闭空调")
                cmd = "insert into " + roomid + " values(now(),"
                cmd = cmd + str(_D_CURS_[roomid]) + ","
                cmd = cmd + str(_D_CURT_[roomid]) + ","
                cmd = cmd + str(_D_TART_[roomid]) + ","
                cmd = cmd + str(_D_WIND_[roomid]) + ","
                cmd = cmd + str(_D_CURC_[roomid]) + ");"
                (db, dbcur) = self.excutecmd(cmd)
                temproomid = roomid[4:]
                msg = str(
                    "L " + str(temproomid) + " " + str(_D_CURS_[roomid]) + " " + str(_D_TART_[roomid]) + " " + str(
                        _D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
                print(msg)
                return msg

            if self.vaildtargett(tt):  # 调节温度合法，直接加入数据库
                cmd = "insert into " + roomid + " values(now(),"
                cmd = cmd + str(_D_CURS_[roomid]) + ","
                cmd = cmd + str(_D_CURT_[roomid]) + ","
                cmd = cmd + str(_D_TART_[roomid]) + ","
                cmd = cmd + str(_D_WIND_[roomid]) + ","
                cmd = cmd + str(_D_CURC_[roomid]) + ");"
                (db, dbcur) = self.excutecmd(cmd)
            else:  # 调节目标不在当前服务模式的调节范围内
                _D_WIND_[roomid] = 0  # 强行停止送风，但不关闭空调
                cmd = "insert into " + roomid + " values(now(),"
                cmd = cmd + str(_D_CURS_[roomid]) + ","
                cmd = cmd + str(_D_CURT_[roomid]) + ","
                cmd = cmd + str(_D_TART_[roomid]) + ","
                cmd = cmd + str(_D_WIND_[roomid]) + ","
                cmd = cmd + str(_D_CURC_[roomid]) + ");"
                (db, dbcur) = self.excutecmd(cmd)
                print("U 更新数据库：", cmd)
                temproomid = roomid[4:]
                msg = str(
                    "U " + str(temproomid) + " " + str(_D_CURS_[roomid]) + " " + str(_D_CURT_[roomid]) + " " + str(
                        _D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
                print(msg, "调节目标不在当前服务模式的调节范围内")
                return msg
            # 执行数据库更新
            (result, ct, tt) = self.cmpcurrentt(db, dbcur, roomid)
            if result == 1:  # 设置目标温度与当前温度一致
                # 将风速改为0
                _D_WIND_[roomid] = 0  # 停止送风
                cmd = "insert into " + roomid + " values(now(),"
                cmd = cmd + str(_D_CURS_[roomid]) + ","
                cmd = cmd + str(_D_CURT_[roomid]) + ","
                cmd = cmd + str(_D_TART_[roomid]) + ","
                cmd = cmd + str(_D_WIND_[roomid]) + ","
                cmd = cmd + str(_D_CURC_[roomid]) + ");"
                (db, dbcur) = self.excutecmd(cmd)
                temproomid = roomid[4:]
                # if str(b[0])=="0":
                #	msg=str("L "+str(roomid)+" 0 "+str(tt)+" "+str(b[3])+" "+str(b[4]))
                # else:
                msg = str("U " + str(temproomid) + " " + str(b[0]) + " " + str(ct) + " " + str(b[3]) + " " + str(b[4]))
                print(msg, "设置目标温度与当前温度一致，停止送风")
                return msg
            else:  # 未达到目标温度，未在调节
                temproomid = roomid[4:]
                # if str(b[0])=="0":
                #	msg=str("L "+str(roomid)+" 0 "+str(tt)+" "+str(b[3])+" "+str(b[4]))
                # else:
                msg = str("C " + str(temproomid) + " " + str(b[0]) + " " + str(tt) + " " + str(b[3]) + " " + str(b[4]))
                print(msg, "未达到目标温度，未在调节")
                return msg

        if a == '1':  # 通告报文
            signal = b[1]  # b=[tar_t,signal]
            print("标志内容：", signal)
            b = b[0:1]
            if signal == 'C':  # 周期通告
                _D_CURT_[roomid] = float(b[0])
                (result, ct, tt) = self.cmpcurrentt(db, dbcur, roomid)
                if result == 1:  # 通过调节到达目标温度
                    temproomid = roomid[4:]
                    b[3] = 0
                    e = 0
                    msg = str("A " + str(temproomid) + " 1 " + str(ct) + " " + str(e) + " " + str(f))
                    print(msg)
                    return msg
                else:  # 未达到目标温度
                    temproomid = roomid[4:]
                    msg = str("C " + str(temproomid) + " 1 " + str(ct) + " " + str(e) + " " + str(f))
                    print(msg)
                    return msg

            if signal == 'D':  # 服务期间
                _D_CURT_[roomid] = float(b[0])
                (result, ct, tt) = self.cmpcurrentt(db, dbcur, roomid)
                if result == 1:  # 设置目标温度与当前温度一致
                    _D_WIND_ = 0  # 停止送风
                    cmd = "insert into " + roomid + " values(now(),"
                    cmd = cmd + str(_D_CURS_[roomid]) + ","
                    cmd = cmd + str(_D_CURT_[roomid]) + ","
                    cmd = cmd + str(_D_TART_[roomid]) + ","
                    cmd = cmd + str(_D_WIND_[roomid]) + ","
                    cmd = cmd + str(_D_CURC_[roomid]) + ");"
                    (db, dbcur) = self.excutecmd(cmd)
                    temproomid = roomid[4:]
                    msg = str(
                        "U " + str(temproomid) + " " + str(_D_CURS_[roomid]) + " " + str(_D_TART_[roomid]) + " " + str(
                            _D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
                    print(msg, "设置目标温度与当前温度一致，已经停止送风")
                    return msg
                else:  # 未达到目标温度，在被服务
                    temproomid = roomid[4:]
                    msg = str(
                        "C " + str(temproomid) + " " + str(_D_CURS_[roomid]) + " " + str(_D_TART_[roomid]) + " " + str(
                            _D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
                    print(msg, "未达到目标温度，在被服务")
                    return msg

    # 比较房间内当前温度和目标温度，是否达到
    def cmpcurrentt(self, db, dbcur, roomid):
        global _D_CURS_
        global _D_CURT_
        global _D_TART_
        global _D_CURC_
        global _D_WIND_
        # cmd="select cur_t,tar_t from "+roomid+" order by time desc limit 1;"
        # (db,dbcur)=excutecmd(db,dbcur,cmd)
        # ct,tt=dbcur.fetchone()
        # ct=float(ct)
        # tt=float(tt)
        tt = _D_TART_[roomid]
        ct = _D_CURT_[roomid]
        print("ct=", ct, "	tt=", tt)
        if ct == tt:  # 已到达温度
            print("房间" + roomid + "已达目标温度")
            return (1, ct, tt)
        else:  # 未到达温度
            print("房间" + roomid + "未达目标温度")
            return (0, ct, tt)
        # client.sendall(bytes("A "+roomid,encoding='utf-8'))

    # 判断调节目标是否在当前模式范围内
    def vaildtargett(self, tt):
        tt = float(tt)
        # print("mubiaowendu:",tt)
        global mode
        if mode == 1:
            if tt >= 16 and tt <= 25:
                return True
            else:
                return False
        else:
            if mode == 0:
                if tt >= 27 and tt <= 30:
                    return True
                else:
                    return False

    # 周期性将所有房间最新信息更新到总表格中
    start_time = datetime.now()

    def update(self, db, dbcur):
        start_time = datetime.now()
        global windagain
        while (1):
            updatelock.acquire()
            try:
                current_time = datetime.now()
                if (current_time - start_time).seconds >= 1:
                    print("最近更新时间：", start_time)
                    self.currentcost(db, dbcur)
                    print("开关状态：", _D_CURS_)
                    print("当前温度：", _D_CURT_)
                    print("目标温度：", _D_TART_)
                    print("当前花费：", _D_CURC_)
                    print("当前风速：", _D_WIND_)
                    print("目标风速：", _D_TARW_)
                    cmd = "select roomid from hotel;"
                    (db, dbcur) = self.excutecmd(cmd)
                    roomlist = dbcur.fetchall()

                    l = []
                    for i in roomlist:
                        for j in i:
                            l.append(str(j))
                    print("当前全部房间：", l)
                    for roomid in l:
                        cmd = "select switch,cur_t,tar_t,w_speed,cur_cost from " + roomid + " order by time desc limit 1;"
                        (db, dbcur) = self.excutecmd(cmd)
                        s, ct, tt, ws, cc = dbcur.fetchone()
                        s = int(s)
                        ct = float(ct)
                        tt = float(tt)
                        ws = int(ws)
                        cc = float(cc) + round(_D_CURC_[roomid], 2)
                        """

                        if s and ws == 0 and (tt - ct >= 1 or ct - tt >= 1):
                            # 仍开空调，不在被服务，但是温差大于1度了
                            windagain.append(roomid)
                        """

                        cmd = "update hotel set switch=" + str(s)
                        cmd = cmd + ",temperature=" + str(ct)
                        cmd = cmd + ",wind=" + str(ws)
                        cmd = cmd + ",cost=" + str(round(cc, 2))
                        cmd = cmd + " where roomid='" + roomid + "';"
                        #print(cmd)
                        self.excutecmd(cmd)
                        if ws != 0:  # 正在被服务
                            smsg = "C " + str(roomid) + " " + str(s) + " " + str(tt) + " " + str(ws) + " " + str(cc)
                        else:  # 当前没有被服务
                            smsg = "C " + str(roomid) + " " + str(s) + " " + str(ct) + " " + str(ws) + " " + str(cc)

                    start_time = current_time
            finally:
                updatelock.release()

    # 计算当前处于服务队列的房间单位时间内的cost
    def currentcost(self, db, dbcur):
        global _D_CURS_
        global _D_CURT_
        global _D_TART_
        global _D_CURC_
        global _D_WIND_
        for roomid, s in _D_CURS_.items():
            if s == 1:
                _D_CURC_[roomid] = round((_D_CURC_[roomid] + _D_WIND_[roomid] * 0.01), 2)
                print(roomid,":费用：",_D_CURC_[roomid])
        return

    # 获取报文第一项房间号，将全数字转化为Room+数字，回传前去掉Room
    def getroomid(self, s):
        s = s.split(" ")
        roomid = "room" + s[0]
        s = s[1:]
        print("roomid:" + roomid)
        temps = ""
        for i in s:
            temps = temps + str(i) + " "

        print("msg:" + temps)
        return (str(roomid), temps)

    """
    # 执行收发报文
    def mainthread(server, max_size):
        while (1):
            # updatelock.acquire()
            # try:
            client, addr = server.accept()
            while (1):
                # update(db,dbcur)
                res_bytes = client.recv(max_size)
                if not res_bytes:
                    break
                res_str = str(res_bytes, encoding='utf-8')
                print("message:" + res_str)
                (roomid, msg) =  (res_str)
                # createtableroom(db,dbcur,roomid)#################0615 14:24
                smsg = str(writerecordroom(db, dbcur, roomid, msg))
                print("返回消息:" + smsg)
                client.sendall(bytes(smsg, encoding='utf-8'))
        # finally:
        #	updatelock.release()
    
        client.close()
        server.close()
    
    
    def setpara():
        global mode
        mode = input("请设置空调运行模式（1-制冷，0-制热）：")
    
    """


"""
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
import core

wind = 0.01
mode = 1  # 运行模式默认为制冷，0为制热
# cost=rate*wind_of_room ps
_D_CURS_ = {}  # 当前开关
_D_CURT_ = {}  # 当前温度
_D_TART_ = {}  # 目标温度
_D_CURC_ = {}  # 当前花费
_D_WIND_ = {}  # 当前风速
_D_TARW_ = {}  # 目标风速

windagain = []
updatelock = threading.Lock()
mainlock = threading.Lock()


# 登陆数据库，选择数据库
def connectdatabase():
    # print("请输入服务器端数据库登陆密码：")
    # psw=input()
    # print("请选择数据库：")
    # dbname=input()
    db = pymysql.connect("localhost", "root", "123456", "airconditioner")
    dbcur = db.cursor()
    return (dbcur, db)


# 执行传入数据库的指令cmd
def excutecmd(db, dbcur, cmd):
    try:
        dbcur.execute(cmd)
        db.commit()
        print(cmd,"执行成功")
    except:
        db.rollback()
        print(cmd, "执行失败")
    # traceback.print_exc()
    return (db, dbcur)


# 创建hotel表，记录所有房间当前情况
def createtablehotel(db, dbcur):
    cmd = "create table if not exists hotel(roomid varchar(8) not null,switch varchar(1),temperature decimal(4,2),wind varchar(1),cost decimal(7,2));"
    (db, dbcur) = excutecmd(db, dbcur, cmd)
    return


# 为每个新出现的房间建表，表格名称为room+房间号
# 初始参数为开机时房间回传的数据
# 即传来第一条请求报文的时候，创建房间
def createtableroom(db, dbcur, roomid, b):
    print("hello here")
    global mode
    global _D_CURS_
    global _D_CURT_
    global _D_TART_
    global _D_CURC_
    global _D_WIND_
    global _D_TARW_
    cmd = "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_NAME='" + roomid + "'"
    (db, dbcur) = excutecmd(db, dbcur, cmd)
    a = dbcur.fetchone()
    print(roomid,"create")
    # 该房间还不存在，需要创建
    if a[0] == 0:
        print("该房间还不存在，需要创建")
        cmd = "create table if not exists "
        cmd = cmd + roomid
        cmd = cmd + " (time datetime not null,"
        cmd = cmd + "switch varchar(1),cur_t decimal(4,2),tar_t decimal(4,2),"
        # cmd=cmd+"w_speed varchar(1),cur_cost decimal(7,2),primary key(time));"
        cmd = cmd + "w_speed varchar(1),cur_cost decimal(7,2));"
        (db, dbcur) = excutecmd(db, dbcur, cmd)
        cmd = "insert into " + roomid + " values"
        cmd = cmd + "(now()," + str(int(b[0])) + ",26.00," + str(float(b[1])) + "," + str(int(b[2])) + ",0);"
        (db, dbcur) = excutecmd(db, dbcur, cmd)
        print(cmd)
        cmd = "insert into hotel values('" + roomid + "'," + str(int(b[0])) + ",26.00," + str(int(b[2])) + ",0);"
        (db, dbcur) = excutecmd(db, dbcur, cmd)
        print(cmd)
        _D_CURS_[roomid] = int(b[0])
        _D_CURT_[roomid] = 26.00
        _D_TART_[roomid] = float(b[1])
        _D_CURC_[roomid] = 0
        _D_WIND_[roomid] = int(b[2])
        _D_TARW_[roomid] = _D_WIND_[roomid]
    return


# 将消息内容（调节请求或当前状态）存入房间表格
def writerecordroom(db, dbcur, roomid, s):
    global windagain
    global _D_CURS_
    global _D_CURT_
    global _D_TART_
    global _D_CURC_
    global _D_WIND_
    global _D_TARW_
    if roomid in windagain:
        temproomid = roomid[4:]
        msg = str(
            "0 " + str(temproomid) + " 1 " + str(float(_D_TART_[roomid])) + " " + str(_D_WIND_[roomid]) + " " + str(
                _D_CURC_[roomid]))
        print(msg, "该房间需要回温")
        windagain.remove(roomid)
        # 先处理新的传入报文，再将是否回送风的信息传回，有问题####################
        writerecordroom(db, dbcur, roomid, s)
        return msg

    s = s.rstrip()
    s = s.split(" ")
    a = s[0]
    print("报文类型：", a)
    b = s[1:]
    print("报文内容：", b)
    createtableroom(db, dbcur, roomid, b)  # b=[switch,tar_t,wind]
    if a == '0':  # 请求报文
        # 判断房间是否已经创建
        cmd = "select cur_t,cur_cost from " + roomid + " order by time desc limit 1;"
        (db, dbcur) = excutecmd(db, dbcur, cmd)
        t, c = dbcur.fetchone()
        t = float(t)
        c = float(c)
        _D_CURS_[roomid] = int(b[0])
        _D_CURT_[roomid] = round(float(t), 2)
        _D_CURC_[roomid] = round(c + _D_CURC_[roomid], 2)
        _D_WIND_[roomid] = int(b[2])
        _D_TART_[roomid] = round(float(b[1]), 2)
        _D_TARW_[roomid] = _D_WIND_[roomid]
        b.insert(1, t)
        b.insert(4, c)
        tt = float(b[2])

        if b[0] == 0:  # 关闭空调的请求
            print(roomid, "关闭空调")
            cmd = "insert into " + roomid + " values(now(),"
            cmd = cmd + str(_D_CURS_[roomid]) + ","
            cmd = cmd + str(_D_CURT_[roomid]) + ","
            cmd = cmd + str(_D_TART_[roomid]) + ","
            cmd = cmd + str(_D_WIND_[roomid]) + ","
            cmd = cmd + str(_D_CURC_[roomid]) + ");"
            (db, dbcur) = excutecmd(db, dbcur, cmd)
            print(cmd)
            (db, dbcur) = excutecmd(db, dbcur, cmd)
            temproomid = roomid[4:]
            msg = str("L " + str(temproomid) + " " + str(_D_CURS_[roomid]) + " " + str(_D_TART_[roomid]) + " " + str(
                _D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
            print(msg)
            return msg

        if vaildtargett(tt):  # 调节温度合法，直接加入数据库
            cmd = "insert into " + roomid + " values(now(),"
            cmd = cmd + str(_D_CURS_[roomid]) + ","
            cmd = cmd + str(_D_CURT_[roomid]) + ","
            cmd = cmd + str(_D_TART_[roomid]) + ","
            cmd = cmd + str(_D_WIND_[roomid]) + ","
            cmd = cmd + str(_D_CURC_[roomid]) + ");"
            (db, dbcur) = excutecmd(db, dbcur, cmd)
        else:  # 调节目标不在当前服务模式的调节范围内
            _D_WIND_[roomid] = 0  # 强行停止送风，但不关闭空调
            cmd = "insert into " + roomid + " values(now(),"
            cmd = cmd + str(_D_CURS_[roomid]) + ","
            cmd = cmd + str(_D_CURT_[roomid]) + ","
            cmd = cmd + str(_D_TART_[roomid]) + ","
            cmd = cmd + str(_D_WIND_[roomid]) + ","
            cmd = cmd + str(_D_CURC_[roomid]) + ");"
            (db, dbcur) = excutecmd(db, dbcur, cmd)
            print("U 更新数据库：", cmd)
            temproomid = roomid[4:]
            msg = str("U " + str(temproomid) + " " + str(_D_CURS_[roomid]) + " " + str(_D_CURT_[roomid]) + " " + str(
                _D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
            print(msg, "调节目标不在当前服务模式的调节范围内")
            return msg
        # 执行数据库更新
        (result, ct, tt) = cmpcurrentt(db, dbcur, roomid)
        if result == 1:  # 设置目标温度与当前温度一致
            # 将风速改为0
            _D_WIND_[roomid] = 0  # 停止送风
            cmd = "insert into " + roomid + " values(now(),"
            cmd = cmd + str(_D_CURS_[roomid]) + ","
            cmd = cmd + str(_D_CURT_[roomid]) + ","
            cmd = cmd + str(_D_TART_[roomid]) + ","
            cmd = cmd + str(_D_WIND_[roomid]) + ","
            cmd = cmd + str(_D_CURC_[roomid]) + ");"
            (db, dbcur) = excutecmd(db, dbcur, cmd)
            temproomid = roomid[4:]
            # if str(b[0])=="0":
            #	msg=str("L "+str(roomid)+" 0 "+str(tt)+" "+str(b[3])+" "+str(b[4]))
            # else:
            msg = str("U " + str(temproomid) + " " + str(b[0]) + " " + str(ct) + " " + str(b[3]) + " " + str(b[4]))
            print(msg, "设置目标温度与当前温度一致，停止送风")
            return msg
        else:  # 未达到目标温度，未在调节
            temproomid = roomid[4:]
            # if str(b[0])=="0":
            #	msg=str("L "+str(roomid)+" 0 "+str(tt)+" "+str(b[3])+" "+str(b[4]))
            # else:
            msg = str("C " + str(temproomid) + " " + str(b[0]) + " " + str(tt) + " " + str(b[3]) + " " + str(b[4]))
            print(msg, "未达到目标温度，未在调节")
            return msg

    if a == '1':  # 通告报文
        signal = b[1]  # b=[tar_t,signal]
        print("标志内容：", signal)
        b = b[0:1]
        if signal == 'C':  # 周期通告
            _D_CURT_[roomid] = float(b[0])
            (result, ct, tt) = cmpcurrentt(db, dbcur, roomid)
            if result == 1:  # 通过调节到达目标温度
                temproomid = roomid[4:]
                b[3] = 0
                e = 0
                msg = str("A " + str(temproomid) + " 1 " + str(ct) + " " + str(e) + " " + str(f))
                print(msg)
                return msg
            else:  # 未达到目标温度
                temproomid = roomid[4:]
                msg = str("C " + str(temproomid) + " 1 " + str(ct) + " " + str(e) + " " + str(f))
                print(msg)
                return msg

        if signal == 'D':  # 服务期间
            _D_CURT_[roomid] = float(b[0])
            (result, ct, tt) = cmpcurrentt(db, dbcur, roomid)
            if result == 1:  # 设置目标温度与当前温度一致
                _D_WIND_ = 0  # 停止送风
                cmd = "insert into " + roomid + " values(now(),"
                cmd = cmd + str(_D_CURS_[roomid]) + ","
                cmd = cmd + str(_D_CURT_[roomid]) + ","
                cmd = cmd + str(_D_TART_[roomid]) + ","
                cmd = cmd + str(_D_WIND_[roomid]) + ","
                cmd = cmd + str(_D_CURC_[roomid]) + ");"
                (db, dbcur) = excutecmd(db, dbcur, cmd)
                temproomid = roomid[4:]
                msg = str(
                    "U " + str(temproomid) + " " + str(_D_CURS_[roomid]) + " " + str(_D_TART_[roomid]) + " " + str(
                        _D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
                print(msg, "设置目标温度与当前温度一致，已经停止送风")
                return msg
            else:  # 未达到目标温度，在被服务
                temproomid = roomid[4:]
                msg = str(
                    "C " + str(temproomid) + " " + str(_D_CURS_[roomid]) + " " + str(_D_TART_[roomid]) + " " + str(
                        _D_WIND_[roomid]) + " " + str(_D_CURC_[roomid]))
                print(msg, "未达到目标温度，在被服务")
                return msg


# 比较房间内当前温度和目标温度，是否达到
def cmpcurrentt(db, dbcur, roomid):
    global _D_CURS_
    global _D_CURT_
    global _D_TART_
    global _D_CURC_
    global _D_WIND_
    # cmd="select cur_t,tar_t from "+roomid+" order by time desc limit 1;"
    # (db,dbcur)=excutecmd(db,dbcur,cmd)
    # ct,tt=dbcur.fetchone()
    # ct=float(ct)
    # tt=float(tt)
    tt = _D_TART_[roomid]
    ct = _D_CURT_[roomid]
    print("ct=", ct, "	tt=", tt)
    if ct == tt:  # 已到达温度
        print("房间" + roomid + "已达目标温度")
        return (1, ct, tt)
    else:  # 未到达温度
        print("房间" + roomid + "未达目标温度")
        return (0, ct, tt)
    # client.sendall(bytes("A "+roomid,encoding='utf-8'))


# 判断调节目标是否在当前模式范围内
def vaildtargett(tt):
    tt = float(tt)
    # print("mubiaowendu:",tt)
    global mode
    if mode == 1:
        if tt >= 16 and tt <= 25:
            return True
        else:
            return False
    else:
        if mode == 0:
            if tt >= 27 and tt <= 30:
                return True
            else:
                return False


# 周期性将所有房间最新信息更新到总表格中
start_time = datetime.now()


def update(db, dbcur):
    start_time = datetime.now()
    global windagain
    while (1):
        updatelock.acquire()
        try:
            current_time = datetime.now()
            if (current_time - start_time).seconds >= 1:
                print("最近更新时间：", start_time)
                currentcost(db, dbcur)
                print("开关状态：", _D_CURS_)
                print("当前温度：", _D_CURT_)
                print("目标温度：", _D_TART_)
                print("当前花费：", _D_CURC_)
                print("当前风速：", _D_WIND_)
                print("目标风速：", _D_TARW_)
                cmd = "select roomid from hotel;"
                (db, dbcur) = excutecmd(db, dbcur, cmd)
                roomlist = dbcur.fetchall()

                l = []
                for i in roomlist:
                    for j in i:
                        l.append(str(j))
                print("当前全部房间：", l)
                for roomid in l:
                    cmd = "select switch,cur_t,tar_t,w_speed,cur_cost from " + roomid + " order by time desc limit 1;"
                    (db, dbcur) = excutecmd(db, dbcur, cmd)
                    s, ct, tt, ws, cc = dbcur.fetchone()
                    s = int(s)
                    ct = float(ct)
                    tt = float(tt)
                    ws = int(ws)
                    cc = float(cc) + round(_D_CURC_[roomid], 2)

                    if s and ws == 0 and (tt - ct >= 1 or ct - tt >= 1):
                        # 仍开空调，不在被服务，但是温差大于1度了
                        windagain.append(roomid)

                    cmd = "update hotel set switch=" + str(s)
                    cmd = cmd + ",temperature=" + str(ct)
                    cmd = cmd + ",wind=" + str(ws)
                    cmd = cmd + ",cost=" + str(round(cc, 2))
                    cmd = cmd + " where roomid='" + roomid + "';"
                    print(cmd)
                    excutecmd(db, dbcur, cmd)
                    if ws != 0:  # 正在被服务
                        smsg = "C " + str(roomid) + " " + str(s) + " " + str(tt) + " " + str(ws) + " " + str(cc)
                    else:  # 当前没有被服务
                        smsg = "C " + str(roomid) + " " + str(s) + " " + str(ct) + " " + str(ws) + " " + str(cc)

                start_time = current_time
        finally:
            updatelock.release()


# 计算当前处于服务队列的房间单位时间内的cost
def currentcost(db, dbcur):
    global _D_CURS_
    global _D_CURT_
    global _D_TART_
    global _D_CURC_
    global _D_WIND_
    for roomid, s in _D_CURS_.items():
        if s == 1:
            _D_CURC_[roomid] = round(_D_CURC_[roomid] + _D_WIND_[roomid] * wind, 2)
    return


# 获取报文第一项房间号，将全数字转化为Room+数字，回传前去掉Room
def getroomid(s):
    s = s.split(" ")
    roomid = "room" + s[0]
    s = s[1:]
    print("roomid:" + roomid)
    temps = ""
    for i in s:
        temps = temps + str(i) + " "

    print("msg:" + temps)
    return (str(roomid), temps)

"""
"""
# 执行收发报文
def mainthread(server, max_size):
    while (1):
        # updatelock.acquire()
        # try:
        client, addr = server.accept()
        while (1):
            # update(db,dbcur)
            res_bytes = client.recv(max_size)
            if not res_bytes:
                break
            res_str = str(res_bytes, encoding='utf-8')
            print("message:" + res_str)
            (roomid, msg) =  (res_str)
            # createtableroom(db,dbcur,roomid)#################0615 14:24
            smsg = str(writerecordroom(db, dbcur, roomid, msg))
            print("返回消息:" + smsg)
            client.sendall(bytes(smsg, encoding='utf-8'))
    # finally:
    #	updatelock.release()

    client.close()
    server.close()


def setpara():
    global mode
    mode = input("请设置空调运行模式（1-制冷，0-制热）：")

"""
