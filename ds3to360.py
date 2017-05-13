#!/usr/bin/env python

'''
Copyright (c) 2017 Joel Hammond

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE
'''

# Import the dozens of libraries we need
import evdev
from evdev import ecodes as ec

# Identify the DS3 device
# Only tested to work when connected via Bluez 5 on Ubuntu 16.04.
#   I have no idea if it will  work when connected via USB or legacy sixad.
ds3=None
for device in [evdev.InputDevice(fn) for fn in evdev.list_devices()]:
    if device.name == "Sony Computer Entertainment Wireless Controller":
        ds3=device
        ds3.grab()
        print "Identified DS3: "+ds3.fn
        break
if ds3 is None:
    print "DS3 Not found"
    exit(1)

# Create a Fake360 UInput Device.
# Button codes were chosen to be roughly accurate while still being placed in
#   the right order, which it turns out is a surprisingly tall order.
x360=evdev.UInput({
    ec.EV_ABS: [
        (ec.ABS_X, evdev.AbsInfo(0,0,255,1,15,0)),
        (ec.ABS_Y, evdev.AbsInfo(0,0,255,1,15,0)),
        (ec.ABS_RX, evdev.AbsInfo(0,0,255,1,15,0)),
        (ec.ABS_RY, evdev.AbsInfo(0,0,255,1,15,0)),
        (ec.ABS_HAT0X, evdev.AbsInfo(0,-1,1,0,0,0)),
        (ec.ABS_HAT0Y, evdev.AbsInfo(0,-1,1,0,0,0)),
        (ec.ABS_TILT_X, evdev.AbsInfo(0,-255,255,1,0,0)), #LT
        (ec.ABS_TILT_Y, evdev.AbsInfo(0,-255,255,1,0,0)), #RT
    ], ec.EV_KEY: [
        ec.BTN_A,
        ec.BTN_B,
        ec.BTN_X,
        ec.BTN_Y,
        ec.BTN_TL, #LB
        ec.BTN_TR, #RB
        ec.BTN_SELECT, #Back
        ec.BTN_START,
        ec.BTN_THUMBL,
        ec.BTN_THUMBR,
        ec.BTN_TRIGGER_HAPPY1, #LT
        ec.BTN_TRIGGER_HAPPY2, #RT
    ]}, "DS3 to 360", 0x3)
print "UInput device created"

# Dictionary Maps to translate DS3 input into x360 input
# You'll notice that some of the inputs are weird, including three buttons 
#   marked with only numbers.  There is no ENUM value associated with these
#   buttons, meaning the driver likely relies upon undocumented behavior.
axismap={
    ec.ABS_X: ec.ABS_X,
    ec.ABS_Y: ec.ABS_Y,
    ec.ABS_Z: ec.ABS_RX, 
    ec.ABS_RZ: ec.ABS_RY,
    ec.ABS_MT_TOUCH_MAJOR: ec.ABS_TILT_X,
    ec.ABS_MT_TOUCH_MINOR: ec.ABS_TILT_Y,
}
btnmap={
    ec.BTN_PINKIE: ec.ABS_HAT0X,
    ec.BTN_BASE2: ec.ABS_HAT0X,
    ec.BTN_TOP2: ec.ABS_HAT0Y,
    ec.BTN_BASE: ec.ABS_HAT0Y,
    302: ec.BTN_A,
    301: ec.BTN_B,
    ec.BTN_DEAD: ec.BTN_X,
    300: ec.BTN_Y,
    ec.BTN_BASE5: ec.BTN_TL,
    ec.BTN_BASE6: ec.BTN_TR,
    ec.BTN_TRIGGER: ec.BTN_SELECT,
    ec.BTN_TOP: ec.BTN_START,
    ec.BTN_THUMB: ec.BTN_THUMBL,
    ec.BTN_THUMB2: ec.BTN_THUMBR,
    ec.BTN_BASE3: ec.BTN_TRIGGER_HAPPY1,
    ec.BTN_BASE4: ec.BTN_TRIGGER_HAPPY2,
}

# The event loop
    
for event in ds3.read_loop():
    if event.type == ec.EV_ABS:
        axis=axismap.get(event.code)
        value=event.value
        if axis is not None:
            # Invert Right Y because I prefer it that way.
            if axis == ec.ABS_RY:
                value=255-value
            x360.write(event.type,axis,value)
            x360.syn()
    elif event.type == ec.EV_KEY:
        btn=btnmap.get(event.code)
        value=event.value
        # DPAD needs to be converted from four buttons to two axis pairs
        if event.code == ec.BTN_TOP2 or event.code == ec.BTN_BASE2:
            value*=-1
            event.type=ec.EV_ABS
        elif event.code == ec.BTN_PINKIE or event.code == ec.BTN_BASE:
            event.type=ec.EV_ABS
        if btn is not None:
            x360.write(event.type,btn,value)
            x360.syn()

exit(0)
# Only way to close the program is ctrl+C, or sending sigterm.
#   That's right, I'm too lazy to add a proper exit strategy. Deal with it.
