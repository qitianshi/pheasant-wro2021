# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line-tracking using a reflected light intensity sensor.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color        # type: ignore
from pybricks.tools import wait, StopWatch, DataLog                         # type: ignore
from pybricks.robotics import DriveBase                                     # type: ignore
# pylint: enable=F0401

from .base.PIDLoop import PIDLoop
from ev3move import DoubleMotorBase

class LineEdge:           # Enum workaround (MicroPython does not support enums)
    LEFT = 0
    RIGHT = 1

class LineTrack(PIDLoop, DoubleMotorBase):

    def __init__(self,
                 threshold: int,
                 trackingEdge: LineEdge,
                 speed: float,
                 sensor: ColorSensor,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

        # Line parameters
        self.threshold = threshold
        self.trackingEdge = trackingEdge

        # Movement parameters
        self.speed = speed

        # Hardware parameters
        self.sensor = sensor
        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

        # PID parameters
        super().__init__(threshold, kp, ki, kd, integralLimit, outputLimit)

    def runUntil(self, stopCondition):

        directionMultiplier = 1 if self.trackingEdge == LineEdge.LEFT else -1

        while not stopCondition():

            output = self.update(self.sensor.reflection() - self.threshold) * directionMultiplier

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)
