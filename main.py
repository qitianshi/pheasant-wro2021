#!/usr/bin/env pybricks-micropython

# main.py
# Created on 6 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Main program.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.nxtdevices import ColorSensor as NxtColorSensor               # type: ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color        # type: ignore
from pybricks.tools import wait, StopWatch, DataLog                         # type: ignore
from pybricks.robotics import DriveBase                                     # type: ignore
# pylint: enable=F0401

import movement
import runlogic

# Initialize PID settings
movement.LineTrack.setDefaultTuning(1.8, 0.0002, 1)
movement.LineTrack.setDefaultIntegralLimit(50)
movement.LineSquare.setDefaultTuning(20, 0, 10000000)
movement.LineSquare.setDefaultOutputLimit(60)
movement.GyroStraight.setDefaultTuning(22, 0.2, 10000000)
movement.GyroStraight.setDefaultIntegralLimit(100)
movement.GyroStraight.setDefaultOutputLimit(1000)
movement.GyroTurn.setDefaultTuning(23, 0, 10000000, 12, 0, 10000000)

# Initialize hardware
brick = EV3Brick()
frontColor = NxtColorSensor(Port.S1)
leftColor = ColorSensor(Port.S2)
rightColor = ColorSensor(Port.S3)
gyro = GyroSensor(Port.S4)
# frontClaw = Motor(Port.A)
leftMotor = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
rightMotor = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
rearClaw = Motor(Port.D)

# Constants
LEFT_THRESHOLD = 47
RIGHT_THRESHOLD = 48

movement.LineTrack(LEFT_THRESHOLD, movement.LineEdge.RIGHT, 1000, lambda: False, leftColor, leftMotor, rightMotor)
