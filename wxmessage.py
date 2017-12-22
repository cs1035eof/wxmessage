# -*- coding:utf-8 -*-

__author__ = 'Furnace'

from apscheduler.schedulers.background import BackgroundScheduler

import datetime as dt
import itchat
import json
import random
import redis
import time
import tool

debug = True
# debug = False

MSG_LENGTH = 10
INCR = 10

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
#timeList.append(12 * 3600 + 15 * 60 + 3)
#timeList.append(13 * 3600 + 15 * 60 + 3)
timeList.append(14 * 3600 + 15 * 60 + 55)
timeList.append(15 * 3600 + 15 * 60 + 40)
timeList.append(16 * 3600 + 15 * 60 + 51)
timeList.append(17 * 3600 + 15 * 60 + 19)
timeList.append(18 * 3600 + 18 * 60 + 32)
timeList.append(19 * 3600 + 47 * 60 + 48)
timeList.append(20 * 3600 + 46 * 60 + 30)
timeList.append(21 * 3600 + 14 * 60 + 50)
timeList.append(22 * 3600 + 15 * 60 + 10)
#timeList.append(23 * 3600 + 56 * 60 + 10)
timeList.sort(reverse=True)
# print(timeList)

class WxMessage(object):
    def __init__(self):
        self.msgDefault = u'暂时没有新的消息'
        self.friendNameListDefault = ['wxrobottest']
        self.msgQueue = []
		
        self.crcTool = tool.CRCTool()

        # load conf.json 
        with open("conf.json",'r') as conf_file:
            conf = json.load(conf_file)
	
        self.ipaddr = conf['ipaddr']
        self.port = conf['port']
        self.dbno = conf['dbno']
        # print('ipaddr = ', self.ipaddr)
        # print('port = ', self.port)
        # print('dbno = ', self.dbno)
	
        redis_tool = tool.RedisTool(self.ipaddr, self.port, self.dbno)
        self.conn = redis_tool.get_conn()
        # print('Is connected to Redis: ', self.conn.ping() )
        if not self.conn.ping():
            print('Is connected to Redis: ', self.conn.ping() )
            return
		
        self.index = self.conn.get('index')
        if not self.index:
            self.index = 0
        self.index = int(self.index)
        #print('index = ', self.index)

    # 获取下一次的问候时间
    def get_next_tick_time(self, srcTime):
        if debug:
            return srcTime + dt.timedelta(seconds=30)
		
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
		
    def get_friend_name_list(self):
        friendNameList = self.conn.lrange('friend_name_list', 0, -1)
        if len(friendNameList) <= 0:
            return self.friendNameListDefault
	
        return friendNameList

    def update_msg_queue(self, incr):
        msgQueueTmp = self.conn.lrange('message_pool', self.index, self.index + incr)
	
        msgLength = len(msgQueueTmp)
        #print('msgLength', msgLength)
		
        for msg in msgQueueTmp:
            self.msgQueue.append(msg)
		
        if msgLength > 0:
            self.index += msgLength
            self.conn.set('index', self.index)
		
        # print('index = ', self.index)
        # print('length = ', len(self.msgQueue))

    def get_msg(self):
        if len(self.msgQueue) <= MSG_LENGTH:
            self.update_msg_queue(INCR)
	
        if len(self.msgQueue) <= 0:
            return self.msgDefault
	
        msg = self.msgQueue[0].decode('utf-8')
        del self.msgQueue[0]
		
        # print('msg = ', msg)
        # print('len = ', len(self.msgQueue))
	
        #msgCrc = self.crcTool.get_value(msg)
        #self.conn.rpush('message_send', msgCrc)
	
        return msg

    def tick(self):
        friendNameList = self.get_friend_name_list()
        # print('friendNameList = ', friendNameList)
		
        if len(friendNameList) <= 0:
            print('friendNameList is null.')
			
        greeting = self.get_msg()
        print('greeting = ', greeting)
    	
        for friendName in friendNameList:
            # friendName = unicode(friendName, 'utf-8')	# python 2
            friendName = friendName.decode('utf-8').replace('\n', '')		# python 3
            print('friendName = ', friendName)
            users = itchat.search_friends(name=friendName)
            # print('users = ', users)
            for user in users:
                userName = user['UserName']
                print('\a')
                itchat.send(u'%s'%(greeting), toUserName=userName)
    	
        time.sleep(1)
        nowTime = dt.datetime.now()
        nextTickTime = self.get_next_tick_time(nowTime)
        print('nextTickTime = %s' % dt.datetime.strftime(nextTickTime, '%Y-%m-%d %H:%M:%S'))
        self.msg_send_scheduler(nextTickTime)

    def msg_send_scheduler(self, runTime):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.tick, 'date', run_date=runTime)
        scheduler.start()

    def run(self):
        if not self.conn.ping():
            print('Is connected to Redis: ', self.conn.ping() )
            return
		
        itchat.auto_login(hotReload=True)
	
        nowTime = dt.datetime.now()
        nextTickTime = self.get_next_tick_time(nowTime)
        print('nextTickTime = %s' % dt.datetime.strftime(nextTickTime, '%Y-%m-%d %H:%M:%S'))
   
        self.msg_send_scheduler(nextTickTime)
	
        itchat.run()
	
if __name__ == '__main__':
    wx = WxMessage()
    wx.run()
