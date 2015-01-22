Python script for using gprs-modem as remote access-point
============================

Credits
----------------------------

- Firstly, script was initially borrowed from Teleofis company. So visit them: http://teleofis.ru

- Secondly, script works on telit hardware and on telit python interpreter. So visit them too: http://telit.com

- Thirdly, if you do not have access to Telit development toolkit (it is true for most of you), then here is handmade toolkit for linux: https://github.com/GROUNDLAB/Telit-Loader . It is initial point and you can't test and upload this script with it, but you can do it with my fork of that toolkit: https://github.com/seik0ixtem/Telit-Loader


Where it should work
-----------------------------

- It is being tested on Telit GL868-Dual GSM module, so it must work with them.

- I believe, that it should *MAINLY* work on most of other Telit modules with python support.


What this script is designed for
-----------------------------

Main idea is that GSM-module on its own connects to some server with TCP, makes some authorization and then allows server to manage this GSM-module.

What is "to manage" GSM-module (some features may be not implemented yet, some features may be missing in this list):

- Change any parameter of the script

- Put any at-commands to the device, and get results.

- Open new TCP connections from device to any destination for logging and debugging purposes

- Read state and change state of GPIO ports of the device

- Allow remote control by CSD reserve channel (by white list)

- Allow remote control by SMS (by white list)

- Send/get data to/from serial port of the device

- Create transparent bridge from device serial port to TCP connection

- Reboot


Also, device should do some work on its own:

- Sync time with server

- Make some specific operations with devices attached to its serial


Notes
------------------------------

Repo may include *.sample files, but script may need that files without .samples suffix.
So, change settings in that file and rename it. I made that not to include my private data in configuration files and added private configuration files in .gitignore
For example: settings.ini.sample.
