# DoubleMotorMovement.py
# Created on 19 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for movement modules involving two motors.


# pylint: disable=F0401
from pybricks.ev3devices import Motor                                       # type: ignore
# pylint: enable=F0401

class DoubleMotorMovement:
    
    LEFT_MOTOR_DEFAULT = None
    RIGHT_MOTOR_DEFAULT = None

    def __init__(self, leftMotor: Motor, rightMotor: Motor):
        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

    @classmethod
    def setDefaultMotors(cls, leftMotor: Motor, rightMotor: Motor):
        cls.LEFT_MOTOR_DEFAULT = leftMotor
        cls.RIGHT_MOTOR_DEFAULT = rightMotor
