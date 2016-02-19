import GPS
import SER
import MDM
import MOD

SER.set_speed('9600', '8N1')

SER.send('### TEST. ver. 2.1\r\n')

while (1):

	SER.send('### --- loop start --- ===\r\n')

	i_max = 1000
	ser_read_start = MOD.secCounter()

	for i in range(1,i_max):
		rcv = SER.read()

	SER.send('SER.read test. Cycle iters: ' + str(i_max)  + '. Elapsed secs: ' + str(MOD.secCounter() - ser_read_start)  + '\r\n')

	ser_send_start = MOD.secCounter()

	for i in range(1,i_max):
		SER.send('0')

	SER.send('\r\n')

	SER.send('SER.send test. Cycle iters: ' + str(i_max)  + '. Elapsed secs: ' + str(MOD.secCounter() - ser_send_start)  + '\r\n')


	mod_seccounter_start = MOD.secCounter()

	for i in range(1,i_max):
		dummy = MOD.secCounter()

	SER.send('MOD.secCounter test. Cycle iters: ' + str(i_max)  + '. Elapsed secs: ' + str(MOD.secCounter() - mod_seccounter_start)  + '\r\n')

	SER.send('### --- loop end --- ###\r\n')
