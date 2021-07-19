# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line-tracking movement using a reflected light intensity sensor.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color        # type: ignore
from pybricks.tools import wait, StopWatch, DataLog                         # type: ignore
from pybricks.robotics import DriveBase                                     # type: ignore
# pylint: enable=F0401

from .base.PIDLoop import PIDLoop

class LineEdge:           # Enum workaround (MicroPython does not support enums)
    LEFT = 0
    RIGHT = 1

class LineTrack(PIDLoop):

    def __init__(self,
                 threshold: int,
                 trackingEdge: LineEdge,
                 speed: float,
                 stopCondition,
                 sensor: ColorSensor,
                 leftMotor: Motor,
                 rightMotor: Motor,
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
        self.stopCondition = stopCondition

        # Hardware parameters
        self.sensor = sensor
        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        # PID parameters
        super().__init__(threshold, kp, ki, kd, integralLimit, outputLimit)

        self.run()

    def run(self):

        directionMultiplier = 1 if self.trackingEdge == LineEdge.LEFT else -1

        while not self.stopCondition():

            output = self.update(self.sensor.reflection() - self.threshold) * directionMultiplier

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)
