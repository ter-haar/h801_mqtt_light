# H801 vs micropython
## Kolejny sterownik RGB led oparty na mqtt.

Po co? Bo żaden z tych które znalazłem nie miał tego co potrzebowałem. Sterownik jest przeznaczony głównie dla H801 WiFi (ale może działać na dowolnym układzie opartym o esp8266) i pozwala sterować niezależnie każdym z kanałów. Można więc zapalić podłączyć pasek rgb i sterować nim, a zupełnie osobno sterować jeszcze dwoma paskami mono. Albo sterować osobno 5 paskami monohromatycznymi.

Kod jest napisany w pythonie - chciałem sprawdzić jak python poradzi sobie w IoT na układzie z tak ograniczonymi zasobami.

Do uruchomienia sterownika potrzebny jest micropython:
1) pobierz plik bin ze strony https://micropython.org/download#esp8266 (na ten moment najnowszy to esp8266-20180511-v1.9.4.bin)

Niestety, H801 nie lubi się z micropythonem. Wygląda na to, że H801 nie ma wyprowadzonego pinu GPIO1 którego używa UART0 używany przez micropythona. Ale przy odrobinie sprytu można problem obejść. Będzie do tego potrzebna dowolna płytka wyposażona w ESP8266 i usb. Np wemos d1 mini.

2) Zaczynamy więc od wgrania micropythona do wemosa:
```
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 write_flash -fm dio 0x00000 esp8266-20180511-v1.9.4.bin
```
3) sklonuj repozytorium ter-haar/h801_mqtt_light, albo pobierz plik zip.
4) edytuj plik config.sample.py - wprowadź essid i hasło do swojego wifi, oraz adres swojego brokera mqtt
5) zapisz plik jako config.py
6) wgraj wszyskie pliki py do wemosa:
 - zainstaluj ampy (https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy)
 - użyj ampy, by wgrać pliki wszyskie pliki .py do wemosa
```
for n in *.py; do ampy --port /dev/ttyUSB0 put $n; done
```
7) sprawdz czy wszystkie pliki zostały wgrane
```
ampy --port /dev/ttyUSB0 put
```
```
/boot.py
/commands.py
/config.py
/main.py
/rgb.py
/setup.py
```
8) podłącz konsole do wemosa
```
picocom /dev/ttyUSB0 -b115200
```
9) zresetuj wemosa, w konsoli powinienieś zobaczyć
```
ets_task(40100130, 3, 3fff83ec, 4)
connected: 192.168.24.102
mqtt connected
('callback', b'home/light/E801-42602f00/info', b'online')
('callback', b'home/light/E801-42602f00/ip', b'192.168.24.102')
```
10) sprawdź mqtt:
```
mosquitto_sub -v -h adres.hosta.mqtt -t '#'
```
o ile wszystko poszło dobrze to powinienieś tam zobaczyć komunikaty
```
home/light/E801-42602f00/info online
home/light/E801-42602f00/ip 192.168.24.102
```
42602f00 to id Twojego esp8266, więc pewnie będzie inne....
No dobrze, mamy działającego wemosa. Ale chcieliśmy H801! Teraz więc sprytna sztuczka
11) zgraj zawartość flasha z wemosa do pliku
```
esptool.py --port /dev/ttyUSB0 read_flash 0x00000 0x100000 to_801.bin
```
12) odłącz wemosa, podłącz h801 (oczywiście potrzebujesz programatora...)
13) i użyj pliku z zawartością flash wemosa by zaprogramować H801 (dokładny opis tutaj: http://tinkerman.cat/closer-look-h801-led-wifi-controller/). W skrócie:
- podłącz programator, RX do RX, TX do TX, zewrzyj J3, podłącz zasilanie.
- sprawdż czy wszystko H801 wszedł w tryb programowania
```
esptool.py --port /dev/ttyUSB0 chip_id
```
powinieneś zobaczyć coś w stylu:
```
esptool.py v2.5.1
Serial port /dev/ttyUSB0
Connecting....
Detecting chip type... ESP8266
Chip is ESP8266EX
Features: WiFi
MAC: dc:4f:22:4b:db:5b
Uploading stub...
Running stub...
Stub running...
Chip ID: 0x004bdb5b
Hard resetting via RTS pin..
```
- wyłącz zasilanie h801, podłącz ponownie, skasuj fabryczny firmware
```
esptool.py --port /dev/ttyUSB0 erase_flash
```
```
esptool.py v2.5.1
Serial port /dev/ttyUSB0
Connecting....
Detecting chip type... ESP8266
Chip is ESP8266EX
Features: WiFi
MAC: dc:4f:22:4b:db:5b
Uploading stub...
Running stub...
Stub running...
Erasing flash (this may take a while)...
Chip erase completed successfully in 3.5s
Hard resetting via RTS pin...
```
- wyłącz zasilanie h801, podłącz ponownie, wgraj swój plik
```
esptool.py --port /dev/ttyUSB0 write_flash -fm dio 0x00000 to_801.bin
```
14) odłącz programator, podłącz zasilanie, sprawdz mqtt
```
mosquitto_sub -v -h 192.168.24.115 -t '#'
```
```
home/light/E801-5bdb4b00/info online
home/light/E801-5bdb4b00/ip 192.168.24.126
```
Jak widzisz id sie zmieniło, bo h801 ma oczywiscie inny id niz wemos.

## I to tyle na temat przeprogramowania h801.

