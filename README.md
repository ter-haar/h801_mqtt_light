# mqtt_light
python driven mqtt rgb light switch

ampy --port /dev/ttyUSB0 put /home/ter_haar/my_projects/micro_python/mqtt_light/config.py
picocom /dev/ttyUSB0 -b115200

mosquitto_sub -v -h 192.168.24.115 -t '#'

esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 read_flash 0x00000 0x100000 to_801
esptool.py --port /dev/ttyUSB0 write_flash -fm dio 0x00000 to_801


mosquitto_pub -h 192.168.24.115 -t home/light/5d916f00/file -m "http://192.168.24.111:8222/config.py"
python -m SimpleHTTPServer 8222


mosquitto_pub -h 192.168.24.115 -t home/light/5d916f00/cmd -m "exit"
