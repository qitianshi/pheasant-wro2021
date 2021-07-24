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

from .base.PIDLoop import PIDLoop
from .base.GyroMovement import GyroMovement
from ev3move import DoubleMotorBase

class GyroStraight(PIDLoop, GyroMovement, DoubleMotorBase):

    def __init__(self,
                 angle: int,
                 speed: float,
                 stopCondition,
                 sensor: GyroSensor = None,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None,
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
        GyroMovement.__init__(self, sensor)
        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

        # PID parameters
        PIDLoop.__init__(self, angle, kp, ki, kd, integralLimit, outputLimit)

        self.run()

    def run(self):
        while not self.stopCondition():

            output = self.update(self.sensor.angle() - self.angle)

            self.leftMotor.run(self.speed - output)
            self.rightMotor.run(self.speed + output)
