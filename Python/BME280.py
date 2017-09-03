#!/usr/bin/python
import spidev
import time
import numpy

BME280 = spidev.SpiDev()
BME280.open(0, 0)

Kalibrationswerte = {}

def WriteRegister(Adresse, Daten):
	Adresse = Adresse & 0x7F
	Datenliste = []
	Datenliste.append(Adresse)
	Datenliste.append(Daten)
	BME280.xfer2(Datenliste)
	
def ReadRegister(Adresse):
	Adresse = Adresse | (1 << 7)
	Datenliste = []
	Datenliste.append(Adresse)
	Datenliste.append(0x00)
	return BME280.xfer2(Datenliste)[1] 
	
def StartMeasurement():
	Config = ReadRegister(0xF4)
	Config &= 0xFC
	Config |= 0x01
	WriteRegister(0xF4, Config)
	
def ReadShort(Adresse):
	LSB = ReadRegister(Adresse)
	MSB = ReadRegister(Adresse + 1)
	
	return (MSB << 8) | LSB

def ReadCalibrationData():
	Kalibrationswerte["dig_T1"] = ReadShort(0x88)
	Kalibrationswerte["dig_T2"] = numpy.int16(ReadShort(0x8A))
	Kalibrationswerte["dig_T3"] = numpy.int16(ReadShort(0x8C))
	
	Kalibrationswerte["dig_P1"] = ReadShort(0x8E)
	Kalibrationswerte["dig_P2"] = numpy.int16(ReadShort(0x90))
	Kalibrationswerte["dig_P3"] = numpy.int16(ReadShort(0x92))
	Kalibrationswerte["dig_P4"] = numpy.int16(ReadShort(0x94))
	Kalibrationswerte["dig_P5"] = numpy.int16(ReadShort(0x96))
	Kalibrationswerte["dig_P6"] = numpy.int16(ReadShort(0x98))
	Kalibrationswerte["dig_P7"] = numpy.int16(ReadShort(0x9A))
	Kalibrationswerte["dig_P8"] = numpy.int16(ReadShort(0x9C))
	Kalibrationswerte["dig_P9"] = numpy.int16(ReadShort(0x9E))
	Kalibrationswerte["dig_H2"] = numpy.int16(ReadShort(0xE1))
	
	Kalibrationswerte["dig_H1"] = ReadRegister(0xA1)
	Kalibrationswerte["dig_H3"] = ReadRegister(0xE3)
	Kalibrationswerte["dig_H6"] = numpy.int8(ReadRegister(0xE7))
	
	MSB = ReadRegister(0xE4)
	LSB = ReadRegister(0xE5) & 0x0F
	Kalibrationswerte["dig_H4"] = numpy.int16((MSB << 4) | LSB)
	
	MSB = ReadRegister(0xE6)
	LSB = ReadRegister(0xE5) & 0xF0
	Kalibrationswerte["dig_H5"] = numpy.int16((MSB << 4) | LSB)

def ReadTemperature():

	XLSB = ReadRegister(0xFC)
	LSB = ReadRegister(0xFB)
	MSB = ReadRegister(0xFA)
	
	ADCData = (MSB << 12) | (LSB << 4) | (XLSB >> 4)
	
	var1 = ((ADCData / 16384.0) - ((Kalibrationswerte["dig_T1"]) / 1024.0)) * Kalibrationswerte["dig_T2"]
	var2 = ((ADCData / 131072.0) - ((Kalibrationswerte["dig_T1"]) / 8192.0)) * Kalibrationswerte["dig_T3"]

	global t_fine
	t_fine = numpy.int32(var1 + var2)
	
	return (float(t_fine) / 5120.0)

def ReadPressure():
	
	var1 = numpy.int64(0)
	var2 = numpy.int64(0)
	p = numpy.int64(0)
	
	XLSB = ReadRegister(0xF9)
	LSB = ReadRegister(0xF8)
	MSB = ReadRegister(0xF7)
	
	ADCData = (MSB << 12) | (LSB << 4) | (XLSB >> 4)

	var1 = numpy.int64(t_fine) - 128000
	var2 = var1 * var1 * numpy.int64(Kalibrationswerte["dig_P6"])
	var2 = var2 + ((var1 * numpy.int64(Kalibrationswerte["dig_P5"])) << 17)
	var2 = var2 + (numpy.int64(Kalibrationswerte["dig_P4"]) << 35)
	var1 = ((var1 * var1 * numpy.int64(Kalibrationswerte["dig_P3"])) >> 8) + ((var1 * numpy.int64(Kalibrationswerte["dig_P2"])) << 12)
	var1 = (((numpy.int64(1) << 47) + var1) * numpy.int64(Kalibrationswerte["dig_P1"])) >> 33
	if (var1 == 0):
		print("Messwert wird durch 0 geteilt!")
		return 0

	p = 1048576 - ADCData; 
	p = numpy.int64((((p << 31) - var2) * 3125) / var1)
	var1 = (numpy.int64(Kalibrationswerte["dig_P9"]) * (p >> 13) * (p >> 13)) >> 25
	var2 = (numpy.int64(Kalibrationswerte["dig_P8"]) * p) >> 19
	p = ((p + var1 + var2) >> 8) + (numpy.int64(Kalibrationswerte["dig_P7"]) << 4)
	return float(p) / 256.0

def ReadHumidity():

	LSB = ReadRegister(0xFE)
	MSB = ReadRegister(0xFD)

	ADCData = LSB | (MSB << 8)

	var1 = t_fine - 76800
	var1 = (((((ADCData << 14) - (Kalibrationswerte["dig_H4"] << 20) - (Kalibrationswerte["dig_H5"] * var1)) + 16384) >> 15) * (((((((var1 * Kalibrationswerte["dig_H6"]) >> 10) * (((var1 * Kalibrationswerte["dig_H3"]) >> 11) + 32768)) >> 10) + 2097152) * Kalibrationswerte["dig_H2"] + 8192) >> 14))
	var1 = var1 - (((((var1 >> 15) * (var1 >> 15)) >> 7) * Kalibrationswerte["dig_H1"]) >> 4)

	return float(var1 >> 12) / 1024

# Sensor reseten
WriteRegister(0xE0, 0xB6)

# Sensor konfigurieren
WriteRegister(0xF5, 0x00)
WriteRegister(0xF4, 0x24)
WriteRegister(0xF2, 0x01)
time.sleep(1)

print("ID: " + str(ReadRegister(0xD0)))
print("Ctrl Meas: " + str(ReadRegister(0xF4)))
print("Ctrl Hum: " + str(ReadRegister(0xF2)))

ReadCalibrationData()

# Messung starten
#StartMeasurement()
#time.sleep(2)
#print("Temperatur: " + str(numpy.round(ReadTemperature(), 2)) + " Grad Celsius")
#print("Luftdruck: " + str(numpy.round(ReadPressure() / 100, 2)) + " hPa")
#print("Luftfeuchtigkeit: " + str(numpy.round(ReadHumidity(), 2)) + " %RH")

while(True):

	StartMeasurement()
	time.sleep(2)
	Temperatur = numpy.round(ReadTemperature(), 2)
	Luftdruck = numpy.round(ReadPressure() / 100.0, 2)
	Luftfeuchtigkeit = numpy.round(ReadHumidity(), 2)
	
	LogFile = open("Klima.csv", "a")
	LogFile.write(time.strftime("%d.%m.%Y %H:%M:%S") + ";" + str(Temperatur) + ";" + str(Luftdruck) + ";" + str(Luftfeuchtigkeit) + "\n")
	LogFile.close()