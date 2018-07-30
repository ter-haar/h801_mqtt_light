import sys

import config


def process(msg, mqtt):
    if msg == b'exit':
        mqtt.publish(config.MQTT_TOPIC + b'/info', b'offline')
        mqtt.disconnect()
        sys.exit(0)

    elif msg == b'ping':
        mqtt.publish(config.MQTT_TOPIC + b'/cmd/status', b'pong')
