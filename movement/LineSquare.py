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

    def __init__(self,
                 leftThreshold: int,
                 rightThreshold: int,
                 linePosition: LinePosition,
                 leftSensor: ColorSensor,
                 rightSensor: ColorSensor,
                 leftMotor: Motor,
                 rightMotor: Motor,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

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
        self.leftPid = PIDLoop(leftThreshold,
                               kp if kp != None else LineSquare.kp_DEFAULT,
                               ki if ki != None else LineSquare.ki_DEFAULT,
                               kd if kd != None else LineSquare.kd_DEFAULT,
                               integralLimit if integralLimit != None else LineSquare.INTEGRAL_LIMIT_DEFAULT,
                               outputLimit if outputLimit != None else LineSquare.OUTPUT_LIMIT_DEFAULT)
        self.rightPid = PIDLoop(rightThreshold,
                               kp if kp != None else LineSquare.kp_DEFAULT,
                               ki if ki != None else LineSquare.ki_DEFAULT,
                               kd if kd != None else LineSquare.kd_DEFAULT,
                               integralLimit if integralLimit != None else LineSquare.INTEGRAL_LIMIT_DEFAULT,
                               outputLimit if outputLimit != None else LineSquare.OUTPUT_LIMIT_DEFAULT)

        self.run()

    def run(self):

        directionMultiplier = 1 if self.linePosition == LinePosition.AHEAD else -1
        
        while not ((self.leftSensor.reflection() == self.leftThreshold and self.leftMotor.speed() == 0) and (self.rightSensor.reflection() == self.rightThreshold and self.rightMotor.speed() == 0)):

            self.leftMotor.run(self.leftPid.update(self.leftSensor.reflection() - self.leftThreshold) * directionMultiplier)
            self.rightMotor.run(self.rightPid.update(self.rightSensor.reflection() - self.rightThreshold) * directionMultiplier)
