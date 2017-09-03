#!/usr/bin/python
import spidev
import time

NoLEDs = 31

WS2801 = spidev.SpiDev()
WS2801.open(0, 0)

def SetLED(Blank, R, G, B):
	for Paket in range(Blank):
		WS2801.writebytes([0x00, 0x00, 0x00])
	WS2801.writebytes([R, G, B])
	time.sleep(0.01)
	
def SetLEDs(LEDList):
	for LED in LEDList:
		R = (LED >> 16) & 0xFF
		G = (LED >> 8) & 0xFF
		B = LED & 0xFF
		WS2801.writebytes([R, G, B])
	time.sleep(0.01)

SetLEDs([0x00FF00, 0xFF0000, 0x000000, 0x0000FF, 0x0000FF, 0x0000FF])
	
WS2801.close()