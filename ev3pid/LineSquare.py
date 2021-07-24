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

from .base.PIDLoop import PIDLoop
from ev3move import DoubleMotorBase

class LinePosition:
    AHEAD = 0
    BEHIND = 1

class LineSquare(PIDLoop, DoubleMotorBase):

    MOVE_TO_LINE_SPEED = 250
    LINE_WAIT_TIME = 75
    LINE_COLOR = Color.BLACK
    THRESHOLD_TOLERANCE = 2

    def __init__(self,
                 leftThreshold: int,
                 rightThreshold: int,
                 linePosition: LinePosition,
                 leftSensor: ColorSensor,
                 rightSensor: ColorSensor,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

        # Resolves optional arguments with default values.
        kp = kp if kp != None else LineSquare.kp_DEFAULT
        ki = ki if ki != None else LineSquare.ki_DEFAULT
        kd = kd if kd != None else LineSquare.kd_DEFAULT
        integralLimit = integralLimit if integralLimit != None else LineSquare.INTEGRAL_LIMIT_DEFAULT
        outputLimit = outputLimit if outputLimit != None else LineSquare.OUTPUT_LIMIT_DEFAULT

        # Line parameters
        self.leftThreshold = leftThreshold
        self.rightThreshold = rightThreshold
        self.linePosition = linePosition

        # Hardware parameters
        self.leftSensor = leftSensor
        self.rightSensor = rightSensor
        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

        # PID parameters
        self.leftPid = PIDLoop(leftThreshold, kp, ki, kd, integralLimit, outputLimit)
        self.rightPid = PIDLoop(rightThreshold, kp, ki, kd, integralLimit, outputLimit)

    def runUntil(self):

        directionMultiplier = 1 if self.linePosition == LinePosition.AHEAD else -1

        # Before running PID loop, the robot drives forward until it reaches the line.
        while not (self.leftSensor.color() == LineSquare.LINE_COLOR and self.rightSensor.color() == LineSquare.LINE_COLOR):
            self.leftMotor.run(LineSquare.MOVE_TO_LINE_SPEED * directionMultiplier)
            self.rightMotor.run(LineSquare.MOVE_TO_LINE_SPEED * directionMultiplier)
        self.leftMotor.hold()
        self.rightMotor.hold()
        wait(LineSquare.LINE_WAIT_TIME)        # Stops for a short time to allow the motors to settle.

        while not (self.leftSensor.reflection() in range(self.leftThreshold - LineSquare.THRESHOLD_TOLERANCE, self.leftThreshold + LineSquare.THRESHOLD_TOLERANCE + 1) and self.rightSensor.reflection() in range(self.rightThreshold - LineSquare.THRESHOLD_TOLERANCE, self.rightThreshold + LineSquare.THRESHOLD_TOLERANCE + 1)):

            self.leftMotor.run(self.leftPid.update(self.leftSensor.reflection() - self.leftThreshold) * directionMultiplier)
            self.rightMotor.run(self.rightPid.update(self.rightSensor.reflection() - self.rightThreshold) * directionMultiplier)

        self.leftMotor.hold()
        self.rightMotor.hold()
        wait(LineSquare.LINE_WAIT_TIME)
