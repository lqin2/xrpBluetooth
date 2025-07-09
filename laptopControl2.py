import sys
import asyncio
import serial
import serial.tools.list_ports
from bleak import BleakClient, BleakScanner
from pynput import keyboard

if sys.platform.startswith("win"):
    try:
        from asyncio.windows_events import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    except ImportError:
        pass  # For older Python versions

    
UART_SERVICE_UUID = "27df26c5-83f4-4964-bae0-d7b7cb0a1f54"
UART_RX_UUID = "452af57e-ad27-422c-88ae-76805ea641a9"


BAUD_RATE = 115200

# Global joystick state
joystick_x = 127
joystick_y = 127

# Clamp function
def clamp(val, min_val=1000, max_val=9000):
    return max(min_val, min(max_val, val))

# Arrow key handlers
def on_press(key):
    global joystick_x, joystick_y
    try:
        if key == keyboard.Key.up:
            joystick_y = 0
        elif key == keyboard.Key.down:
            joystick_y = 255
        elif key == keyboard.Key.left:
            joystick_x = 55
        elif key == keyboard.Key.right:
            joystick_x = 200
    except:
        pass

def on_release(key):
    global joystick_x, joystick_y
    if key in [keyboard.Key.up, keyboard.Key.down]:
        joystick_y = 127
    if key in [keyboard.Key.left, keyboard.Key.right]:
        joystick_x = 127
        
def choose_com_port_gui():
    import tkinter as tk
    from tkinter import simpledialog, messagebox

    ports = list(serial.tools.list_ports.comports())
    if not ports:
        messagebox.showerror("Error", "No serial ports found.")
        exit(1)

    

    # List ports for user to select
    root = tk.Tk()
    root.withdraw()
    def is_pico_port(port):
        desc = port.description.lower()
        hwid = port.hwid.lower() if hasattr(port, "hwid") else ""
        return ("pico" in desc) or ("rp2" in desc) or ("raspberry" in desc) or ("pico" in hwid) or ("rp2" in hwid)

    port_names = []
    for port in ports:
        if is_pico_port(port):
            port_names.append(f"{port.device} - {port.description} [PICO?]")
        else:
            port_names.append(f"{port.device} - {port.description}")

    port_str = "\n".join([f"{i}: {name}" for i, name in enumerate(port_names)])
    selected = simpledialog.askinteger("Select Port", f"Available COM ports:\n{port_str}\n\nEnter index (0-{len(ports)-1}):", minvalue=0, maxvalue=len(ports)-1)
    root.destroy()

    if selected is None:
        messagebox.showerror("No selection", "No COM port selected. Exiting.")
        exit(1)
    return ports[selected].device


def select_device_gui(device_list):
    import tkinter as tk
    from tkinter import messagebox

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
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    from bleak import BleakScanner

    # Scan for BLE devices
   
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

    if len(xrp_devices) == 1:
        messagebox.showinfo("XRP Found", f"Found: {xrp_devices[0].name} ({xrp_devices[0].address})")
        return xrp_devices[0]

    index = select_device_gui(xrp_devices)
    if index is not None:
        return xrp_devices[index]
    else:
        return None

  
            
async def main():
    COM_PORT = choose_com_port_gui()
    # Start keyboard listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Open serial to Pico A
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        print(f"📡 Listening to {COM_PORT} for voltage data...")
    except Exception as e:
        print("❌ Serial connection failed:", e)
        return

    # Scan and connect to XRProbot
    device = await choose_xrp_ble_device()
    print(f"✅ Found: {device.name} ({device.address})")
    async with BleakClient(device) as client:
        print("🔗 Connected to XRP")

        while True:
            try:
                line = ser.readline().decode().strip()
                if not line.startswith("DUTY:"):
                    continue

                duty = int(line[5:].strip())
                duty = clamp(duty)

                report = bytearray(20)
                report[0] = 0x01
                report[1] = joystick_x
                report[2] = joystick_y
                report[7] = (duty >> 8) & 0xFF      # High byte
                report[8] = duty & 0xFF             # Low byte

                await client.write_gatt_char(UART_RX_UUID, report)
                print(f"📤 Sent: DUTY:{duty} | JoyX:{joystick_x} JoyY:{joystick_y}")

            except Exception as e:
                print("⚠️ Error:", e)
                await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Exiting.")
