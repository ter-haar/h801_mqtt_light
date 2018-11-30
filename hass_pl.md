# H801 vs micropython
## Konfiguracja Home Assistant

Przykładowa konfiguracja home assistant'a, do H801 podłączony jeden pasek RGB i dwa paski mono

```
- platform: mqtt_json
    name: python_h801_rgb
    state_topic: "home/light/E801-5d916f00/rgb/status"
    command_topic: "home/light/E801-5d916f00/rgb/set"
    availability_topic: "home/light/E801-5d916f00/info"
    brightness: true
    rgb: true

  - platform: mqtt_json
    name: python_h801_w1
    state_topic: "home/light/E801-5d916f00/w1/status"
    command_topic: "home/light/E801-5d916f00/w1/set"
    availability_topic: "home/light/E801-5d916f00/info"
    brightness: true

  - platform: mqtt_json
    name: python_h801_w2
    state_topic: "home/light/E801-5d916f00/w2/status"
    command_topic: "home/light/E801-5d916f00/w2/set"
    availability_topic: "home/light/E801-5d916f00/info"
    brightness: true
```

Osobne sterowanie każdym kanałem R,G,B

```
- platform: mqtt_json
    name: python_h801_r
    state_topic: "home/light/E801-5d916f00/r/status"
    command_topic: "home/light/E801-5d916f00/r/set"
    availability_topic: "home/light/E801-5d916f00/info"
    brightness: true

  - platform: mqtt_json
    name: python_h801_g
    state_topic: "home/light/E801-5d916f00/g/status"
    command_topic: "home/light/E801-5d916f00/g/set"
    availability_topic: "home/light/E801-5d916f00/info"
    brightness: true

  - platform: mqtt_json
    name: python_h801_b
    state_topic: "home/light/E801-5d916f00/b/status"
    command_topic: "home/light/E801-5d916f00/b/set"
    availability_topic: "home/light/E801-5d916f00/info"
    brightness: true
```
