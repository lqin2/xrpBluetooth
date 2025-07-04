import asyncio
from bleak import BleakClient, BleakScanner
from pynput import keyboard
import tkinter as tk
from tkinter import messagebox

UART_SERVICE_UUID = "27df26c5-83f4-4964-bae0-d7b7cb0a1f54"
UART_RX_UUID = "452af57e-ad27-422c-88ae-76805ea641a9"

# Global joystick and claw state
joystick_x = 127
joystick_y = 127
claw_duty = 5000  # Neutral claw position

# Clamp function
def clamp(val, min_val=1000, max_val=9000):
    return max(min_val, min(max_val, val))

# Arrow key and claw handlers
def on_press(key):
    global joystick_x, joystick_y, claw_duty
    try:
        if key == keyboard.Key.up:
            joystick_y = 0
        elif key == keyboard.Key.down:
            joystick_y = 255
        elif key == keyboard.Key.left:
            joystick_x = 55
        elif key == keyboard.Key.right:
            joystick_x = 200
        elif key.char == 'q':
            claw_duty = clamp(claw_duty - 200)
        elif key.char == 'w':
            claw_duty = clamp(claw_duty + 200)
    except:
        pass

def on_release(key):
    global joystick_x, joystick_y
    if key in [keyboard.Key.up, keyboard.Key.down]:
        joystick_y = 127
    if key in [keyboard.Key.left, keyboard.Key.right]:
        joystick_x = 127

def select_device_gui(device_list):
    selected_index = [None]

    def on_select(event):
        selected = listbox.curselection()
        if selected:
            selected_index[0] = selected[0]
            root.quit()

    def on_cancel():
        root.quit()

    root = tk.Tk()
    root.title("Select XRProbot")
    root.geometry("400x200")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
    for i, dev in enumerate(device_list):
        listbox.insert("end", f"{i}: {dev.name} ({dev.address})")
    listbox.pack(side="left", fill="both", expand=True)
    listbox.bind("<<ListboxSelect>>", on_select)
    listbox.bind("<Double-1>", on_select)

    scrollbar.config(command=listbox.yview)

    cancel_button = tk.Button(root, text="Cancel", command=on_cancel)
    cancel_button.pack(pady=5)

    root.mainloop()
    root.destroy()

    return selected_index[0]

async def choose_xrp_ble_device():
    print("🔍 Scanning for XRProbot devices...")
    await asyncio.sleep(3.0)
    try:
        devices = await BleakScanner.discover(timeout=5.0)
    except Exception as e:
        print("❌ BLE scan failed:", e)
        return None

    xrp_devices = [dev for dev in devices if dev.name and dev.name.lower() != "none"]

    if not xrp_devices:
        messagebox.showerror("Not found", "No XRProbot devices found.")
        return None

    index = select_device_gui(xrp_devices)
    if index is not None:
        return xrp_devices[index]
    else:
        return None

async def main():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    device = await choose_xrp_ble_device()
    if not device:
        return

    print(f"✅ Found: {device.name} ({device.address})")
    async with BleakClient(device) as client:
        print("🔗 Connected to XRP (W = open claw, Q = close claw)")

        while True:
            try:
                report = bytearray(20)
                report[0] = 0x01
                report[1] = joystick_x
                report[2] = joystick_y
                report[7] = (claw_duty >> 8) & 0xFF
                report[8] = claw_duty & 0xFF

                await client.write_gatt_char(UART_RX_UUID, report)
                print(f"📤 Sent: Claw:{claw_duty} | JoyX:{joystick_x} JoyY:{joystick_y}")

                await asyncio.sleep(0.05)
            except Exception as e:
                print("⚠️ Error:", e)
                await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Exiting.")
