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

import MOD
import SER
import MDM
import MDM2
import sys

class GSM:
    def __init__(self, config, debug, serial):
        self.config= config
        self.debug = debug
        self.serial = serial
        self.buffer = ''
        
    def reboot(self):
        self.sendATDefault('AT#ENHRST=1,0\r', 'OK')
        sys.exit()
    
    def sendAT(self, atcom, atres, trys = 1, timeout = 1, csd = 1):
        mdm_timeout = int(self.config.get('TIMEOUT_MDM'))
        s = MDM2.receive(mdm_timeout)
        result = -2
        while(1):
            if(csd):
                self.tryCSD()
            if(self.config.get('DEBUG_AT') == '1'):
                self.debug.send('AT OUT: ' + atcom)
            s = ''
            MDM2.send(atcom, mdm_timeout)
            timer = MOD.secCounter() + timeout
            while(1):
                s = s + MDM2.receive(mdm_timeout)
                if(s.find(atres) != -1):
                    result = 0
                    break
                if(s.find('ERROR') != -1):
                    result = -1
                    break
                if(MOD.secCounter() > timer):
                    break
            if(self.config.get('DEBUG_AT') == '1'):
                self.debug.send('AT IN: ' + s[2:])
            trys = trys - 1
            if((trys <= 0) or (result == 0)):
                break
            MOD.sleep(15)
        return (result, s)
    
    def sendATData(self, atcom, atres, trys = 1, timeout = 1, csd = 1):
        mdm_timeout = int(self.config.get('TIMEOUT_MDM'))
        s = MDM.receive(mdm_timeout)
        result = -2
        while(1):
            if(csd):
                self.tryCSD()
            if(self.config.get('DEBUG_AT') == '1'):
                self.debug.send('DATA AT OUT: ' + atcom)
            s = ''
            MDM.send(atcom, mdm_timeout)
            timer = MOD.secCounter() + timeout
            while(1):
                s = s + MDM.receive(mdm_timeout)
                if(s.find(atres) != -1):
                    result = 0
                    break
                if(s.find('ERROR') != -1):
                    result = -1
                    break
                if(MOD.secCounter() > timer):
                    break
            if(self.config.get('DEBUG_AT') == '1'):
                self.debug.send('DATA AT IN: ' + s[2:])
            trys = trys - 1
            if((trys <= 0) or (result == 0)):
                break
            MOD.sleep(15)
        return (result, s)
    
    def sendATDefault(self, request, response):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendAT(request, response, 1, at_timeout, self.config.get('CSD_ENABLED'))
        if (a < 0):
            raise Exception, 'ERROR. sendAT(): ' + request + '#' + response

    def tryCSD(self):
        ring = MDM2.getRI()
        if(ring == 1):
            at_timeout = int(self.config.get('TIMEOUT_AT'))
            a, s = self.sendAT('ATA\r', 'CONNECT', 1, 30, 0)
            if(a == 0):
                self.debug.send('CSD CONNECTED')
                while(ring == 1):
                    rcv = self.serial.receive(int(self.config.get('TCP_MAX_LENGTH')))
                    if(len(rcv) > 0):
                        self.sendMDM2(rcv)
                    try:
                        rcv = self.receiveMDM2()
                    except Exception, e:
                        break
                    if(len(rcv) > 0):
                        self.serial.send(rcv)
                    ring = MDM2.getRI()
                    MOD.watchdogReset()
                self.debug.send('CSD DISCONNECTED')
            else:
                self.debug.send('CSD CONNECT ERROR')

    def initModem(self):
        self.sendATDefault('ATE0\r', 'OK')
        self.sendATDefault('AT\\R0\r', 'OK')
        self.sendATDefault('AT#ENHRST=2,' + self.config.get('REBOOT_PERIOD') + '\r', 'OK')
        self.debug.send('initModem() passed OK')
        
    def startAtRun(self):
        self.sendAT('AT#TCPATRUNCFG=3,3,12345,' + self.config.get('ATRUN_PORT') + ',"' + self.config.get('ATRUN_HOST') + '",1,5,1,5,1' + '\r', 'OK')
        self.sendAT('AT#TCPATRUND=1\r', 'OK', 2, 20)
        
    def stopAtRun(self):
        self.sendAT('AT#TCPATRUND=0\r', 'OK', 2, 20)

    def setLed(self, state):
        self.sendATDefault('AT#SLED=' + state + '\r', 'OK')

    def initSim(self):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendAT('AT+CPIN?\r', 'READY', 3, at_timeout)
        if (a < 0):
            a, s = self.sendATD('AT+CPIN?\r', 'SIM PIN', 3, at_timeout)
            if(a == 0):
                a, s = self.sendAT('AT+CPIN=' + self.config.get('PIN') + '\r', 'OK', 3, at_timeout)
                if (a == 0):
                    a, s = self.sendAT('AT+CPIN?\r', 'READY', 3, at_timeout)
                    if (a < 0):
                        raise Exception, 'ERROR. initSim() failed'
                else:
                    raise Exception, 'ERROR. initSim() failed'
            else:
                raise Exception, 'ERROR. initSim() failed'
        self.debug.send('initSim() passed OK')

    def initCreg(self):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendAT('AT+CREG?\r', '+CREG: 0,1', 10, at_timeout)
        if (a < 0):
            raise Exception, 'ERROR. initCreg() failed'
        self.debug.send('initCreg() passed OK')

    def initCsq(self):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendAT('AT+CSQ\r', 'OK', 3, at_timeout)
        if (a < 0):
            raise Exception, 'ERROR. initCsq() failed'
        a_i = s.split(chr(13))
        a_i_p = a_i[1].find('+CSQ')
        self.debug.send('initCsq() passed OK ' + a_i[1][a_i_p:])

    def initStartMode(self):
        mode = self.config.get('STARTMODESCR')
        self.sendATDefault('AT#STARTMODESCR=' + mode + '\r', 'OK')
        self.debug.send('initStartMode() passed OK')
    
        # НАСТРОЙКА ПАРАМЕТРОВ FIREWALL
    def initFirewall(self):
        self.sendATDefault('AT#FRWL=2\r', 'OK')
        self.sendATDefault('AT#FRWL=1,"' + self.config.get('DEST_IP') + '","255.255.255.255"\r', 'OK')
    
    # НАСТРОЙКА ПАРАМЕТРОВ PDP КОНТЕКСТА
    def initContext(self):
        self.sendATDefault('AT+CGDCONT=1,"IP","' + self.config.get('APN') + '"\r', 'OK')
    
    # АКТИВАЦИЯ КОНТЕКСТА - ВКЛЮЧЕНИЕ GPRS
    def activateContext(self):
        timeout = int(self.config.get('TIMEOUT_PDP'))
        a, s = self.sendAT('AT#SGACT=1,0\r', 'OK', 5, timeout)
        if (a == 0):
            a, s = self.sendAT('AT#SGACT=1,1,"' + self.config.get('GPRS_USER') + '","' + self.config.get('GPRS_PASSWD') + '"\r', 'OK', 10, timeout)
            if (a == 0):
                str_IP = s.split(chr(13))
                i_str_IP = str_IP[1].find(': ')
                My_IP = str_IP[1][i_str_IP + 2:]
                self.debug.send('GPRS CONTEXT activated ... OK  IP: ' + My_IP)
                return My_IP
        raise Exception, 'ERROR. Activate GPRS CONTEXT failed'
    
    def checkContext(self):
        timeout = int(self.config.get('TIMEOUT_MDM'))
        a, s = self.sendAT('AT#SGACT?\r', 'OK', 10, timeout)
        d = s.find('#SGACT:')
        if (d != -1):
            return(s[d + 10])
        raise Exception, 'ERROR. checkContext() failed'
    
    def initSocket(self, scfg, scfgext):
        self.sendATDefault(scfg, 'OK')
        self.sendATDefault(scfgext, 'OK')
        self.debug.send('initSocket() passed OK')
    
    def connect(self, socket, ip, port, trys):
        timeout = int(self.config.get('TIMEOUT_TCP'))
        if(socket == '1'):
            a, s = self.sendATData('AT#SD=' + socket + ',0,' + port + ',"' + ip + '",0,1,0\r', 'CONNECT', trys, timeout)
        else:
            a, s = self.sendAT('AT#SD=' + socket + ',0,' + port + ',"' + ip + '",0,1,1\r', 'OK', trys, timeout)
        if (a < 0):
            raise Exception, 'ERROR. TCP connection on socket ' + socket + ' failed'
        self.debug.send('Socket ' + socket + ' connected to ' + ip + ':' + port)
    
    # Проверка доступности узла
    def ping(self, ip):
        timeout = int(self.config.get('TIMEOUT_TCP'))
        a, s = self.sendAT('AT#PING="' + ip + '",1,32,' + self.config.get('PING_TIMEOUT') + ',128\r', 'OK', 1, timeout)
        if ((a < 0) or (s.find('600,255') != -1)):
            self.debug.send('ERROR. ping() to ' + ip + ' failed')
            return (-1)
        self.debug.send('ping() to ' + ip + ' OK')
        return (0)
    
    def checkSocket(self, socket):
        timeout = int(self.config.get('TIMEOUT_MDM'))
        a, s = self.sendAT('AT#SS=' + socket + '\r', 'OK', 10, timeout)
        d = s.find('#SS:')
        if (d != -1):
            return(s[d + 7])
        raise Exception, 'ERROR. checkSocket() ' + socket + ' failed'
    
    def getImei(self):
        a, s = self.sendAT('AT+CGSN\r', 'OK')
        self.debug.send('IMEI RAW: ' + s)
        if(a < 0):
            self.debug.send('ERROR. getImei() failed')
            return '0'
        imei = s.strip()[6:15]
        return imei
        
    
    def receive(self, socket = '2'):
        res_string = ''
        a, s = self.sendAT('AT#SRECV=' + socket + ',1500\r', 'OK')
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
        self.sendATDefault('AT#SSENDEXT=' + socket + ',' + str(len(data)) + '\r', '>')
        self.sendATDefault(data, 'OK')
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
        
        
