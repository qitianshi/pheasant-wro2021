#!/usr/bin/env pybricks-micropython

# RunMotors.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Controls the motors using brick buttons.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor                                       # type: ignore
from pybricks.parameters import Port, Button                                # type: ignore
from pybricks.tools import wait                                             # type: ignore
# pylint: enable=F0401

SPEED = 400
brick = EV3Brick()
motors = {}

# Initializes motors.
for port, key in zip([Port.A, Port.B, Port.C, Port.D], ["A", "B", "C", "D"]):

    try:
        motor = Motor(port)
        motors[key] = motor
    except:
        print("Motor at '", port, "' not found.", sep='')

# Initial motor controls.
upDownMotor = "A"
leftRightMotor = "D"
brick.screen.draw_text(0, 0, "Running: " + upDownMotor + ', ' + leftRightMotor)

while True:

    pressedButtons = brick.buttons.pressed()

    # Toggles between A/D and B/C motor control using the center button.
    if Button.CENTER in pressedButtons:

        upDownMotor = "B" if upDownMotor == "A" else "A"
        leftRightMotor = "C" if leftRightMotor == "D" else "D"

        # Updates the screen display.
        brick.screen.clear()
        brick.screen.draw_text(0, 0, "Running: " + upDownMotor + ', ' + leftRightMotor)

        # Waits for the center button to be released.
        while Button.CENTER in brick.buttons.pressed():
            wait(50)

    # Motor control for up/down buttons
    if Button.UP in pressedButtons:
        motors[upDownMotor].run(SPEED)
    elif Button.DOWN in pressedButtons:
        motors[upDownMotor].run(SPEED * -1)
    else:
        motors[upDownMotor].stop()

    # Motor control for left/right buttons.
    if Button.LEFT in pressedButtons:
        motors[leftRightMotor].run(SPEED)
    elif Button.RIGHT in pressedButtons:
        motors[leftRightMotor].run(SPEED * -1)
    else:
        motors[leftRightMotor].stop()
