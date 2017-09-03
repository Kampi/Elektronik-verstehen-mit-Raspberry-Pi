#!/usr/bin/python
import smbus
import time

ChipAdresse = 0x40

PCA8685 = smbus.SMBus(1)

# Chip reseten
PCA8685.write_byte(0x00, 0x06)

def SetDutyCycle(Pin, OnZeit):
	Basisadresse = 0x06 + Pin * 4
	
	LowByte = (0xFFF - OnZeit) & 0x00FF
	HighByte = ((0xFFF - OnZeit) & 0xFF00) >> 8
	PCA8685.write_byte_data(ChipAdresse, Basisadresse, LowByte)
	PCA8685.write_byte_data(ChipAdresse, Basisadresse + 1, HighByte)

	LowByte = 0xFFF & 0x00FF
	HighByte = (0xFFF  & 0xFF00) >> 8
	PCA8685.write_byte_data(ChipAdresse, Basisadresse + 2, LowByte)
	PCA8685.write_byte_data(ChipAdresse, Basisadresse + 3, HighByte)

def SetPWMPrecaler(Prescaler):
	Mode = PCA8685.read_byte_data(ChipAdresse, 0x00)
	Mode = Mode & 0x7F
	SleepMode = Mode | (1 << 4)
	PCA8685.write_byte_data(ChipAdresse, 0x00, SleepMode)
	PCA8685.write_byte_data(ChipAdresse, 0xFE, Prescaler)
	PCA8685.write_byte_data(ChipAdresse, 0x00, Mode)
	time.sleep(0.01)
	PCA8685.write_byte_data(ChipAdresse, 0x00, Mode | (1 << 8))

def RotateServo(Winkel):
	DutyCycle = Winkel / 0.87
	SetDutyCycle(0, 204 + int(DutyCycle))

PCA8685.write_byte_data(ChipAdresse, 0x01, 0x04)
PCA8685.write_byte_data(ChipAdresse, 0x00, 0x01)
time.sleep(0.01)

# Vorteiler fuer eine 50 Hz Frequenz setzen
SetPWMPrecaler(0x79)

# Nullposition anfahren
RotateServo(0)
time.sleep(5)

# Mittelposition anfahren
RotateServo(90)
time.sleep(5)

# Endanschlag anfahren
RotateServo(180)
time.sleep(5)

while(True):

	for Winkel in range(0, 180, 1):
		RotateServo(Winkel)
		time.sleep(0.05)

	time.sleep(1)

	for Winkel in range(180, 0, -1):
		RotateServo(Winkel)
		time.sleep(0.05)

	time.sleep(1)


# PWM deaktivieren
SetDutyCycle(0, 0)
