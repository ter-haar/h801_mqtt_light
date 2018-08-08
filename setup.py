import machine
import network

from umqtt.robust import MQTTClient
from ubinascii import hexlify

import config


mqtt = None
wlan = None


def ap_off():
    ap = network.WLAN(network.AP_IF)
    ap.active(False)


def sta_on():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.WIFI_ESSID, config.WIFI_PASSWORD)

    while not wlan.isconnected():
        machine.idle()

    print('connected: {}'.format(wlan.ifconfig()[0]))


def mqtt(cb):
    config.MQTT_CLIENT_ID = hexlify(machine.unique_id())
    config.MQTT_TOPIC = config.MQTT_TOPIC + config.MQTT_CLIENT_ID

    global mqtt
    mqtt = MQTTClient(config.MQTT_CLIENT_ID, config.MQTT_HOST, keepalive=120)
    mqtt.set_last_will(config.MQTT_TOPIC + b'/info', b'offline', retain=True)
    mqtt.set_callback(cb)

    mqtt.connect()
    mqtt.subscribe(config.MQTT_TOPIC + b'/#')
    mqtt.publish(config.MQTT_TOPIC + b'/info', b'online', retain=True)
