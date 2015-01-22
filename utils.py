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

import crc16

class Utils:
    def __init__(self, config, debug):
        self.config = config
        self.debug = debug
        
    def getAnalitycsReply(self, imei):
        data = [0xFF, 0xFE, 0x10, 0x08, 0x00, 0x91, imei & 0xFF, (imei >> 8) & 0xFF, (imei >> 16) & 0xFF, (imei >> 24) & 0xFF, 0x02, 0x00, 0x0C, 0x5D]
        crc = crc16.crc16calc(data)
        data = data + [crc & 0xFF, (crc >> 8) & 0xFF, 0x0D, 0x0A]
#        data1 = struct.pack("<BBBHBIBH", 0xFF, 0xFE, 0x10, 8, 0x91, imei, 0x01, 1500)
#        crc = crc16.crc16calc(data1)
#        data2 = struct.pack("<HBB", crc, 0x0D, 0x0A)
        return data
    
    def getAnalitycsRequest(self):
#        data1 = struct.pack("<BBBHBIB", 0xFF, 0xFE, 0x10, 1, 5, 0, 1)
#        crc = crc16.crc16calc(data1)
#        data2 = struct.pack("<H", crc)
        return []

    def getServerReply(self, id):
        id_H4 = id[2:4]
        id_H3 = id[4:6]
        id_H2 = id[6:8]
        id_H1 = id[8:10]

        result = 0xFFFF
        DATA1 = chr(int('FD', 16)) + chr(int(id_H4, 16)) + chr(int(id_H3, 16)) \
        + chr(int(id_H2, 16)) + chr(int(id_H1, 16)) + chr(int('25', 16)) \
        + chr(int('12', 16)) + chr(int('10', 16)) + chr(int('00', 16)) \
        + chr(int('00', 16)) + chr(int('04', 16))
        len_DATA1 = len(DATA1)

        for i in xrange(0, len_DATA1):
            result = result ^ ord(DATA1[i])
            for j in xrange(1, 9):
                bit = result & 0x0001
                result = result >> 1
                if bit == 0x0001:
                    result = result ^ 0xA001

        result_hex = hex(result)
        crcL1 = result_hex[4:6]
        crcH1 = result_hex[2:4]
        shablon1 = DATA1 + crcL1 + crcH1

        X1 = int('1000' + str((int('0xFD', 16) & 128) == 128) \
            + str((ord(DATA1[1]) & 128) == 128) \
            + str((ord(DATA1[2]) & 128) == 128) \
            + str((ord(DATA1[3]) & 128) == 128), 2)
        X2 = int('1' + str((ord(DATA1[4]) & 128) == 128) \
            + str((ord(DATA1[5]) & 128) == 128) \
            + str((ord(DATA1[6]) & 128) == 128) \
            + str((ord(DATA1[7]) & 128) == 128) \
            + str((ord(DATA1[8]) & 128) == 128) \
            + str((ord(DATA1[9]) & 128) == 128) \
            + str((ord(DATA1[10]) & 128) == 128), 2)
        X3 = int('1' + str(int(crcL1, 16) > 127) \
            + str((int(crcH1, 16) > 127)) + '00000', 2)

        DATA2 = chr(int('02', 16)) + chr(int('AA', 16)) + chr(int('AA', 16)) + \
               chr(int('86', 16)) + chr(int('81', 16)) + chr(int('8F', 16)) + \
               chr(int('80', 16)) + chr(int('80', 16)) + chr(int('FD', 16)) + \
               chr((int(id_H4, 16) | 128)) + chr((int(id_H3, 16) | 128)) + \
               chr((int(id_H2, 16) | 128)) + chr(X1) + chr((int(id_H1, 16) | 128)) + \
               chr(int('A5', 16)) + chr(int('92', 16)) + chr(int('90', 16)) + \
               chr(int('80', 16)) + chr(int('80', 16)) + chr(int('84', 16)) + chr(X2) + \
               chr(int(crcL1, 16) | 128) + chr(int(crcH1, 16) | 128) + chr(X3)

        result = 0x0000
        len_DATA2 = len(DATA2)

        for i in xrange(3, len_DATA2):
            b = ord(DATA2[i]) << 8
            result = result ^ b
            for j in xrange(1, 9):
                bit = result & 0x8000
                if bit > 32767:
                    result = result << 1
                    result = result ^ 0x1021
                else:
                    result = result << 1
        result = result | 0x8080
        result = result & 0xffff
        result_hex = hex(result)

        crcL2 = result_hex[4:6]
        crcH2 = result_hex[2:4]
        REG_SERVER_REPLY = DATA2 + chr(int(crcL2, 16)) + chr(int(crcH2, 16)) + chr(int('0x03', 16))

        return REG_SERVER_REPLY
