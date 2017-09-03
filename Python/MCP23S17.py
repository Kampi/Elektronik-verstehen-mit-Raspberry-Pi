#!/usr/bin/python
import spidev
import time
import RPi.GPIO as GPIO

# SPI oeffnen
MCP23S17 = spidev.SpiDev()
MCP23S17.open(0, 0)

# Konfiguration auslesen
Konfiguration = MCP23S17.xfer2([0x41, 0x05, 0x00])

# Konfiguration in den Port Expander uebertragen
# Ohne Interrupts
#if(Konfiguration[2] < 0x80):
	#MCP23S17.xfer2([0x40, 0x0A, 0xA0])
	#print("Konfiguriere Port Expander")

# Mit Interrupts
if(Konfiguration[2] < 0x80):
	MCP23S17.xfer2([0x40, 0x0A, 0xA2])
	print("Konfiguriere Port Expander")
	
# Bereits vorhandene Interrupts loeschen
MCP23S17.xfer2([0x41, 0x09, 0x00])

# Schaltet einen Pin an einem Port als Ausgang
def SetOutput(Port, Pin):
	Offset = 0x00
	
	if(Port == "A"):
		Offset = 0x00	
	elif(Port == "B"):
		Offset = 0x10

	# Lese Registerinhalt des IODIR-Registers aus
	Register = MCP23S17.xfer2([0x41, Offset + 0x00, 0x00])
	Register[2] &= ~(1 << Pin)
	MCP23S17.xfer2([0x40, Offset + 0x00, Register[2]])
	
	# OLAT-Register entsprechend setzen
	MCP23S17.xfer2([0x40, Offset + 0x0A, Register[2]])
	
# Schaltet einen Pin an einem Port als Eingang
def SetInput(Port, Pin):
	Offset = 0x00
	
	if(Port == "A"):
		Offset = 0x00	
	elif(Port == "B"):
		Offset = 0x10

	# Lese Registerinhalt des IODIR-Registers aus
	Register = MCP23S17.xfer2([0x41, Offset + 0x00, 0x00])
	Register[2] |= 1 << Pin
	MCP23S17.xfer2([0x40, Offset + 0x00, Register[2]])
	
# Aktiviert den Interrupt an einem bestimmten Pin eines bestimmten Ports
def EnableInterrupt(Port, Pin):
	Offset = 0x00
	
	if(Port == "A"):
		Offset = 0x00	
	elif(Port == "B"):
		Offset = 0x10

	# Aktiviere Interrupt im GPINTEN-Register
	Register = MCP23S17.xfer2([0x41, Offset + 0x02, 0x00])
	Register[2] |= 1 << Pin
	MCP23S17.xfer2([0x40, Offset + 0x02, Register[2]])
	
	# Konfiguriere Interrupt fuer value changed, also jedes mal ein Interrupt, wenn sich
	# der Zustand des I/O aendert
	Register = MCP23S17.xfer2([0x41, Offset + 0x04, 0x00])
	Register[2] &= ~(1 << Pin)
	MCP23S17.xfer2([0x40, Offset + 0x04, Register[2]])

# Schaltet einen I/O an einem Port 
def SetIO(Port, Pin, Value):
	Offset = 0x00
	
	if(Port == "A"):
		Offset = 0x00	
	elif(Port == "B"):
		Offset = 0x10

	# Lese Registerinhalt des GPIO-Registers aus
	Register = MCP23S17.xfer2([0x41, Offset + 0x09, 0x00])
	
	# Ueberpruefe ob der Pin gesetzt oder geloescht werden soll
	if(Value == 0):
		Register[2] &= ~(1 << Pin)
	elif(Value == 1):
		Register[2] |= (1 << Pin)

	Register = MCP23S17.xfer2([0x40, Offset + 0x09, Register[2]])

# Interruptmethode fuer den Raspberry Pi
def InterruptCallback(GPIO):

	# Alle Interrupts loeschen
	GPIO_Status = MCP23S17.xfer2([0x41, 0x09, 0x00])
	
	# Interruptbedingung pruefen
	if(GPIO_Status[2] & 0x01): 
		# LED einschalten
		SetIO("B", 0, 1)
	else:
		# LED ausschalten
		SetIO("B", 0, 0)

# GPIO 17 fuer Interrupt konfigurieren
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.add_event_detect(17, GPIO.RISING, callback = InterruptCallback)  

# Kapitel Ausgaenge
#SetOutput("A", 0)
SetOutput("B", 0)

# Kapitel Eingaenge
SetInput("A", 0)
EnableInterrupt("A", 0)

time.sleep(1)
print("Start...")

# Konfigurationsbyte auslesen
print("Konfiguration: " + str(MCP23S17.xfer2([0x41, 0x05, 0x00])[2]))

while(True):

	#SetIO("A", 0, 0)
	#SetIO("B", 0, 1)
	#time.sleep(1)
	#SetIO("A", 0, 1)
	#SetIO("B", 0, 0)
	time.sleep(1)