# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import sys
print (sys.version)

import os
import time
import board
import busio
import serial
import adafruit_dht
import adafruit_gps


################### DHT22 temp/humidity collection and logging ###################

dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

f = open('/home/pi/Project/dht22_sal.csv', 'a+') # this file may need to change
if os.stat('/home/pi/Project/dht22_sal.csv').st_size == 0:
    f.write('Date,Time,Temperature,Humidity\r\n')
running = True
while running:

    try:
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity

        print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity))

        if humidity is not None and temperature_c is not None:
            f.write('{0},{1},{2:0.1f}*C,{3:0.1f}%\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), temperature_c, humidity))
            time.sleep(3)


        else:
            print("failed to read sensor")

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue
    except KeyboardInterrupt:
        print("Program stopped")
        running = False
        f.close()

################### GPS location collection ###################

#uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)

gps = adafruit_gps.GPS(uart, debug=False)

gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

gps.send_command(b"PMTK220, 1000")

last_print = time.monotonic()
while True:
	gps.update()
	current = time.monotonic()
	if current - last_print >= 1.0:
		last_print = current
		if not gps.has_fix:
			print("Waiting for fix")
			continue
		print("=" * 40)
		print(
			"Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,  # month!
                gps.timestamp_utc.tm_sec,		
			)
		)
		print("Latitude: {0:.6f} degrees".format(gps.latitude))
        print("Longitude: {0:.6f} degrees".format(gps.longitude))
		print("Fix quality: {}".format(gps.fix_quality))
		
		if gps.satellites is not True:
		    print("# satellites: {}".format(gps.satellites))
		if gps.altitude_m is not None: 	
		    print("Altitude: {} meters".format(gps.altitude_m))
		if gps.speed_knots is not None:
		    print("Speed: {} knots".format(gps.speed_knots))
		if gps.track_angle_deg is not None:
		    print("Track angle: {} degrees".format(gps.track_angle_deg))
		if gps.horizontal_dilution is not None:
		    print("Horizontal dilution: {}".format(gps.horizontal_dilution))
		if gps.height_geoid is not None:
		    print("Height geo ID: {} meters".format(gps.height_geoid))
			
######################## GPS datalogging ########################		

LOG_FILE = "gps.txt" #change to same file as T/H logging after testing functionality 
LOG_MODE = "ab"

uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)

gps = adafruit_gps.GPS(uart)


with open(LOG_FILE, LOG_MODE) as outfile:
    while True:
	    sentence = gps.readline()
		if not sentence:
		    continue
		print(str(sentence, "ascii").strip())
		outfile.write(sentence)
		outfile.flush()	