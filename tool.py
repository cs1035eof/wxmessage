# -*- coding:utf-8 -*-

__author__ = 'Furnace'

import crcmod
import crcmod.predefined
import json
import redis

class CRCTool:
    def __init__(self):
        self.crc16 = crcmod.predefined.Crc('crc-16-mcrf4xx')
        pass
	
    def get_value(self, message):
        message = message.encode('utf-8')
        self.crc16.update(message)
        value = self.crc16.hexdigest()
        return value
        #return ''
		
class RedisTool:
    def __init__(self, ipaddr, port, dbno):
        self.ipaddr = ipaddr
        self.port = port
        self.dbno = dbno
        self.conn = redis.Redis(host=ipaddr, port=port, db=dbno)
		
    def get_conn(self):
        return self.conn
        
if __name__ == '__main__':
    # conf = json.loads('{"ipaddr" : "192.168.20.50", "port" : 6379, "dbno" : 9}')
    # print(conf)
    # print(conf['ipaddr'])
    # print(conf['port'])
    # print(conf['dbno'])
	
    with open("conf.json",'r') as conf_file:
        conf = json.load(conf_file)
        # print(conf)
        # print(conf['ipaddr'])
        # print(conf['port'])
        # print(conf['dbno'])
	
    ipaddr = conf['ipaddr']
    port = conf['port']
    dbno = conf['dbno']
	
    # redis_tool = RedisTool("192.168.20.50", 6379, 9)
    redis_tool = RedisTool(ipaddr, port, dbno)
    conn = redis_tool.get_conn()
    print( conn.ping() )
    # print( conn.info() )
	
    crc_tool = CRCTool()
    crc_value = crc_tool.get_value('abc')
    print('crc_value = ', crc_value)
