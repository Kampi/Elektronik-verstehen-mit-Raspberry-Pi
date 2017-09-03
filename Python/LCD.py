#!/usr/bin/python
import serial
import time

LCD_Interface = serial.Serial("/dev/serial0", 9600)

def LCD_PrintLine(Reihe, Position, Text):
	if(Reihe == 1):
		Cursor = 0
	elif(Reihe == 2):
		Cursor = 64
	elif(Reihe == 3):
		Cursor = 20
	elif(Reihe == 4):
		Cursor = 84
	else:
		Cursor = 0
	Cursor = Cursor + Position + 0x80
	LCD_Interface.write(chr(0xFE))
	LCD_Interface.write(chr(Cursor))
	LCD_Interface.write(Text)
	
def LCD_ClearScreen():
	LCD_Interface.write(chr(0xFE))
	LCD_Interface.write(chr(0x01))

while(True):
	temp = open("/sys/class/thermal/thermal_zone0/temp", "r")
	Temperatur = temp.readline()
	Temperatur = float(Temperatur)
	Temperatur = Temperatur / 1000
	Temperatur = str(Temperatur)

	LCD_ClearScreen()
	LCD_PrintLine(1, 0, "Temperatur:")
	LCD_PrintLine(2, 0, Temperatur)
	time.sleep(1)
