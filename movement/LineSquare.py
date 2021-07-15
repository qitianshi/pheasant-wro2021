# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line alignment using two reflected light intensity sensors.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color        # type: ignore
from pybricks.tools import wait, StopWatch, DataLog                         # type: ignore
from pybricks.robotics import DriveBase                                     # type: ignore
# pylint: enable=F0401

from .PIDLoop import PIDLoop

class LinePosition:
    AHEAD = 0
    BEHIND = 0

class LineSquare(PIDLoop):

    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 leftThreshold: int,
                 rightThreshold: int,
                 linePosition: LinePosition,
                 leftSensor: ColorSensor,
                 rightSensor: ColorSensor,
                 leftMotor: Motor,
                 rightMotor: Motor,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT):

        # Line parameters
        self.leftThreshold = leftThreshold
        self.rightThreshold = rightThreshold
        self.linePosition = linePosition

        # Hardware parameters
        self.leftSensor = leftSensor
        self.rightSensor = rightSensor
        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        # PID parameters
        self.leftPid = PIDLoop(leftThreshold, kp, ki, kd)
        self.rightPid = PIDLoop(rightThreshold, kp, ki, kd)

        self.run()

    def run(self):

        directionMultiplier = 1 if self.linePosition == LinePosition.AHEAD else -1
        
        while not ((self.leftSensor.reflection() == self.leftThreshold and self.leftMotor.speed() == 0) and (self.rightSensor.reflection() == self.rightThreshold and self.rightMotor.speed() == 0)):

            leftMotor.run(leftPid.update() * directionMultiplier)
            rightMotor.run(rightPid.update() * directionMultiplier)
