# DoubleMotorBase.py
# Created on 19 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for ev3move modules involving two motors.


# pylint: disable=F0401
from pybricks.ev3devices import Motor                                       # type: ignore
# pylint: enable=F0401

class DoubleMotorBase:

    LEFT_MOTOR_DEFAULT = None
    RIGHT_MOTOR_DEFAULT = None

    def __init__(self, leftMotor: Motor, rightMotor: Motor):

        # Resolves optional arguments with default values.
        self.leftMotor = leftMotor if leftMotor != None else self.__class__.LEFT_MOTOR_DEFAULT
        self.rightMotor = rightMotor if rightMotor != None else self.__class__.RIGHT_MOTOR_DEFAULT

    @classmethod
    def setDefaultMotors(cls, leftMotor: Motor, rightMotor: Motor):
        cls.LEFT_MOTOR_DEFAULT = leftMotor
        cls.RIGHT_MOTOR_DEFAULT = rightMotor
