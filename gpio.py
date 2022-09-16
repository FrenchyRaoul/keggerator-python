from dataclasses import dataclass
import RPi.GPIO as GPIO
import time

from config import RELAY_MIN_ON_TIME_SECONDS, RELAY_MIN_OFF_TIME_SECONDS
from util import Temperature


__all__ = ['initialize_gpio', 'ADC', 'Relay']


def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)


class Relay(object):

    def __init__(self, relay_pin: int):
        self.relay_pin = relay_pin
        self.on = None
        self.last_update = time.time()
        self.initialize()


    def initialize(self):
        GPIO.setup(self.relay_pin, GPIO.OUT)
        self.turn_off()

    def turn_on(self):
        if self.on:
            print("can't turn on relay; it is already on")
            return
        down_time = time.time() - self.last_update
        if down_time > RELAY_MIN_OFF_TIME_SECONDS:
            GPIO.output(self.relay_pin, False)  # 1=off, 0=on
            self.on = True
            self.last_update = time.time()
        else:
            print(f"cannot turn on relay, relay has been off for {down_time} seconds, minimum toggle time is {RELAY_MIN_OFF_TIME_SECONDS} seconds")

    def turn_off(self):
        if not self.on:
            print("can't turn off relay, it is already off")
        up_time = time.time() - self.last_update
        if up_time > RELAY_MIN_ON_TIME_SECONDS:
            GPIO.output(self.relay_pin, True)  # 1=off, 0=on
            self.on = False
            self.last_update = time.time()
        else:
            print(f"cannot turn off relay, relay has been on for {up_time} seconds, minimum toggle time is {RELAY_MIN_ON_TIME_SECONDS} seconds")


@dataclass
class ADC(object):
    adc_number: int
    clock_pin: int
    mosi_pin: int
    miso_pin: int
    cs_pin: int

    def __post_init__(self):
        if 0 < self.adc_number > 7:
            raise ValueError("adc number must be greater than 0, less than 7")

        # set up the SPI interface pins
        GPIO.setup(self.mosi_pin, GPIO.OUT)
        GPIO.setup(self.miso_pin, GPIO.IN)
        GPIO.setup(self.clock_pin, GPIO.OUT)
        GPIO.setup(self.cs_pin, GPIO.OUT)

    def read(self) -> int:
        print("reading adc")
        GPIO.output(self.cs_pin, True)

        GPIO.output(self.clock_pin, False)  # start clock low
        GPIO.output(self.cs_pin, False)  # bring CS low

        commandout = self.adc_number
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3  # we only need to send 5 bits here
        for i in range(5):
            if (commandout & 0x80):
                GPIO.output(self.mosi_pin, True)
            else:
                GPIO.output(self.mosi_pin, False)
            commandout <<= 1
            GPIO.output(self.clock_pin, True)
            GPIO.output(self.clock_pin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            GPIO.output(self.clock_pin, True)
            GPIO.output(self.clock_pin, False)
            adcout <<= 1
            if (GPIO.input(self.miso_pin)):
                adcout |= 0x1

        GPIO.output(self.cs_pin, True)

        adcout >>= 1  # first bit is 'null' so drop it
        return adcout

    def read_temperature_c(self) -> Temperature:
        millivolts = self.read() * (5010.0 / 1024.0)
        return Temperature(float((millivolts - 500) / 10))
