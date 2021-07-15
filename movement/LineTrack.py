# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line-tracking movement using a reflected light intensity sensor.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase

from .PIDLoop import PIDLoop

class LineEdge:           # Enum workaround (MicroPython does not support enums).
    LEFT = 0
    RIGHT = 1

class LineTrack(PIDLoop):

    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 threshold: int,
                 trackingEdge: LineEdge,
                 speed: float,
                 stopCondition,
                 sensor: ColorSensor,
                 leftMotor: Motor,
                 rightMotor: Motor,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT):

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
        super().__init__(threshold, kp, ki, kd)

        self.run()

    def run(self):

        directionMultiplier = 1 if self.trackingEdge == LineEdge.LEFT else -1

        while not self.stopCondition():

            output = self.update(self.sensor.reflection() - self.threshold) * directionMultiplier

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)
