#!/usr/bin/python
import serial
import sys
import time
from operator import xor

# UART
ID= ""
Zeichen = 0

# Tag
Checksumme = 0
Tag = 0 

# UART oeffnen
RFID = serial.Serial("/dev/serial0", 9600)
if(RFID.isOpen() == False):
	RFID.open()

while True:

	# Variablen loeschen
	Checksumme = 0
	Checksumme_Tag = 0
	ID = ""

	# Zeichen einlesen
	Zeichen = RFID.read() 

	# Uebertragungsstart signalisiert worden?
	if Zeichen == chr(0x02):

		# ID zusammen setzen
		for Counter in range(13):

			Zeichen = RFID.read() 
			ID = ID + str(Zeichen)

		# Endflag aus dem String loeschen
		ID = ID.replace(chr(0x03), "")

		# Checksumme berechnen
		for I in range(0, 9, 2):
			Checksumme = Checksumme ^ (((int(ID[I], 16)) << 4) + int(ID[I+1], 16))
		Checksumme = hex(Checksumme)

		# Ausgabe der Daten
		print("------------------------------------------")
		print("Datensatz: ", ID)
		print("ID: ", ID[0:10])
		print("Checksumme: ", Checksumme)
		print("------------------------------------------")