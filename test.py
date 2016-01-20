import GPS
import SER
import MDM
import MOD

SER.set_speed('115200', '8N1')
while 1:
	SER.send('hello world!')
	MOD.sleep(30)

