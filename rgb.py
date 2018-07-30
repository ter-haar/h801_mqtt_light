import machine
import network
import utime
import ujson

from umqtt.robust import MQTTClient
from ubinascii import hexlify

import config
import commands


mqtt = None
wlan = None
PWM = {}
STATUS = {}


def setup_wifi():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.WIFI_ESSID, config.WIFI_PASSWORD)

    while not wlan.isconnected():
        machine.idle()

    print('connected: {}'.format(wlan.ifconfig()[0]))


def setup_mqtt(cb):
    config.MQTT_CLIENT_ID = hexlify(machine.unique_id())
    config.MQTT_TOPIC = config.MQTT_TOPIC + config.MQTT_CLIENT_ID

    global mqtt
    mqtt = MQTTClient(config.MQTT_CLIENT_ID, config.MQTT_HOST)
    mqtt.set_last_will(config.MQTT_TOPIC + b'/info', b'offline')
    mqtt.set_callback(cb)

    mqtt.connect()
    mqtt.subscribe(config.MQTT_TOPIC + b'/#')
    mqtt.publish(config.MQTT_TOPIC + b'/info', b'online')


def setup_pins():
    for color, pin in config.RGB_PINOUT.items():
        machine.Pin(pin, machine.Pin.OUT, value=1)

        PWM[color] = machine.PWM(machine.Pin(pin), freq=1000)
        PWM[color].duty(0)

        STATUS[color] = {
            'state': '',
            'final': 0,         # final PWM after dimming process
            'current': 0,       # current PWM
            'last': 1023,       # last color (after brightness correction)
            'original': 1023,   # last color (without brightness correction)
        }

    STATUS['rgb'] = {
        'state': '',
        'brightness': 255,
    }


def callback(topic, msg):
    # topic and msg are bytes
    print(('callback', topic, msg))
    words = topic.split(b'/')
    if (len(words) > 2):
        # ------------------ set r,g,b,w1,w2 or rgb channel -------------------
        if words[-1] == b'set':
            try:
                payload = ujson.loads(msg)
            except ValueError:
                payload = None

            # ---------- set one chanel (r, g, b, w1, w2) ----------
            if payload and words[-2] in (b'r', b'g', b'b', b'w1', b'w2'):
                # words[-2] is bytes object, LEP_PINOUT keys are string
                color = words[-2].decode()
                obj = {}

                if payload.get('brightness'):
                    STATUS[color]['last'] = payload['brightness'] * 4
                    obj['brightness'] = payload['brightness']

                if payload.get('state') in ('ON', 'OFF'):
                    if payload['state'] == 'ON':
                        STATUS[color]['final'] = STATUS[color]['last']
                    else:
                        STATUS[color]['final'] = 0
                    STATUS[color]['state'] = payload['state']
                    obj['state'] = STATUS[color]['state']
                    obj['brightness'] = STATUS[color]['final'] / 4

                if obj:
                    mqtt.publish(
                        config.MQTT_TOPIC + b'/' + words[-2] + b'/status',
                        ujson.dumps(obj)
                    )

            # ---------- set rgb channels ----------
            if words[-2] == b'rgb':
                obj = {}

                # simple rgb message
                # rgb(89,61,32)
                if msg.startswith(b'rgb('):
                    obj['color'] = {}
                    rgb = msg[4:-1].split(b',')
                    for c, color in enumerate(('r', 'g', 'b'), 0):
                        duty = int(rgb[c]) * 4
                        STATUS[color]['final'] = duty
                        obj['color'][color] = int(rgb[c])
                    obj['state'] = 'ON'
                    # add state = off if all zeros

                # json message
                if payload:
                    if payload.get('brightness'):
                        STATUS['rgb']['brightness'] = int(
                            payload['brightness']
                        )
                        gain = STATUS['rgb']['brightness'] / 255
                        for color in ('r', 'g', 'b'):
                            STATUS[color]['last'] = int(
                                STATUS[color]['original'] * gain
                            )
                        obj['brightness'] = payload['brightness']

                    if payload.get('color'):
                        obj['color'] = {}
                        for color, value in payload['color'].items():
                            STATUS[color]['last'] = value * 4
                            STATUS[color]['original'] = value * 4
                            obj['color'][color] = value

                    if payload.get('state') in ('ON', 'OFF'):
                        STATUS['rgb']['state'] = payload['state']
                        obj['state'] = payload['state']
                        for color in ('r', 'g', 'b'):
                            if payload['state'] == 'ON':
                                STATUS[color]['final'] = STATUS[color]['last']
                            else:
                                STATUS[color]['final'] = 0

                if obj:
                    mqtt.publish(
                        config.MQTT_TOPIC + b'/rgb/status',
                        ujson.dumps(obj)
                    )

        # ------------------------------ command ------------------------------
        elif words[-1] == b'cmd':
            commands.process(msg, mqtt)


def change_pins():
    changed = False
    for color in config.RGB_PINOUT:
        sc = STATUS[color]
        duty = None
        if sc['current'] < sc['final']:
            sc['current'] = sc['current'] + config.RGB_STEP
            duty = sc['current']

        if sc['current'] > sc['final']:
            sc['current'] = sc['current'] - config.RGB_STEP
            duty = sc['current']

        if sc['current'] != sc['final']:
            if abs(sc['current'] - sc['final']) < config.RGB_STEP:
                sc['current'] = sc['final']
                duty = sc['current']

        if duty is not None:
            PWM[color].duty(duty)
            changed = True

    return changed


def main():
    try:
        setup_pins()
        setup_wifi()
        setup_mqtt(callback)

        while True:
            if not wlan.isconnected():
                setup_wifi()

            mqtt.check_msg()

            if not change_pins():
                machine.idle()
            else:
                utime.sleep_ms(10)
    except OSError:
        machine.reset()
