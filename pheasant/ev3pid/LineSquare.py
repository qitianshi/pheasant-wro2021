# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line alignment using two reflected light intensity sensors.


from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Color
from pybricks.tools import wait

from ev3move import DoubleMotorBase
from .utils.PIDController import PIDController
from .utils.DoubleColorInput import DoubleColorInput

class LinePosition:
    AHEAD = hash("AHEAD")               #HACK: enum workaround
    BEHIND = hash("BEHIND")

class LineSquare(PIDController, DoubleColorInput, DoubleMotorBase):

    LINE_WAIT_TIME = 75
    THRESHOLD_TOLERANCE = 1

    def __init__(self,
                 linePosition: LinePosition,
                 leftSensor: ColorSensor = None,
                 rightSensor: ColorSensor = None,
                 leftThreshold: int = None,
                 rightThreshold: int = None,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

        # Line parameters
        self.linePosition = linePosition

        # Hardware parameters
        DoubleColorInput.__init__(self, leftSensor, rightSensor, leftThreshold, rightThreshold)
        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

        # Resolves optional arguments with default values.
        kp = kp if kp is not None else LineSquare.kp_DEFAULT
        ki = ki if ki is not None else LineSquare.ki_DEFAULT
        kd = kd if kd is not None else LineSquare.kd_DEFAULT
        integralLimit = integralLimit if integralLimit is not None else LineSquare.INTEGRAL_LIMIT_DEFAULT
        outputLimit = outputLimit if outputLimit is not None else LineSquare.OUTPUT_LIMIT_DEFAULT

        # PID parameters
        self.leftPid = PIDController(leftThreshold, kp, ki, kd, integralLimit, outputLimit)
        self.rightPid = PIDController(rightThreshold, kp, ki, kd, integralLimit, outputLimit)

    def run(self):

        directionMultiplier = 1 if self.linePosition == LinePosition.AHEAD else -1

        while not (self.leftSensor.reflection() in range(self.leftThreshold - LineSquare.THRESHOLD_TOLERANCE, \
                   self.leftThreshold + LineSquare.THRESHOLD_TOLERANCE + 1) \
                   and self.rightSensor.reflection() in range(self.rightThreshold - LineSquare.THRESHOLD_TOLERANCE, \
                   self.rightThreshold + LineSquare.THRESHOLD_TOLERANCE + 1)):

            self.leftMotor.run(self.leftPid.update(self.leftSensor.reflection() - self.leftThreshold) \
                * directionMultiplier)
            self.rightMotor.run(self.rightPid.update(self.rightSensor.reflection() - self.rightThreshold) \
                * directionMultiplier)

        self.leftMotor.hold()
        self.rightMotor.hold()
        wait(LineSquare.LINE_WAIT_TIME)
