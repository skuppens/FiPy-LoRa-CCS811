import binascii
import pycom
import socket
import time
import struct
from network import LoRa


from machine import Pin, I2C
import CCS811

i2c = I2C(0, pins=('P10','P11'))
# Adafruit sensor breakout has i2c addr: 90; Sparkfun: 91
sensor = CCS811.CCS811(i2c=i2c, addr=91)
time.sleep(1)
#while True:
     # if sensor.data_ready():
     #     print('eCO2: %d ppm, TVOC: %d ppb' % (sensor.eCO2, sensor.tVOC))
     #     time.sleep(1)

# Colors
off = 0x000000
red = 0xff0000
green = 0x00ff00
blue = 0x0000ff

# Turn off hearbeat LED
pycom.heartbeat(False)

# Initialize LoRaWAN radio
lora = LoRa(mode=LoRa.LORAWAN)

# Set network keys
app_eui = binascii.unhexlify('70B3D57ED002C9EF')
app_key = binascii.unhexlify('D7FD383E0507B21A5CA9BD0ED6E4937F')

# Join the network
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
pycom.rgbled(red)

# Loop until joined
while not lora.has_joined():
    print('Not joined yet...')
    pycom.rgbled(off)
    time.sleep(0.1)
    pycom.rgbled(red)
    time.sleep(2)

print('Joined')
pycom.rgbled(blue)

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setblocking(True)

i = 0
while True:
    if sensor.data_ready():
        print('eCO2: %d ppm, TVOC: %d ppb' % (sensor.eCO2, sensor.tVOC))
        time.sleep(0.1)
    #count = s.send(bytes([i % 256]))
    data = struct.pack('>hh', sensor.tVOC, sensor.eCO2)
    #count = s.send(bytes([sensor.eCO2 % 256, sensor.tVOC % 256]))
    s.send(data)
    print('Sent %s bytes' % data)
    pycom.rgbled(green)
    time.sleep(0.1)
    pycom.rgbled(blue)
    time.sleep(9.9)
    i += 1
