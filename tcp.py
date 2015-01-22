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

import MDM
import MDM2

class TCP:
    def __init__(self, config, debug, gsm):
        self.config = config
        self.debug = debug
        self.gsm = gsm
        self.buffer = ''
    
    # НАСТРОЙКА ПАРАМЕТРОВ FIREWALL
    def initFirewall(self):
        self.gsm.sendATDefault('AT#FRWL=2\r', 'OK')
        self.gsm.sendATDefault('AT#FRWL=1,"' + self.config.get('DEST_IP') + '","255.255.255.255"\r', 'OK')
    
    # НАСТРОЙКА ПАРАМЕТРОВ PDP КОНТЕКСТА
    def initContext(self):
        self.gsm.sendATDefault('AT+CGDCONT=1,"IP","' + self.config.get('APN') + '"\r', 'OK')
    
    # АКТИВАЦИЯ КОНТЕКСТА - ВКЛЮЧЕНИЕ GPRS
    def activateContext(self):
        timeout = int(self.config.get('TIMEOUT_PDP'))
        a, s = self.gsm.sendAT('AT#SGACT=1,0\r', 'OK', 5, timeout)
        if (a == 0):
            a, s = self.gsm.sendAT('AT#SGACT=1,1\r', 'OK', 10, timeout)
            if (a == 0):
                str_IP = s.split(chr(13))
                i_str_IP = str_IP[1].find(': ')
                My_IP = str_IP[1][i_str_IP + 2:]
                self.debug.send('GPRS CONTEXT activated ... OK  IP: ' + My_IP)
                return My_IP
        raise Exception, 'ERROR. Activate GPRS CONTEXT failed'
    
    def checkContext(self):
        timeout = int(self.config.get('TIMEOUT_MDM'))
        a, s = self.gsm.sendAT('AT#SGACT?\r', 'OK', 10, timeout)
        d = s.find('#SGACT:')
        if (d != -1):
            return(s[d + 10])
        raise Exception, 'ERROR. checkContext() ' + socket + ' failed'
    
    def initSocket(self, scfg, scfgext):
        self.gsm.sendATDefault(scfg, 'OK')
        self.gsm.sendATDefault(scfgext, 'OK')
        self.debug.send('initSocket() passed OK')
    
    def connect(self, socket, ip, port, trys):
        timeout = int(self.config.get('TIMEOUT_TCP'))
        if(socket == '1'):
            a, s = self.gsm.sendATData('AT#SD=' + socket + ',0,' + port + ',"' + ip + '",0,1,0\r', 'CONNECT', trys, timeout)
        else:
            a, s = self.gsm.sendAT('AT#SD=' + socket + ',0,' + port + ',"' + ip + '",0,1,1\r', 'OK', trys, timeout)
        if (a < 0):
            raise Exception, 'ERROR. TCP connection on socket ' + socket + ' failed'
        self.debug.send('Socket ' + socket + ' connected to ' + ip + ':' + port)
    
    # Проверка доступности узла
    def ping(self, ip):
        timeout = int(self.config.get('TIMEOUT_TCP'))
        a, s = self.gsm.sendAT('AT#PING="' + ip + '",1,32,' + self.config.get('PING_TIMEOUT') + ',128\r', 'OK', 1, timeout)
        if ((a < 0) or (s.find('600,255') != -1)):
            self.debug.send('ERROR. ping() to ' + ip + ' failed')
            return (-1)
        self.debug.send('ping() to ' + ip + ' OK')
        return (0)
    
    def checkSocket(self, socket):
        timeout = int(self.config.get('TIMEOUT_MDM'))
        a, s = self.gsm.sendAT('AT#SS=' + socket + '\r', 'OK', 10, timeout)
        d = s.find('#SS:')
        if (d != -1):
            return(s[d + 7])
        raise Exception, 'ERROR. checkSocket() ' + socket + ' failed'
    
    def receive(self, socket = '2'):
        res_string = ''
        a, s = self.gsm.sendAT('AT#SRECV=' + socket + ',1500\r', 'OK')
        f_srecv = s.find('#SRECV')
        if (f_srecv == -1):
            return ''
        len_srecv = len(s)
        i_srecv = 9
        while (1):
            i_srecv = i_srecv + 1
            if (f_srecv + i_srecv >= len_srecv):
                return ''
            code_char = ord(s[f_srecv + i_srecv])
            if (code_char == 13):
                break
        start_int = f_srecv + 10             # ВЫЧИСЛЯЕМ МЕСТО НАХОЖДЕНИЯ ПОЛЕЙ "РАЗМЕР ДАННЫХ" И САМИ ДАННЫЕ
        end_int = f_srecv + i_srecv
        string1 = s[start_int:end_int]
        q_data = int(s[start_int:end_int])   # КОЛИЧЕСТВО ПОСТУПИВШИХ ДАННЫХ 
        res_string = s[end_int + 2:end_int + 2 + q_data]
        if (q_data > 0):
            self.debug.send('Data received from socket #' + socket + ': ' + str(q_data) + ' bytes')
        return res_string

    def send(self, data, socket = '2'):
        self.gsm.sendATDefault('AT#SSENDEXT=' + socket + ',' + str(len(data)) + '\r', '>')
        self.gsm.sendATDefault(data, 'OK')
        self.debug.send('Sending data to socket #' + socket + ': ' + str(len(data)) + ' bytes')
    
    def getBuffer(self, size):
        data = ''
        if(len(self.buffer) > size):
            data = self.buffer[0:size]
            self.buffer = self.buffer[size:]
        else:
            data = self.buffer
            self.buffer = ''
        return data
    
    def receiveMDM(self):
        data = ''
        size = int(self.config.get('TCP_MAX_LENGTH'))
        while(1):
            rcv = MDM.read()
            if(len(rcv) > 0):
                self.buffer = self.buffer + rcv
                if(len(self.buffer) > size):
                    break
            else:
                break
        if(len(self.buffer) > 0):
            data = self.getBuffer(size)
            if(data.find('NO CARRIER') != -1):
                raise Exception, '"NO CARRIER" on socket #1'
            self.debug.send('Data received from socket #1 (data): ' + str(len(data)) + ' bytes')
        return data
    
    def receiveMDM2(self):
        data = ''
        size = int(self.config.get('TCP_MAX_LENGTH'))
        while(1):
            rcv = MDM2.read()
            if(len(rcv) > 0):
                self.buffer = self.buffer + rcv
                if(len(self.buffer) > size):
                    break
            else:
                break
        if(len(self.buffer) > 0):
            data = self.getBuffer(size)
            if(data.find('NO CARRIER') != -1):
                raise Exception, '"NO CARRIER" on CSD connection'
            self.debug.send('Data received from CSD connection: ' + str(len(data)) + ' bytes')
        return data
    
    def sendMDM(self, data):
        MDM.send(data, 50)
        self.debug.send('Sending data to socket #1 (data): ' + str(len(data)) + ' bytes')
        
    def sendMDM2(self, data):
        MDM2.send(data, 50)
        self.debug.send('Sending data to CSD: ' + str(len(data)) + ' bytes')




