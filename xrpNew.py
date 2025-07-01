from machine import Pin, PWM, ADC
import uasyncio as asyncio
import time
from XRPLib.defaults import drivetrain
from pestolink import PestoLinkAgent

robot_name = "XRPbot2"
pestolink = PestoLinkAgent(robot_name)

# Flag to toggle between simulated voltage and real voltage reading
USE_FAKE_VOLTAGE = True
sim_voltage = 7.0  # Start at mid-range for fake voltage

# Initialize PWM for servo on GPIO16
servo_pwm = PWM(Pin(16))
servo_pwm.freq(50)

# Track last angle to avoid redundant PWM writes
last_angle = -1

def set_servo_angle(angle):
    global last_angle
    angle = max(10, min(170, angle))  # Clamp
    if abs(angle - last_angle) >= 2:  # Only update if difference ≥ 2°
        min_duty = 1000
        max_duty = 9000
        duty = int(min_duty + (max_duty - min_duty) * angle / 180)
        servo_pwm.duty_u16(duty)
        last_angle = angle

async def ble_loop():
    global last_angle, sim_voltage
    prev_voltage = 0
    angle = 90  # Start neutral

    while True:
        if pestolink.is_connected():
            throttle = -1 * pestolink.get_axis(1)
            rotation = -1 * pestolink.get_axis(0)
            drivetrain.arcade(throttle, rotation)

            if USE_FAKE_VOLTAGE:
                voltage = sim_voltage
                sim_voltage += 0.05 if time.ticks_ms() % 2000 < 1000 else -0.05
                sim_voltage = max(6.5, min(8.2, sim_voltage))  # Clamp fake voltage
            else:
                voltage = (ADC(Pin("BOARD_VIN_MEASURE")).read_u16()) / (1024 * 64 / 14)

            pestolink.telemetryPrintBatteryVoltage(voltage)

            # Voltage-based claw control
            delta = voltage - prev_voltage
            if abs(delta) > 0.01:
                angle += 2 if delta > 0 else -2
                angle = max(10, min(170, angle))
                set_servo_angle(angle)

            prev_voltage = voltage

        else:
            drivetrain.arcade(0, 0)
            set_servo_angle(90)
            servo_pwm.duty_u16(0)
            last_angle = -1

        await asyncio.sleep(0.1)

asyncio.run(ble_loop())
