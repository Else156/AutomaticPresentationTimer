# Based on https://gist.github.com/t-622/c10183117565c404325a7a01d542617a
from machine import Pin
from time import sleep_us, sleep_ms

class Lcd:
    def __init__(self, rs, e, d4, d5, d6, d7):
        self.rs = Pin(rs, Pin.OUT)
        self.e = Pin(e, Pin.OUT)
        self.d4 = Pin(d4, Pin.OUT)
        self.d5 = Pin(d5, Pin.OUT)
        self.d6 = Pin(d6, Pin.OUT)
        self.d7 = Pin(d7, Pin.OUT)
        self.init()

    def pulse_e(self):
        self.e.on()
        sleep_us(40)
        self.e.off()
        sleep_us(40)

    def write_4bits(self, data):
        self.d4.value((data >> 0) & 1)
        self.d5.value((data >> 1) & 1)
        self.d6.value((data >> 2) & 1)
        self.d7.value((data >> 3) & 1)
        self.pulse_e()

    def send(self, data, is_cmd=True):
        self.rs.value(not is_cmd)
        self.write_4bits(data >> 4)  # High nibble
        self.write_4bits(data & 0x0F)  # Low nibble

    def init(self):
        sleep_ms(50)
        self.write_4bits(0x03)
        sleep_ms(5)
        self.write_4bits(0x03)
        sleep_us(100)
        self.write_4bits(0x03)
        self.write_4bits(0x02)
        
        self.send(0x28)  # Function set: 4-bit, 2-line, 5x8 dots
        self.send(0x0C)  # Display control: Display on, cursor off, blink off
        self.send(0x06)  # Entry mode set: Increment cursor, no shift
        self.clear()

    def clear(self):
        self.send(0x01) # Clear display
        sleep_ms(2)

    def move_to(self, x, y):
        addr = x + (0x40 if y == 1 else 0x00)
        self.send(0x80 | addr)
    
    def putstr(self, s):
        for char in s:
            if char == '\n':
                self.move_to(0, 1)
            else:
                self.send(ord(char), is_cmd=False)