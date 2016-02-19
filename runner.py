# magic comment to allow russian bukvs
# coding=UTF8

'''

За основу взяты скрипы с сервера "ТЕЛЕОФИС"

==================================
Copyright (c) 2013, ОАО "ТЕЛЕОФИС"

Разрешается повторное распространение и использование как в виде исходного кода, так и в двоичной форме, 
с изменениями или без, при соблюдении следующих условий:

- При повторном распространении исходного кода должно оставаться указанное выше уведомление об авторском праве, 
  этот список условий и последующий отказ от гарантий.
- При повторном распространении двоичного кода должна сохраняться указанная выше информация об авторском праве, 
  этот список условий и последующий отказ от гарантий в документации и/или в других материалах, поставляемых 
  при распространении.
- Ни название ОАО "ТЕЛЕОФИС", ни имена ее сотрудников не могут быть использованы в качестве поддержки или 
  продвижения продуктов, основанных на этом ПО без предварительного письменного разрешения.

ЭТА ПРОГРАММА ПРЕДОСТАВЛЕНА ВЛАДЕЛЬЦАМИ АВТОРСКИХ ПРАВ И/ИЛИ ДРУГИМИ СТОРОНАМИ «КАК ОНА ЕСТЬ» БЕЗ КАКОГО-ЛИБО 
ВИДА ГАРАНТИЙ, ВЫРАЖЕННЫХ ЯВНО ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ИМИ, ПОДРАЗУМЕВАЕМЫЕ ГАРАНТИИ 
КОММЕРЧЕСКОЙ ЦЕННОСТИ И ПРИГОДНОСТИ ДЛЯ КОНКРЕТНОЙ ЦЕЛИ. НИ В КОЕМ СЛУЧАЕ НИ ОДИН ВЛАДЕЛЕЦ АВТОРСКИХ ПРАВ И НИ 
ОДНО ДРУГОЕ ЛИЦО, КОТОРОЕ МОЖЕТ ИЗМЕНЯТЬ И/ИЛИ ПОВТОРНО РАСПРОСТРАНЯТЬ ПРОГРАММУ, КАК БЫЛО СКАЗАНО ВЫШЕ, НЕ 
НЕСЁТ ОТВЕТСТВЕННОСТИ, ВКЛЮЧАЯ ЛЮБЫЕ ОБЩИЕ, СЛУЧАЙНЫЕ, СПЕЦИАЛЬНЫЕ ИЛИ ПОСЛЕДОВАВШИЕ УБЫТКИ, ВСЛЕДСТВИЕ 
ИСПОЛЬЗОВАНИЯ ИЛИ НЕВОЗМОЖНОСТИ ИСПОЛЬЗОВАНИЯ ПРОГРАММЫ (ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ПОТЕРЕЙ ДАННЫХ, ИЛИ 
ДАННЫМИ, СТАВШИМИ НЕПРАВИЛЬНЫМИ, ИЛИ ПОТЕРЯМИ ПРИНЕСЕННЫМИ ИЗ-ЗА ВАС ИЛИ ТРЕТЬИХ ЛИЦ, ИЛИ ОТКАЗОМ ПРОГРАММЫ 
РАБОТАТЬ СОВМЕСТНО С ДРУГИМИ ПРОГРАММАМИ), ДАЖЕ ЕСЛИ ТАКОЙ ВЛАДЕЛЕЦ ИЛИ ДРУГОЕ ЛИЦО БЫЛИ ИЗВЕЩЕНЫ О 
ВОЗМОЖНОСТИ ТАКИХ УБЫТКОВ.
==================================


Но с тех пор скрипты (особенно основной) сильно переписаны.

'''

version = 'wrx100-2.0'

import MOD
import sys

import config
CONFIG = config.Config()
CONFIG.read()

import debug
DEBUG = debug.Debug(CONFIG)

import utils
UTILS = utils.Utils(CONFIG, DEBUG)

import mserial
SERIAL = mserial.Serial(CONFIG, DEBUG)

import gsm
GSM = gsm.GSM(CONFIG, DEBUG, SERIAL)

import sms
SMS = sms.SMS(GSM, DEBUG)

import sms_msg

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
C_SCFG1 = 'AT#SCFG=1,1,' + CONFIG.get('TCP_MAX_LENGTH') + ',90,30,2\r'	 # AT КОМАНДА НАСТРОЙКИ СОКЕТА №1,"2" - data sending timeout; after this period data are sent also if they’re less than max packet size.
C_SCFGEXT1 = 'AT#SCFGEXT=1,1,0,0,0,0\r'  # COKET1, SRING + DATA SIZE, receive in TEXT, keepalive off, autoreceive off, send in TEXT

