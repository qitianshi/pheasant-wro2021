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

from .PIDLoop import PIDLoop

class GyroTurn(PIDLoop):

    # Different tuning values depending on the number of wheels being driven for turning.
    kp_SINGLE_DEFAULT = None
    ki_SINGLE_DEFAULT = None
    kd_SINGLE_DEFAULT = None
    kp_DOUBLE_DEFAULT = None
    ki_DOUBLE_DEFAULT = None
    kd_DOUBLE_DEFAULT = None

    def __init__(self,
                 angle: int,
                 leftDriven: bool,
                 rightDriven: bool,
                 sensor: GyroSensor,
                 leftMotor: Motor,
                 rightMotor: Motor,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None):

        # Angle parameters
        self.angle = angle

        # Movement parameters
        self.leftDriven = leftDriven
        self.rightDriven = rightDriven

        # Hardware parameters
        self.sensor = sensor
        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        # PID parameters
        if leftDriven and rightDriven:
            super().__init__(angle, GyroTurn.kp_DOUBLE_DEFAULT, GyroTurn.ki_DOUBLE_DEFAULT, GyroTurn.kd_DOUBLE_DEFAULT)
        else:
            super().__init__(angle, GyroTurn.kp_SINGLE_DEFAULT, GyroTurn.ki_SINGLE_DEFAULT, GyroTurn.kd_SINGLE_DEFAULT)

        self.run()

    def run(self):

        while not (self.sensor.angle() == self.angle and self.leftMotor.speed() == 0 and self.rightMotor().speed == 0):

            output = self.update(self.sensor.angle() - self.angle)

            self.leftMotor.run(self.leftDriven * output)
            self.rightMotor.run(self.rightDriven * output * -1)

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
