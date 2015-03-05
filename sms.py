# magic comment to allow russian bukvs
# coding=UTF8

'''
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
'''

import sms_msg

class SMS:
	def __init__(self, gsm, debug):
		self.gsm = gsm
		self.debug = debug

	def init(self):
		self.gsm.sendATDefault('AT#SMSMODE=1\r', 'OK')
		self.gsm.sendATDefault('AT+CMGF=1\r', 'OK')
		self.debug.send('SMS.init() passed OK')

	def receiveSms(self):
		self.debug.send('Trying to receive SMS messages...')
		r, d = self.gsm.sendAT("AT+CMGL=ALL\r", "OK", 5)
		if(r == 0):
			self.debug.send('Got new messages, parsing then...')
			position = d.find('+CMGL')
			if(position != -1):
				d = d[position:]
				one = d.split('\r')
				if(len(one) > 1):
					header = one[0].strip()[7:]
					data = one[1].strip()
					header_data = header.split(',')
					if(len(header_data) > 5):
						index = header_data[0]
						status = header_data[1].replace('"', '')
						number = header_data[2].replace('"', '')
						time = header_data[4].replace('"', '') + ',' + header_data[5].replace('"', '')
						sms = sms_msg.SmsMessage(index, number, time, data)
						return sms
		return None
    
	def sendSms(self, message):
		r, d = self.gsm.sendAT("AT+CMGS=" + message.getNumber() + "\r", ">", 5)
		if(r == 0):
			r, d = self.gsm.sendAT(message.getText() + chr(0x1A) + "\r", "OK", 10)
			if(r == 0):
				return 0
		return -1
        
        
	def deleteSms(self, index):
		r, d = self.gsm.sendAT("AT+CMGD=" + index + "\r", "OK", 5)
		if(r == 0):
			return 0
		return -1