C_SCFG2 = 'AT#SCFG=2,1,' + CONFIG.get('TCP_MAX_LENGTH') + ',120,30,2\r'   # AT КОМАНДА НАСТРОЙКИ СОКЕТА №2 - Сокет для определения точного времени 15 сек на попытку подключенния
C_SCFGEXT2 = 'AT#SCFGEXT=2,1,0,0,0,0\r'  # COKET2, SRING + DATA SIZE+DATA, receive in TEXT, keepalive off, autoreceive off, send in TEXT

C_SCFG3 = 'AT#SCFG=3,1,' + CONFIG.get('TCP_MAX_LENGTH') + ',300,30,2\r'   # 
C_SCFGEXT3 = 'AT#SCFGEXT=3,1,0,2,0,0\r'  # keep alive on

def initWatchdog():
	MOD.watchdogEnable(int(CONFIG.get('WATCHDOG_PERIOD')))
	
def resetWatchdog():
	MOD.watchdogReset()
	
def ping(trys):
	servers = CONFIG.get('PING_IPS').split(',')
	for i in range(trys):
		for server in servers:
			DEBUG.send('Send ping to ' + server)
			res = GSM.ping(server)
			if(res == 0):
				return (0)
			resetWatchdog()
	return (-1)

def smsProcessing():
	message = SMS.receiveSms()
	if message is not None:
		text = message.getText()
		DEBUG.send('Got incoming SMS from ' + message.getNumber() + ' with text: "' + text + '"')

		# always delete sms, maan
		SMS.deleteSms(message.getId())

		if (text == 'WAKEUPNEO'):
			SMS.sendSms(sms_msg.SmsMessage('0', message.getNumber(), '', 'Follow the white rabbit'))
			GSM.reboot()

		# other cases - compound commands
		words = text.split(' ')
		
		if (len(words) >= 3):
			if (words[0] == "SET"):
				CONFIG.set(words[1], words[2])
				CONFIG.write()
				SMS.sendSms(sms_msg.SmsMessage('0', message.getNumber(), '', 'done cfg write for "' + message.getText() + '"' ))


