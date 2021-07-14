# GyroTurn.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements turning by angle using a gyroscopic sensor.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.iodevices import Ev3devSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase

from .GyroStraight import GyroStraight

class GyroTurn(GyroStraight):

    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 angle: int,
                 sensor: GyroSensor,
                 leftMotor: Motor,
                 rightMotor: Motor,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT):

        # Lambda expression for stop condition may need to be modified for its margin of error.
        stopCondition = lambda: sensor.angle() == angle and leftMotor.speed() == 0 and rightMotor().speed == 0

        super().__init__(angle, 0, stopCondition, sensor, leftMotor, rightMotor, kp, ki, kd)
