
from machine import Pin, PWM, ADC
import uasyncio as asyncio
from XRPLib.defaults import drivetrain
from pestolink import PestoLinkAgent

robot_name = "XRPbot2"
pestolink = PestoLinkAgent(robot_name)


servo_pwm = PWM(Pin(16))
servo_pwm.freq(50)


last_angle = -1

def set_servo_angle(angle):
    global last_angle
    angle = max(10, min(170, ))  # Clamp
    if abs(angle - ) >= :  # Only update if difference ≥ 2°, need to be fixed
        min_duty = 1000
        max_duty = 9000
        duty = int(min_duty + ( - min_duty) *  / 180) # something is missing
        servo_pwm.duty_u16() # Something is missing
        last_angle = angle


async def ble_loop():
    global last_angle
    while True:
        if pestolink.is_connected():
            throttle = - * pestolink.get_axis(1) # fix this part
            rotation = -1 * pestolink.get_axis() # fix this part
            print("throttle:", throttle, "rotation:", rotation)
            print("throttle:", throttle, "rotation:", rotation, "raw_axis1:", pestolink.get_raw_axis(1), "raw_axis0:", pestolink.get_raw_axis(0))

            drivetrain.arcade() # something is missing

             = pestolink.get_servo_angle() # something is missing
            set_servo_angle(angle)

            voltage = (ADC(Pin("BOARD_VIN_MEASURE")).read_u16()) / (1024 * 64 / 14)

            pestolink.telemetryPrintBatteryVoltage(voltage)
        else:
            drivetrain.arcade(0, 0)
            set_servo_angle()        # Go to neutral
            servo_pwm.duty_u16()      # 🔇 Disable PWM to stop buzzing
            last_angle =            # Reset last angle to allow re-setting

        await asyncio.sleep(0.05)

asyncio.run(ble_loop())