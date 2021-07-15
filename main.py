#!/usr/bin/env pybricks-micropython

# main.py
# Created on 6 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Main program.

# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color        # type: ignore
from pybricks.tools import wait, StopWatch, DataLog                         # type: ignore
from pybricks.robotics import DriveBase                                     # type: ignore
# pylint: enable=F0401

import movement
import runlogic

# TODO: Add PID tuning values
# Initialize PID settings
movement.LineTrack.setDefaultTuning(None, None, None)
movement.LineSquare.setDefaultTuning(None, None, None)
movement.GyroStraight.setDefaultTuning(None, None, None)
movement.GyroTurn.setDefaultTuning(None, None, None, None, None, None)

# Initialize hardware
brick = EV3Brick()
frontColor = ColorSensor(Port.S1)
leftColor = ColorSensor(Port.S2)
rightColor = ColorSensor(Port.S3)
gyro = GyroSensor(Port.S4)
frontClaw = Motor(Port.A)
leftMotor = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
rightMotor = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
rearClaw = Motor(Port.D)

# Constants
LEFT_THRESHOLD = 50
RIGHT_THRESHOLD = 48
