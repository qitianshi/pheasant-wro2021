# GyroStraight.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements straight-line movement using a gyroscopic sensor.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase

from .PIDLoop import PIDLoop

class GyroStraight(PIDLoop):

    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 angle: int,
                 speed: float,
                 stopCondition,
                 sensor: GyroSensor,
                 leftMotor: Motor,
                 rightMotor: Motor,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT):

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
        super().__init__(angle, kp, ki, kd)

        self.__run()

    def __run(self):
        while not self.stopCondition():
            
            output = self.update(self.sensor.angle() - self.angle)

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)
