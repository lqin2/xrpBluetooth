
from machine import Pin, PWM, ADC
import uasyncio as asyncio
from XRPLib.defaults import drivetrain
from pestolink import PestoLinkAgent

robot_name = "XRPbot2"
pestolink = PestoLinkAgent(robot_name)

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
    global last_angle
    while True:
        if pestolink.is_connected():
            throttle = -1 * pestolink.get_axis(1)
            rotation = -1 * pestolink.get_axis(0)
            print("throttle:", throttle, "rotation:", rotation)
            print("throttle:", throttle, "rotation:", rotation, "raw_axis1:", pestolink.get_raw_axis(1), "raw_axis0:", pestolink.get_raw_axis(0))

            drivetrain.arcade(throttle, rotation)

            angle = pestolink.get_servo_angle()
            set_servo_angle(angle)

            voltage = (ADC(Pin("BOARD_VIN_MEASURE")).read_u16()) / (1024 * 64 / 14)

            pestolink.telemetryPrintBatteryVoltage(voltage)
        else:
            drivetrain.arcade(0, 0)
            set_servo_angle(90)        # Go to neutral
            servo_pwm.duty_u16(0)      # 🔇 Disable PWM to stop buzzing
            last_angle = -1            # Reset last angle to allow re-setting

        await asyncio.sleep(0.05)

asyncio.run(ble_loop())
