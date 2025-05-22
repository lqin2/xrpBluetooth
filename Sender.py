from machine import ADC, Pin
import time

potentiometer = ADC(Pin(26))  # ADC0

while True:
    pot_value = potentiometer.read_u16()
    angle = (pot_value / 65535) * 180
    min_duty = 1000
    max_duty = 9000
    duty = int(min_duty + (max_duty - min_duty) * angle / 180)
    print(f"DUTY:{duty}")  # ✅ Sent to your PC via USB (COM8)
    time.sleep(0.5)