try:
#	 REG_REPLY = UTILS.getServerReply(CONFIG.get('ID_SERVER'))				 # РАСЧЕТ ОТВЕТА РЕГИСТРАЦИИ НА СЕРВЕРЕ НА ОСНОВЕ СВОЕГО ID_SERVER
#	 REG_LOG_REPLY = UTILS.getServerReply(CONFIG.get('ID_LOG_SERVER'))
	
	initWatchdog()
	SERIAL.init()						# ИНИЦИАЛИЗАЦИЯ ПОСЛЕДОВАТЕЛЬНОГО ПОРТА
	GSM.initModem()						# НАСТРОЙКА ПАРАМЕТРОВ GSM МОДЕМА
	# GSM.initStartMode()				  # НАСТРОЙКА РЕЖИМА ЗАПУСКА СКРИПТОВ
	GSM.initSim()						# ПРОВЕРКА РАБОТОСПОСОБНОСТИ SIM КАРТЫ
	GSM.initCreg()						# ПРОВЕРКА РЕГИСТРАЦИИ В СЕТИ
	GSM.initCsq()						# ПОЛУЧЕНИЕ УРОВНЯ СИГНАЛА В АНТЕННЕ
	SMS.init()

	DEBUG.send(' SCRIPT STARTED. Version: ' + version + '\r\nCopyright 2012.' \
				'Teleofis Wireless Communications\r\n==============' \
				'==================================')

	try:
		GSM.initSocket(C_SCFG1, C_SCFGEXT1) # ИНИЦИАЛИЗАЦИЯ Socket 1
	#	 GSM.initSocket(C_SCFG2, C_SCFGEXT2) # ИНИЦИАЛИЗАЦИЯ Socket 2
	#	 GSM.initSocket(C_SCFG3, C_SCFGEXT3) # ИНИЦИАЛИЗАЦИЯ Socket 3
	except Exception, e:
		DEBUG.send('Socket init exception: ' + e)
	GSM.initContext()					# НАСТРОЙКА ПАРАМЕТРОВ PDP КОНТЕКСТА
	
	if(CONFIG.get('ATRUN_ENABLED') == '1'):
		GSM.startAtRun()
	
	#
	# Status flags
	#
	#DATA_AUTH = 0
	#LOG_AUTH = 0
	DATA_SOCKET = 0
	#LOG_SOCKET = 0
	
	#
	# Timers
	#
	TCP_LOG_TIMER = 0
	# arithmetics used to make always check for sms on first iteration
	CHECK_SMS_TIMER = MOD.secCounter() - int(CONFIG.get('SMS_CHECK_PERIOD')) - 1

	while(1):

		if ((MOD.secCounter() - CHECK_SMS_TIMER) > int(CONFIG.get('SMS_CHECK_PERIOD'))):
			DEBUG.send('Processing SMS')
			smsProcessing()
			CHECK_SMS_TIMER = MOD.secCounter()

		# check context
		context = GSM.checkContext()
		if(context != '1'):
			DEBUG.send('Activation GPRS context')
			GSM.activateContext()
		
		# check socket 1
		socket = GSM.checkSocket('1')
		if(socket not in ['1', '2', '3']):	 # Socket closed
			DEBUG.send('Trying to open a socket #1 (data)')
			DATA_SOCKET = 0
		#	 DATA_AUTH = 0
			try:
				GSM.connect('1', CONFIG.get('DEST_IP'), CONFIG.get('DEST_PORT'), 3)
				DATA_SOCKET = 1
			except Exception, e:
				DEBUG.send(str(e))
				ping_trys = int(CONFIG.get('PING_TRYS'))
				res = ping(ping_trys)
				if(res < 0):
					raise Exception, 'ERROR. Ping failed'
				continue
		
		# data channel authorization
		#if((CONFIG.get('REG_SERVER') == '1') and (DATA_SOCKET == 1) and (DATA_AUTH == 0)):
		#	 DEBUG.send('Start authorization on socket #1 (data)')
		#	 MOD.sleep(20)
		#	 data = ''
		#	 try:
		#		 data = GSM.receiveMDM()
		#	 except Exception, e:
		#		 DEBUG.send(e)
		#	 if((len(data) > 0)): # and (data.find(AUTH_REQUEST) != -1)):
		#		 if(CONFIG.get('AUTH_TYPE') == '0'):
		#			 GSM.sendMDM(REG_REPLY)
		#		 else:
		#			 imei = GSM.getImei()
		#			 DEBUG.send('IMEI: %s' % (imei))
		#			 auth = UTILS.getAnalitycsReply(int(imei))
		#			 b = ''
		#			 for i in auth:
		#				 b = b + chr(i)
		#			 DEBUG.send('AUTH REPLY: %s' % (b))
		#			 GSM.sendMDM(b)
		#	 else:
		#		 DEBUG.send('Authorization failed')
		#		 continue
		#	 DATA_AUTH = 1
		#	 DEBUG.send('Authorization complete')
		#
		#if(CONFIG.get('AUTH_TYPE') != '1'):
		#	 if(CONFIG.get('DEBUG_TCP') == '1'):
		#		 socket = GSM.checkSocket('2')
		#		 if(socket not in ['1', '2', '3']):   # Socket closed
		#			 DEBUG.send('Trying to open a socket #2 (log)')
		#			 LOG_SOCKET = 0
		#			 LOG_AUTH = 0
		#			 try:
		#				 GSM.connect('2', CONFIG.get('LOG_IP'), CONFIG.get('LOG_PORT'), 3)
		#				 LOG_SOCKET = 1
		#			 except Exception, e:
		#				 DEBUG.send(e)
			
			# log channel authorization
		#	 if((CONFIG.get('REG_LOG_SERVER') == '1') and (LOG_SOCKET == 1) and (LOG_AUTH == 0)):
		#		 DEBUG.send('Start authorization on socket #2 (log)')
		#		 data = ''
		#		 try:
		#			 data = GSM.receive('2')
		#		 except Exception, e:
		#			 DEBUG.send(e)
		#		 if((len(data) > 0)): # and (data.find(AUTH_REQUEST) != -1)):
		#			 GSM.send(REG_LOG_REPLY, '2')
		#		 else:
		#			 DEBUG.send('Authorization failed')
		#		 LOG_AUTH = 1
		#		 DEBUG.send('Authorization complete')
		
			# send TCP debug info
		#	 if((CONFIG.get('DEBUG_TCP') == '1') and (MOD.secCounter() > TCP_LOG_TIMER) and (LOG_SOCKET == 1)):
		#		 buffer = DEBUG.getTcpBuffer()
		#		 GSM.send(buffer, '2')
		#		 TCP_LOG_TIMER = MOD.secCounter() + int(CONFIG.get('DEBUG_TCP_PERIOD'))

		# serial to tcp

		lastActivityTime = MOD.secCounter()

		while (1):

			activityDetected = 0

			data = SERIAL.receive(int(CONFIG.get('TCP_MAX_LENGTH')))
			if(len(data) > 0):
				GSM.sendMDM(data)
				activityDetected = 1
		
			# tcp to serial
			data = ''
			try:
				data = GSM.receiveMDM()
			except Exception, e:
				DEBUG.send(str(e))

			if(len(data) > 0):
				SERIAL.send(data)
				activityDetected = 1

			resetWatchdog()

			if (activityDetected == 1):
				lastActivityTime = MOD.secCounter()
			else:
				if ((MOD.secCounter() - lastActivityTime) > int(CONFIG.get('TIMEOUT_CONSISTENT_SER'))):
					DEBUG.send('Consistent minisession broken due to inactivity')
					break
	
except Exception, e:
	DEBUG.send('Exception!' + str(e))
	GSM.reboot()
		

		
