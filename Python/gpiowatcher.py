try:
    import RPi.GPIO as GPIO
except:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using sudo to run your script")
    pass
	
import time
import urllib2
import socket, struct, fcntl
import os
import datetime
import configparser

print("Waiting 30 sec for network to fully load..")
time.sleep(30)

config = configparser.ConfigParser()
config.read('gpiowatcher.ini')

serverConfig = config['SERVER']

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd = sock.fileno()
SIOCGIFADDR = 0x8915

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))
    
def get_ip(iface = 'eth0'):
     ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00'*14)
     try:
         res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
     except:
         return None
     ip = struct.unpack('16sH2x4s8x', res)[2]
     return socket.inet_ntoa(ip)
	 
def poststate(inputnumber, state):
    response = urllib2.urlopen(serverConfig['host'].format(serverConfig['serialnumber'],inputnumber,state))
    print("{} - State sent Monitor:{} - State:{}".format(time.strftime("%Y-%m-%d %H:%M:%S"),inputnumber,state))
	 
def postkeyvalue(key, value):
    response = urllib2.urlopen(serverConfig['host'].format(serverConfig['serialnumber'],key,value))
    print("{} - Key value post Key:{} - Value:{}".format(time.strftime("%Y-%m-%d %H:%M:%S"),key,value))

def postkey(key):
    response = urllib2.urlopen(serverConfig['keypost'].format(serverConfig['serialnumber'],key))
    print("{} - KEy post: {}".format(time.strftime("%Y-%m-%d %H:%M:%S"),key))

GPIO.setmode(GPIO.BOARD)
mode = GPIO.getmode()
print("Mode:{}".format(mode))

postkey('start')
postkeyvalue('ip',  get_ip('wlan0'))
postkeyvalue('cputemp',  getCPUtemperature())

count = 0
oldout = 0
oldhome = 0

starttime = time.time()

gpiolist[0] = 0 
gpiolist[1] = 1 
gpiolist[2] = 2 
gpiolist[3] = 3 
gpiolist[4] = 4 
gpiolist[5] = 5 
gpiolist[6] = 6 
gpiolist[7] = 7 
gpiolist[8] = 8 
gpiolist[9] = 9 
gpiolist[10] = 10
gpiolist[11] = 11
gpiolist[12] = 12
gpiolist[13] = 13
gpiolist[14] = 14
gpiolist[15] = 15
gpiolist[16] = 16
gpiolist[17] = 21
gpiolist[18] = 22
gpiolist[20] = 23
gpiolist[21] = 24
gpiolist[22] = 25
gpiolist[23] = 26
gpiolist[24] = 27
gpiolist[25] = 28
gpiolist[26] = 29

for e in gpiolist:
	GPIO.setup(e, GPIO.IN)


while True:
	try:

		for e in gpiolist:
			if (state[e] != GPIO.input(e)):
				countList[e] = countList[e] + 1

		for e in countList:
			if (e > 5):
				countList[e] = 0
				state[e] = GPIO.input(e)			
				if (state[e] == 1):	
					poststate(e,'1')
				else:
					poststate(e,'0')
    
		if ((time.time() - starttime) > 3600):
			starttime = time.time()
			postkey('keepalive')
			postkeyvalue('cputemp',  getCPUtemperature())
    
		time.sleep(1)

	except RuntimeError:
		print("Exception")
