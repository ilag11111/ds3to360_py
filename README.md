# ds3to360_py
I wrote this script so that I could use my DualShock 3 controller to play Saint's Row 2.  It might be useful to other people or for other games, so I decided to throw it up here and just see what happens.

## Usage
* Be running an up to date Linux with Bluez 5.
* Get python-evdev.  Use pip, package manager, voodoo rituals, whatever you want.
* Connect your DualShock 3 controller via bluetooth.
* python ds3to360.py
* If necessary, disable the native DualShock 3 entries in wine control.

## Backstory

Saint's Row 2 is a very interesting PC port.  It's an annoying buggy mess which manages to crash more often than a heavily-modded Bethesda game.  The PC port is so bad that they didn't even bother releasing the DLC for it.  And yet for some bizarre reason, many years later they came out with a Linux port of the PC port.  Unfortunately GOG only has the PC version and not the Linux version, so I'm stuck with using Wine.  Somehow this did not make a lick of a difference for my project that I can tell.

Like many PC games, Saint's Row 2 is designed to only support the 360 controller.  The Problem is, it doesn't properly use the XInput library, and any game controller plugged in will have their inputs mapped as though it's a 360 controller.  With the DualShock 3, every single button is pressure sensitive, the sort order of axes and buttons is completely different, and the dpad is handled as buttons rather than a HAT.  Because the controller is so different than expected, The game completely spazzes out and becomes literally unplayable as long as the controller is connected.

This script works around the spazzing out by creating a new virtual controller mapped close enough to the 360 controller that the game functions as intended with no further ingame remapping needed.
