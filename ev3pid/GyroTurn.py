# GyroTurn.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements turning by angle using a gyroscopic sensor.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color        # type: ignore
from pybricks.tools import wait, StopWatch, DataLog                         # type: ignore
from pybricks.robotics import DriveBase                                     # type: ignore
# pylint: enable=F0401

from .base.PIDLoop import PIDLoop
from .base.GyroMovement import GyroMovement
from ev3move import DoubleMotorBase

class GyroTurn(PIDLoop, GyroMovement, DoubleMotorBase):

    # Different tuning values used depending on the number of wheels being driven for turning.

    # For single motor turning
    kp_SINGLE_DEFAULT = None
    ki_SINGLE_DEFAULT = None
    kd_SINGLE_DEFAULT = None
    INTEGRAL_LIMIT_SINGLE_DEFAULT = None
    OUTPUT_LIMIT_SINGLE_DEFAULT = None

    # For double motor turning
    kp_DOUBLE_DEFAULT = None
    ki_DOUBLE_DEFAULT = None
    kd_DOUBLE_DEFAULT = None
    INTEGRAL_LIMIT_DOUBLE_DEFAULT = None
    OUTPUT_LIMIT_DOUBLE_DEFAULT = None

    def __init__(self,
                 angle: int,
                 leftDriven: bool,
                 rightDriven: bool,
                 sensor: GyroSensor = None,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

        # Resolves optional arguments with default values.
        if leftDriven and rightDriven:
            kp = kp if kp != None else GyroTurn.kp_DOUBLE_DEFAULT
            ki = ki if ki != None else GyroTurn.ki_DOUBLE_DEFAULT
            kd = kd if kd != None else GyroTurn.kd_DOUBLE_DEFAULT
            integralLimit = integralLimit if integralLimit != None else GyroTurn.INTEGRAL_LIMIT_DOUBLE_DEFAULT
            outputLimit = outputLimit if outputLimit != None else GyroTurn.OUTPUT_LIMIT_DOUBLE_DEFAULT
        else:
            kp = kp if kp != None else GyroTurn.kp_SINGLE_DEFAULT
            ki = ki if ki != None else GyroTurn.ki_SINGLE_DEFAULT
            kd = kd if kd != None else GyroTurn.kd_SINGLE_DEFAULT
            integralLimit = integralLimit if integralLimit != None else GyroTurn.INTEGRAL_LIMIT_SINGLE_DEFAULT
            outputLimit = outputLimit if outputLimit != None else GyroTurn.OUTPUT_LIMIT_SINGLE_DEFAULT

        # Angle parameters
        self.angle = angle

        # Movement parameters
        self.leftDriven = leftDriven
        self.rightDriven = rightDriven

        # Hardware parameters
        GyroMovement.__init__(self, sensor)
        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

        # PID parameters
        super().__init__(angle, kp, ki, kd, integralLimit, outputLimit)

        self.run()

    def run(self):

        while not (self.sensor.angle() == self.angle and self.leftMotor.speed() == 0 and self.rightMotor.speed() == 0):

            output = self.update(self.sensor.angle() - self.angle)

            self.leftMotor.run(self.leftDriven * output * -1)
            self.rightMotor.run(self.rightDriven * output)

        self.leftMotor.hold()
        self.rightMotor.hold()

    @classmethod
    def setDefaultTuning(cls,
                         kpSingle: float,
                         kiSingle: float,
                         kdSingle: float,
                         kpDouble: float,
                         kiDouble: float,
                         kdDouble: float):

        cls.kp_SINGLE_DEFAULT = kpSingle
        cls.ki_SINGLE_DEFAULT = kiSingle
        cls.kd_SINGLE_DEFAULT = kdSingle
        
        cls.kp_DOUBLE_DEFAULT = kpDouble
        cls.ki_DOUBLE_DEFAULT = kiDouble
        cls.kd_DOUBLE_DEFAULT = kdDouble

    @classmethod
    def setDefaultIntegralLimit(cls, limitSingle: float, limitDouble: float):
        cls.INTEGRAL_LIMIT_SINGLE_DEFAULT = limitSingle
        cls.INTEGRAL_LIMIT_DOUBLE_DEFAULT = limitDouble

    @classmethod
    def setDefaultOutputLimit(cls, limitSingle: float, limitDouble: float):
        cls.OUTPUT_LIMIT_SINGLE_DEFAULT = limitSingle
        cls.OUTPUT_LIMIT_DOUBLE_DEFAULT = limitDouble
