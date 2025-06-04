Connect the Pico W to the computer, then upload Sender.py and save it as main.py. Exit the code editor, then unplug the Pico W and replug it back to the computer.

Connect the Pico W on the xrp to the computer, Go to https://experientialrobotics.org/drive-an-xrp-robot-with-pestolink/ download the PestoLink-MicroPython repository and unzip it. Upload that to the xrp. After that replace pestolink_example in the example folder with xrp.py then save it as main.py. Then update pestolink.py with pestolinkNew.py in this gitHub save it and keep the name as pestolink.py. Exit the code editor, then unplug the Pico W on the xrp and connect the xrp to the power supply.

Now save laptopControl.py to your computer make sure it is in \Users\username. Download Python 3.11 if you didn’t: https://www.python.org/downloads/release/python-3110/
Open your Windows PowerShell and type py -3.11 -m pip install bleak pyserial pynput. After you download that type py -3.11 laptopControl.py in the PowerShell.

You can also download laptopControl.exe to control the xrp without downloading Python.

You should be able to control the xrp using the arrow keys.

