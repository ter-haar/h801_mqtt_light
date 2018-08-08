import machine
import sys
import urequests

import config


def process_cmd(msg, mqtt):
    if msg == b'exit':
        mqtt.publish(config.MQTT_TOPIC + b'/info', b'offline')
        mqtt.disconnect()
        sys.exit(0)

    elif msg == b'ping':
        mqtt.publish(config.MQTT_TOPIC + b'/cmd/status', b'pong')

    elif msg == b'reset':
        mqtt.disconnect()
        machine.reset()


def process_file(msg, mqtt):
    print (msg)

    response = urequests.get(str(msg, 'utf8'))
    if response.status_code == 200:
        path = msg.split(b'/')[-1]
        print (path)
        f = open(path, 'w')
        f.write(response.text)
        f.close()

# mosquitto_pub -h 192.168.24.115 -t home/light/42602f00/file -m "http://192.168.24.111:8222/config.py"
# python -m SimpleHTTPServer 8222
