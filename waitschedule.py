from socketserver import BaseRequestHandler,ThreadingTCPServer,ForkingTCPServer
import threading
import socket
#import sys
import modulefinder
import send
import schedule
import ast
import json
import core
from datetime import date, time, datetime, timedelta
"""
class waitschedule():
  def runTask(self):
       while True:
        # 找WAITLIST里面
        if core.waitlist.__len__() == 0:
            continue

        core.servicelist = sorted(core.servicelist, key=lambda e: e.__getitem__('servicetime'),
                                  reverse=True)  # 以最大值排序，即最早
        core.servicelist = sorted(core.servicelist, key=lambda e: e.__getitem__('wind'),
                                  reverse=False)  # 以最小值排序，即最小风

        num=min(core.waitlist.__len__(),5)
        for k in range(num):
            if  core.waitlist[0]['waittime'] == 0:  # 1 mins
                core.waitlist.append(core.servicelist[0])
                core.servicelist.remove(core.servicelist[0])
                core.servicelist[0]['waittime'] = 0
                core.servicelist[0]['servicetime'] = 0
                core.waitlist[k]['waittime'] = 60
                core.waitlist[k]['servicetime'] = 0
                core.servicelist.append(core.waitlist[k])
                core.waitlist.remove(core.waitlist[k])
                core.servicelist = sorted(core.servicelist, key=lambda e: e.__getitem__('servicetime'),
                                          reverse=True)  # 以最大值排序，即最早
                core.servicelist = sorted(core.servicelist, key=lambda e: e.__getitem__('wind'),
                                          reverse=False)  # 以最小值排序，即最小风
            else:
                break
"""