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

PCA8685.write_byte_data(ChipAdresse, 0x01, 0x04)
PCA8685.write_byte_data(ChipAdresse, 0x00, 0x01)
time.sleep(0.01)

# Vorteiler auf 100 setzen
Mode = PCA8685.read_byte_data(ChipAdresse, 0x00)
Mode = Mode & 0x7F
SleepMode = Mode | (1 << 4)
PCA8685.write_byte_data(ChipAdresse, 0x00, SleepMode)
PCA8685.write_byte_data(ChipAdresse, 0xFE, 0x3C)
PCA8685.write_byte_data(ChipAdresse, 0x00, Mode)
time.sleep(0.01)
PCA8685.write_byte_data(ChipAdresse, 0x00, Mode | (1 << 8))

# PWM mit 10% On-Zeit und 90% Off-Zeit erzeugen
#SetDutyCycle(0, 0xE66)

DutyCycle = 0
while(True):
	SetDutyCycle(0, 409)
	DutyCycle = DutyCycle + 41
	time.sleep(1)