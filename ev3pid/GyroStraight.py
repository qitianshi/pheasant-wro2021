# GyroStraight.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements straight-line movement using a gyroscopic sensor.


# pylint: disable=F0401
from pybricks.ev3devices import Motor, GyroSensor                           # type: ignore
# pylint: enable=F0401

from .base.PIDLoop import PIDLoop
from .base.GyroInput import GyroInput
from ev3move import DoubleMotorBase

class GyroStraight(PIDLoop, GyroInput, DoubleMotorBase):

    def __init__(self,
                 speed: float,
                 angle: int,
                 sensor: GyroSensor = None,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

        # Movement parameters
        self.speed = speed
        self.angle = angle

        # Hardware parameters
        GyroInput.__init__(self, sensor)
        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

        # PID parameters
        PIDLoop.__init__(self, angle, kp, ki, kd, integralLimit, outputLimit)

    def runUntil(self, stopCondition):
        while not stopCondition():

            output = self.update(self.sensor.angle() - self.angle)

            self.leftMotor.run(self.speed - output)
            self.rightMotor.run(self.speed + output)
