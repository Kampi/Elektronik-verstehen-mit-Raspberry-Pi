#!/usr/bin/python
import smbus
import time

ADS1015 = smbus.SMBus(1)

ADS1015.write_word_data(0x48, 0x01, 0x8342)

# Kalibrierte Spannung bei einem Strom von 0 A
Nullspannung = 2.464

# Empfindlichkeit in V/A
Empfindlichkeit = 0.1

while(True):
	
	# Spannungswert auslesen
	Messergebnis = ADS1015.read_word_data(0x48, 0) 
	MSB = Messergebnis & 0x00FF
	LSB = (Messergebnis & 0xFF00) >> 8
	
	# Spannung berechnen
	Messergebnis_gedreht = (MSB << 8) | LSB
	Messergebnis_gedreht = Messergebnis_gedreht >> 4
	
	if(Messergebnis_gedreht > 2047):
		Messergebnis_invertiert = ~Messergebnis_gedreht		
		Messergebnis = (Messergebnis_invertiert + 1) & 0x7FF
		Messergebnis = (-1) * Messergebnis_gedreht 
	
	Spannung = 4.096 * (float(Messergebnis_gedreht) / 2048.0)
	
	# Differenzspannung bilden
	Differenz = Nullspannung - Spannung
	
	# Strom berechnen
	Strom = Differenz / Empfindlichkeit
	
	print("Die Spannung betraegt: " + str(Spannung) + " V")
	print("Die gemessene Strom betraegt: " + str(Strom) + " A")
	
	time.sleep(1)