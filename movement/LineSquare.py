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
    BEHIND = 1

class LineSquare(PIDLoop):

    MOVE_TO_LINE_SPEED = 250
    LINE_WAIT_TIME = 75
    THRESHOLD_TOLERANCE = 3

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

        # Before running PID loop, the robot drives forward until it reaches the line.
        while not (self.leftSensor.reflection() < self.leftThreshold and self.rightSensor.reflection() < self.rightThreshold):
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
