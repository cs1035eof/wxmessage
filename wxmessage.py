# -*- coding:utf-8 -*-

__author__ = 'Furnace'

from apscheduler.schedulers.background import BackgroundScheduler

import datetime as dt
import itchat
import random
import redis
import time
import tool

IPADDR = 'localhost'
#IPADDR = '192.168.1.180'
PORT = 6379
DBNO = 10

MSG_LENGTH = 10
INCR = 10

msgDefault = u'暂时没有新的消息'
friendNameListDefault = ['wxrobottest']

conn = redis.Redis(host=IPADDR, port=PORT, db=DBNO)
print( conn.ping() )

msgQueue = []

crcTool = tool.CRCTool()

def get_friend_name_list():
    friendNameList = conn.lrange('friend_name_list', 0, -1)
    if len(friendNameList) <= 0:
        return friendNameListDefault
	
    return friendNameList

def update_msg_queue(incr):
    msgQueueTmp = conn.lrange('message_pool', 0, incr)
    print( u'type(msgQueueTmp) = %s' % type(msgQueueTmp) )
	
    msgLength = len(msgQueueTmp)
    conn.ltrim('message_pool', 0, msgLength)
	
    msgQueue = msgQueueTmp

def get_msg():
    if len(msgQueue) <= MSG_LENGTH:
        update_msg_queue(INCR)
	
    if len(msgQueue) <= 0:
        return msgDefault
	
    msg = msgQueue[0]
    del msgQueue[0]
	
    msgCrc = crcTool.get_value(msg)
    conn.rpush('message_send', msgCrc)
	
    return msg

# 问候时间列表
timeList = []
#timeList.append(0 * 3600 + 34 * 60 + 0)
#timeList.append(1 * 3600 + 15 * 60 + 22)
#timeList.append(2 * 3600 + 15 * 60 + 22)
#timeList.append(3 * 3600 + 15 * 60 + 22)
#timeList.append(4 * 3600 + 15 * 60 + 22)
#timeList.append(5 * 3600 + 15 * 60 + 22)
#timeList.append(6 * 3600 + 15 * 60 + 22)
#timeList.append(7 * 3600 + 15 * 60 + 22)
timeList.append(8 * 3600 + 15 * 60 + 22)
timeList.append(9 * 3600 + 15 * 60 + 37)
timeList.append(10 * 3600 + 15 * 60 + 11)
timeList.append(11 * 3600 + 15 * 60 + 3)
timeList.append(14 * 3600 + 15 * 60 + 55)
timeList.append(15 * 3600 + 15 * 60 + 40)
timeList.append(16 * 3600 + 15 * 60 + 51)
timeList.append(17 * 3600 + 15 * 60 + 19)
timeList.append(18 * 3600 + 15 * 60 + 32)
timeList.append(19 * 3600 + 15 * 60 + 48)
timeList.append(20 * 3600 + 15 * 60 + 30)
timeList.append(21 * 3600 + 15 * 60 + 20)
timeList.append(22 * 3600 + 15 * 60 + 10)
#timeList.append(23 * 3600 + 15 * 60 + 22)
timeList.sort(reverse=True)
# print(timeList)

# 获取下一次的问候时间
def get_next_tick_time(srcTime):
    lenList = len(timeList)
    if lenList < 1:
        return srcTime + dt.timedelta(hours=1)
	
    timeListStart = timeList[lenList - 1]
    timeListFinish = timeList[0]
	
    total_sec = srcTime.hour * 3600 + srcTime.minute * 60 + srcTime.second
    nextTime = srcTime - dt.timedelta(seconds=total_sec)
    print('total_sec = %d' % total_sec)
    print(dt.datetime.strftime(nextTime, '%Y-%m-%d %H:%M:%S'))	
	
    if total_sec > timeListFinish:
        nextTime += dt.timedelta(days=1)
        nextTime += dt.timedelta(seconds=timeListStart)
        return nextTime

    i = 1
    while i < lenList:
        print('i=%d' % i)
        if total_sec > timeList[i]:
            nextTime += dt.timedelta(seconds=timeList[i - 1])
			
            return nextTime
        else:
            i += 1

    return nextTime + dt.timedelta(seconds=timeListStart)

def tick():
    friendNameList = get_friend_name_list()
	
    for friendName in friendNameList:
        users = itchat.search_friends(name=friendName)
        for user in users:
            userName = user['UserName']
            greeting = get_msg()
            print('\a')
            itchat.send(u'%s'%(greeting), toUserName=userName)
	
    time.sleep(1)
    nowTime = dt.datetime.now()
    nextTickTime = get_next_tick_time(nowTime)
    print('nextTickTime = %s' % dt.datetime.strftime(nextTickTime, '%Y-%m-%d %H:%M:%S'))
    msg_send_scheduler(nextTickTime)

def msg_send_scheduler(runTime):
    scheduler = BackgroundScheduler()
    scheduler.add_job(tick, 'date', run_date=runTime)
    scheduler.start()

if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
	
    nowTime = dt.datetime.now()
    nextTickTime = get_next_tick_time(nowTime)
    print('nextTickTime = %s' % dt.datetime.strftime(nextTickTime, '%Y-%m-%d %H:%M:%S'))
   
    msg_send_scheduler(nextTickTime)
	
    itchat.run()
