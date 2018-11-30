# H801 vs micropython
## sterowanie h801 przez mqtt

```
mosquitto_pub -h adres.brokera.mqtt -t 'home/light/E801-5d916f00/cmd' -m 'ping'
```

* włączenie danego kanału (albo rgb)
```
home/light/E801-5d916f00/rgb/set {"state": "ON"}
home/light/E801-5d916f00/r/set {"state": "ON"}
home/light/E801-5d916f00/g/set {"state": "ON"}
home/light/E801-5d916f00/b/set {"state": "ON"}
home/light/E801-5d916f00/w1/set {"state": "ON"}
home/light/E801-5d916f00/w2/set {"state": "ON"}
```

* wyłączenie
```
home/light/E801-5d916f00/rgb/set {"state": "OFF"}
```

* włączenie, ustawienie koloru, ustawienie jasności
```
home/light/E801-5d916f00/rgb/set {"color": {"g": 0, "r": 255, "b": 148}, "state": "ON", "brightness": 255}
```

* ping - przydaje się by sprawdzić czy układ 'żyje'
```
home/light/E801-5d916f00/cmd ping
```
