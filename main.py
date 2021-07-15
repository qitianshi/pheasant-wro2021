#!/usr/bin/env pybricks-micropython

# main.py
# Created on 6 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Main program.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase

import movement
import runlogic

# TODO: Add PID tuning values
# Initialize PID settings
movement.LineTrack.setDefaultTuning(None, None, None)
movement.LineSquare.setDefaultTuning(None, None, None)
movement.GyroStraight.setDefaultTuning(None, None, None)
movement.GyroTurn.setDefaultTuning(None, None, None)

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
