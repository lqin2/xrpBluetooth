from machine import ADC, Pin
import time


min_duty = 1000
max_duty = 9000
duty = min_duty
step = 200  # Amount to increase or decrease each cycle
direction = 1  # 1 = increasing, -1 = decreasing

while True:
    print(f"DUTY:{duty}")  # Sent to PC via USB (COMx)
    duty += step * direction

    if duty >= max_duty:
        duty = max_duty
        direction = -1
    elif duty <= min_duty:
        duty = min_duty
        direction = 1

    time.sleep(0.5)
