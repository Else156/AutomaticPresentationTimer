# ZHO-0420S-05A4.5(5V)を制御するためのコード
# メインプログラムに結合する前の単体テストコード
from machine import Pin
from utime import sleep

solenoid_pin = Pin(15, Pin.OUT)

def activate_solenoid(duration):
    print("Activating solenoid...")
    solenoid_pin.high()
    sleep(duration)
    solenoid_pin.low()
    print("Solenoid deactivated.")

if __name__ == "__main__":
    sleep(3) 
    try:
        while True:
            activate_solenoid(0.1)  
            sleep(5)
            
            activate_solenoid(0.1)  
            sleep(0.1)
            activate_solenoid(0.1)  
            sleep(5)

            activate_solenoid(0.1)  
            sleep(0.1)
            activate_solenoid(0.1) 
            sleep(0.1) 
            activate_solenoid(0.1)  
            sleep(5)
    except KeyboardInterrupt:
        solenoid_pin.low()
        print("Operation interrupted. Solenoid deactivated.")