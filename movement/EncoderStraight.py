# EncoderStraight.py
# Created on 12 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements straight-line movement using a motor encoder.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase

from .PIDLoop import PIDLoop

class EncoderStraight(PIDLoop):

    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 speed: float,
                 stopCondition,
                 leftMotor,
                 rightMotor,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT):

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

            output = self.update(self.leftMotor.angle() - self.rightMotor.angle())

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)
