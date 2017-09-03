#!/usr/bin/python
import smbus
import time

Triangle = [ 0.375, 0.75, 1.125, 1.5, 1.875, 2.25, 2.625, 3.0, 2.625, 2.25, 1.875, 1.5, 1.125, 0.75, 0.375, 0 ]

U_Max = 3.3
delta_U = U_Max / 4096

MCP4725 = smbus.SMBus(1)

def SendVoltage(Voltage):
	if(Voltage > U_Max):
		return false

	Voltage_Dez = Voltage / delta_U
	Voltage_Dez = int(Voltage_Dez)
	Voltage_Dez_High = (Voltage_Dez >> 4) & 0xFF 
	Voltage_Dez_Low = (Voltage_Dez & 0x0F) << 4
	
	MCP4725.write_word_data(0x62, 0x40, (Voltage_Dez_Low << 8) | Voltage_Dez_High)

while(True):
	#for Value in Triangle:
	#	SendVoltage(Value)
	#	time.sleep(0.125)
	
	SendVoltage(1.2)
