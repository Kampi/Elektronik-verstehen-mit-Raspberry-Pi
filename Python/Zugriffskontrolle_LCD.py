#!/usr/bin/python
import serial
import time
import operator

# UART
Datensatz = ""
Zeichen = 0

# User ID
ID = 0
User = ""
Benutzer = {}
Checksumme = 0
Checksumme_Tag = 0
Check = 0

# UART oeffnen
RFID = serial.Serial("/dev/ttyUSB0", 9600)
if(RFID.isOpen() == False):
	RFID.open()
	
# LCD oeffnen
LCD_Interface = serial.Serial("/dev/ttyAMA0", 9600)
if(LCD_Interface.isOpen() == False):
	LCD_Interface.open()

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
	
# Datei oeffnen
Temp = open("/Programme/ID.txt", "r")

# Datei zeilenweise auslesen
for Zeile in Temp: 

	# CR aus der Textzeile entfernen
	Zeile = Zeile.replace("\n", "")
	
	# LF aus der Textzeile entfernen
	Zeile = Zeile.replace("\r", "")
	
	# Textzeile aufteilen
	Zeile = Zeile.split(":")
	
	# ID aus der Datei in eine Zahl umwandeln
	Zeile[1] = int(Zeile[1])
	
	# Daten zu der Liste hinzufuegen
	Benutzer[Zeile[1]] = Zeile[0]

Temp.close()

while True:

	# Variablen loeschen
	Checksumme = 0
	Checksumme_Tag = 0
	Datensatz = ""
	
	# Zeichen einlesen
	Zeichen = RFID.read() 

	# Uebertragungsstart signalisiert worden?
	if Zeichen == chr(0x02):

		# ID zusammen setzen 
		for Counter in range(13):

			Zeichen = RFID.read() 
			Datensatz = Datensatz + str(Zeichen)

		# Endflag aus dem String loeschen
		Datensatz = Datensatz.replace(chr(0x03), "" );

		# Checksumme berechnen
		for I in range(0, 9, 2):
			Checksumme = Checksumme ^ (((int(Datensatz[I], 16)) << 4) + int(Datensatz[I+1], 16))

		# Checksumme ueberpruefen
		Checksumme_Tag = ((int(Datensatz[10], 16)) << 4) + (int(Datensatz[11], 16))
		
		if Checksumme_Tag == Checksumme:
			Check = 1
		else:
			Check = 0
		
		# ID herausfiltern und zum Suchen in einen Int umwandeln
		ID = Datensatz[4:10]
		ID = int(ID, 16)
		
		# User herausfinden
		User = Benutzer.get(ID, "Unbekannt")

	LCD_ClearScreen()

	if Check == 1:
		LCD_PrintLine(1, 0, "Daten: " + str(Datensatz))
		LCD_PrintLine(2, 0, "ID: " + str(ID))
		LCD_PrintLine(3, 0, "User: " + str(User))
	else:
		LCD_PrintLine(1, 0, "Lesefehler")
		LCD_PrintLine(2, 0, "Erneut versuchen")
	
RFID.close()