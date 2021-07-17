# GyroStraight.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements straight-line movement using a gyroscopic sensor.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color        # type: ignore
from pybricks.tools import wait, StopWatch, DataLog                         # type: ignore
from pybricks.robotics import DriveBase                                     # type: ignore
# pylint: enable=F0401

from .PIDLoop import PIDLoop

class GyroStraight(PIDLoop):

    def __init__(self,
                 angle: int,
                 speed: float,
                 stopCondition,
                 sensor: GyroSensor,
                 leftMotor: Motor,
                 rightMotor: Motor,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

        # Angle parameters
        self.angle = angle

        # Movement parameters
        self.speed = speed
        self.stopCondition = stopCondition

        # Hardware parameters
        self.sensor = sensor
        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        # PID parameters
        super().__init__(angle, kp, ki, kd, integralLimit, outputLimit)

        self.run()

    def run(self):
        while not self.stopCondition():

            output = self.update(self.sensor.angle() - self.angle)

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)
