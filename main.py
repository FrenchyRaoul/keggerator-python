#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import datetime
# import dhtreader

from config import *
from config import SPICLK, SPIMISO, SPICS, RELAY
from gpio import *


if __name__ == '__main__':

    print("initializing gpio")
    initialize_gpio()

    print("initializing adc")
    adc = ADC(adc_number=adc_number, clock_pin=SPICLK, mosi_pin=SPIMISO, miso_pin=SPIMISO, cs_pin=SPICS)

    print("initializing relay")
    relay = Relay(RELAY)

    print("entering loop")
    try:
        while True:
            #		k=1
            #		while k<10:
            #			try:
            #				print 'dht read start'
            #				tempDHT, humidity = dhtreader.read(22, 26)
            #				print 'dht read successful'
            #				break
            #			except TypeError:
            #				k += 1
            #

            temp = adc.read_temperature_c().temp_f
            # tempF2 = tempDHT * 2 + 30
            # itempAve = float((tempF+tempF2)/2)

            timenow = datetime.datetime.now()


            if temp > target_temp_f and not relay.on:
                try:
                    relay.turn_on()
                except CompressorException:
                    pass
            elif temp < target_temp_f and relay.on:
                try:
                    relay.turn_off()
                except CompressorException:
                    pass

            print("temp is".format(temp))

            # if databaseConnect:
            #     sql = "INSERT INTO temperature (year,month,day,hour,minute,second,temperature,temperature2, humidity) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
            #     timenow.year, timenow.month, day, hour, minute, second, tempF, tempF2, humidity)
            #     cur.execute(sql)

            time.sleep(2)

    except Exception as e:
        print(f"main loop crashed: {e}")

    finally:
        print("attempting to turn of fridge.")
        try:
            relay._turn_off()
            print("relay disengage signal sent. program terminating")
        except:
            print("failed to disengage relay. program terminating")
