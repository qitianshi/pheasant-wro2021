# GyroStraight.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements straight-line movement using a gyroscopic sensor.


from pybricks.ev3devices import Motor, GyroSensor

from ev3move import DoubleMotorBase
from .utils.PIDController import PIDController
from .utils.GyroInput import GyroInput

class GyroStraight(PIDController, GyroInput, DoubleMotorBase):

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
        PIDController.__init__(self, angle, kp, ki, kd, integralLimit, outputLimit)

    def runUntil(self, stopCondition):
        while not stopCondition():

            output = self.update(self.sensor.angle() - self.angle)

            self.leftMotor.run(self.speed - output)
            self.rightMotor.run(self.speed + output)

    def rawControllerOutput(self):
        return self.update(self.sensor.angle() - self.angle)
