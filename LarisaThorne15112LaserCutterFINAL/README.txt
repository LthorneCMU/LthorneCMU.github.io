~~~~~~~~~~~~~~~~~~~~README~~~~~~~~~~~~~~~~~~~~

15-112 Final Project: LASER CUTTER
Larisa Thorne (lthorne), Section A
Last updated: 2015-12-09



This project uses:

	- Python 3
	- Tkinter, which is native with python installs
	- Pillow module, for image manipulation:
		http://pillow.readthedocs.org/en/3.0.x/installation.html
		(Type into terminal: ‘pip install Pillow’)
	- Pyserial, which is used for serial communication:
		https://pypi.python.org/pypi/pyserial
		(Download that, then can use ‘import serial’ in .py)
	- Arduino:
		https://www.arduino.cc/en/Main/Software
		(Download and copy to Applications folder)
	- Adafruit MotorShield, v2.3:
		https://learn.adafruit.com/adafruit-motor-shield-v2-for-arduino/install-software
		(Rename to ‘Adafruit_MotorShield’; put in Arduino folder)

* Note: You will also need an Arduino Uno, and the Adafruit MotorShields (and all the rest of the hardware) for this to work.



What this software does:

	(0) Load image (black and white pixels only).
	(1) Takes in image, finds locations of black pixels.
	(2) Look at black pixel locations and create a path similar to flood fill: we look in all 8 directions for another black pixel that’s not been visited, and go there. Once there are no more pixels fulfilling that requirement, go back to an earlier step and finish looking in the remaining directions.
	(3) Use this method to order the black pixel locations into a pixel path.
	(4) Create instances of Pixel class, so that each pixel path location is represented by a Pixel.
	(5) Assign ordinals: go through pixel path in order, find the corresponding Pixel, and give it a number, which is one greater than the previous Pixel.
	(6) Draw everything, including a resized original image on left, and the Pixels (which have locations on the canvas) on the right. I chose not to have a white background for the right panel so it’s easier to tell that this is happening.
	(7) Data/cut times are calculated, written/drawn as well.
	(8) When “Cut!” is selected, opens an instance of SerialComm class, which has an init which initiates the connection, and a method for sending a stringed integer (via ‘write’) out my USB to the Arduino. 
	(9) Take pixel path format it into triplets: each (%3=0)th list member is a laser on/off command (0 = off, 1 = on), (%3=1)th is an x direction, and the (%3=2) is a y direction. Feed these, one by one, via serial to Arduino as separate “move” commands.
	(10) Arduino code takes input (after initializing the connection), and checks what the value of local variable “isY” is before assigning the input value to either the steppers or laser. Similar to how step (7) works, isY=0 routes serial input to laser, isY=1 routes it to X stepper motor (on bottom shield), and isY=2 routes it to pair of Y stepper motors (on top shield). For steppers, the number inputted will be the amount of steps the motor turns (1 step = some fraction of a full revolution, depending on the stepper).
	(11) When move is complete, if we’ve just written a y direction, the corresponding pixel color changes to red and the countdown timer is decreased.
	(12) Time values are based on sleep time of serial connections (2s for start, 1.5s between movements).
	