import crcmod
import crcmod.predefined

STX = b'\x02'
ETX = b'\x03'
data = b'G18M1314D4417,2511165'
message = STX + data + ETX

crc16 = crcmod.predefined.Crc('crc-16-mcrf4xx')
crc16.update(message)
crc = crc16.hexdigest()
print(crc)

message = u'你好啊我的朋友'
message = message.encode('utf-8')
crc16.update(message)
crc = crc16.hexdigest()
print(crc)