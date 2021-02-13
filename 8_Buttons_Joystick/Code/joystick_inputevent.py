#!/usr/bin/python3
"""
XAC 8 button, 2 axis joystick triggered by USB and BT mouse events.
"""

import sys
import asyncio
import evdev        # sudo apt install python3-evdev
from enum import IntEnum
from Joystick_8 import *

Joystick = Joystick_8()
Joystick.begin('/dev/hidg0')

"""
USB HID joysticks may optionally expose digital buttons through the HID
interface. The Xbox Adaptivecontroller will map the first 8 buttons to
X1/X2/ThumbBtnL/BumperL/A/B/View/Menufor Left USB port, and
View/Menu/ThumbBtnR/BumperR/X/Y/X1/X2for Right USB port.  Any additional
buttons will be ignored.If the mapped buttons are reconfigured using the Xbox
Accessories App, the new configurations will be applied to USB HID joystick
buttons,too.
"""

class LEFT_BUTTON(IntEnum):
    X1 = 0
    X2 = 1
    ThumbBtnL = 2
    BumperL = 3
    A = 4
    B = 5
    View = 6
    Menu = 7

class RIGHT_BUTTON(IntEnum):
    View = 0
    Menu = 1
    ThumbBtnR = 2
    BumperR = 3
    X = 4
    Y = 5
    X1 = 6
    X2 = 7

# Map keyboard keys or mouse buttons to joystick buttons.
EVENT2BUTTON = {
    str(evdev.ecodes.BTN_LEFT): LEFT_BUTTON.A,
    str(evdev.ecodes.BTN_RIGHT): LEFT_BUTTON.B,
    str(evdev.ecodes.BTN_MIDDLE): LEFT_BUTTON.BumperL,
    str(evdev.ecodes.BTN_SIDE): LEFT_BUTTON.ThumbBtnL,
    str(evdev.ecodes.BTN_EXTRA): LEFT_BUTTON.View,
    str(evdev.ecodes.KEY_A): LEFT_BUTTON.Menu,
    str(evdev.ecodes.KEY_S): LEFT_BUTTON.X1,
    str(evdev.ecodes.KEY_D): LEFT_BUTTON.X2,
}

async def handle_events(device):
    # Grab exclusive access means the shell and/or GUI no longer receives the input events
    with device.grab_context():
        async for event in device.async_read_loop():
            if event.code == evdev.ecodes.KEY_PAUSE:
                sys.exit(0)
            if str(event.code) in EVENT2BUTTON:
                joystick_button = EVENT2BUTTON[str(event.code)]
                if event.value == 1:
                    print('Key or button down', 'joystick down', joystick_button)
                    Joystick.press(joystick_button)
                elif event.value == 0:
                    print('Key or button up', 'joystick up', joystick_button)
                    Joystick.release(joystick_button)
            else:
                """ Map mouse motion to thumbstick motion """
                if event.code == evdev.ecodes.REL_X:
                    print('REL_X', event.value)
                    #Joystick.xAxis(?)
                elif event.code == evdev.ecodes.REL_Y:
                    print('REL_Y', event.value)
                    #Joystick.yAxis(?)
                elif event.code == evdev.ecodes.REL_WHEEL:
                    print('REL_WHEEL', event.value)
                elif event.code == evdev.ecodes.REL_HWHEEL:
                    print('REL_HWHEEL', event.value)
                elif event.code == evdev.ecodes.ABS_X:
                    print('ABS_X', event.value)
                elif event.code == evdev.ecodes.ABS_Y:
                    print('ABS_Y', event.value)

def main():
    """ Trigger XAC joystick with USB or BT mouse and keyboard  """

    # Examine all input devices and find keyboards and mice.
    # Process all keyboard and mouse input events.
    for devpath in evdev.list_devices():
        device = evdev.InputDevice(devpath)
        print(device)
        print(device.path, device.name, device.phys)
        print(device.capabilities(verbose=True))
        if evdev.ecodes.EV_KEY in device.capabilities():
            print('Has EV_KEY')
            print(device.capabilities()[evdev.ecodes.EV_KEY])
            if evdev.ecodes.KEY_A in device.capabilities()[evdev.ecodes.EV_KEY]:
                print('Keyboard', device)
                asyncio.ensure_future(handle_events(device))
            elif evdev.ecodes.BTN_MOUSE in device.capabilities()[evdev.ecodes.EV_KEY]:
                print('Mouse', device)
                asyncio.ensure_future(handle_events(device))

    loop = asyncio.get_event_loop()
    loop.run_forever()

if __name__ == "__main__":
    main()
