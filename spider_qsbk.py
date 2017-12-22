# -*- coding:utf-8 -*-

__author__ = 'Furnace'

from fake_useragent import UserAgent
import json
import re
import requests
import time
import tool

MAX_POOL_SIZE = 10000

class SpiderQSBK(object):
    def __init__(self):	
        self.crc_tool = tool.CRCTool()
		
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
			
        self.last_hot_msg_update_timestamp = self.conn.get('last_hot_msg_update_timestamp')
        if not self.last_hot_msg_update_timestamp:
            self.last_hot_msg_update_timestamp = 0
        self.interval = 5 * 60		# 5 minutes
		
        print('self.last_hot_msg_update_timestamp = ', self.last_hot_msg_update_timestamp)
        print('self.interval = ', self.interval)
		
        self.length = self.conn.llen('message_pool')
        print('self.length = ', self.length)
		
        ua = UserAgent()
        self.headers = {'UserAgent' : 'us.random'}
        self.page = 1
        self.domain = 'http://www.qiushibaike.com/hot/page/'
        self.domain_text = 'https://www.qiushibaike.com/text/page/'
	
    def update_text_msg(self, url):
        if self.length >= MAX_POOL_SIZE:
            return
	
        response = requests.get(url, headers=self.headers, timeout=10)
        # print('url = ', url)
        content = response.text
        # print('111')
		
        pattern = re.compile('<div.*?class="author clearfix">.*?<a.*?<img.*?>.*?</a>.*?<h2>(.*?)</h2>.*?</a>.*?<div.*?'+
                             'class="content">.*?<span>(.*?)</span>.*?</div>.*?</a>(.*?)<div class="stats.*?class="number">(.*?)</i>',re.S)
		
        # print('222')					 
        items = re.findall(pattern,content)
        print('items number = ', len(items) )
		
        for item in items:
            haveImg = re.search("img",item[2])
            if not haveImg:
                # print( item[0],item[1],item[3] )
                msg = item[1]
                msg = msg.replace('<br/>', '').strip()
                # print('msg = ', msg)
				
                msg_crc = self.crc_tool.get_value(msg)
                # print('msg_crc = ', msg_crc)
                exist = self.conn.sismember('message_pool_crc', msg_crc)
                if exist :
                    # print('msg_crc ', msg_crc, 'is exist.')
                    continue
				
                self.conn.rpush('message_pool', msg)
                self.conn.sadd('message_pool_crc', msg_crc)
				
                self.length += 1
	
    def update_hot_msg(self, url):
        if self.length >= MAX_POOL_SIZE:
            return
			
        response = requests.get(url, headers=self.headers)
        content = response.text
		
        pattern = re.compile('<div.*?class="author clearfix">.*?<a.*?<img.*?>.*?</a>.*?<h2>(.*?)</h2>.*?</a>.*?<div.*?'+
                             'class="content">.*?<span>(.*?)</span>.*?</div>.*?</a>(.*?)<div class="stats.*?class="number">(.*?)</i>',re.S)
							 
        items = re.findall(pattern,content)
        print('items number = ', len(items) )
		
        for item in items:
            haveImg = re.search("img",item[2])
            if not haveImg:
                # print( item[0],item[1],item[3] )
                msg = item[1]
                msg = msg.replace('<br/>', '').strip()
                # print('msg = ', msg)
				
                msg_crc = self.crc_tool.get_value(msg)
                # print('msg_crc = ', msg_crc)
                exist = self.conn.sismember('message_pool_crc', msg_crc)
                if exist :
                    # print('msg_crc ', msg_crc, 'is exist.')
                    continue
				
                self.conn.rpush('message_pool', msg)
                self.conn.sadd('message_pool_crc', msg_crc)
				
                self.length += 1
	
    def run(self):
        if not self.conn.ping():
            print('Is connected to Redis: ', self.conn.ping() )
            return
		
        for i in range(13, 14):
        # for i in range(1, 14):
            url = self.domain_text + str(i)
            print('text_url = ', url)
            self.update_text_msg(url)
            time.sleep(10)
		
        while True:
            timestamp = int( time.time() )
            # print('timestamp =', timestamp)
            if timestamp < int(self.last_hot_msg_update_timestamp) + int(self.interval):
                time.sleep(10)
                continue
			
            url = self.domain + str(self.page)
            print('hot_url = ', url)
            self.update_hot_msg(url)
			
            self.last_hot_msg_update_timestamp = timestamp
            self.conn.set('last_hot_msg_update_timestamp', self.last_hot_msg_update_timestamp)
            # print('self.last_hot_msg_update_timestamp =', self.last_hot_msg_update_timestamp)
			
if __name__ == '__main__':
    spider = SpiderQSBK()
    spider.run()
