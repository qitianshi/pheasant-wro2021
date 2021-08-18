# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line-tracking using a reflected light intensity sensor.


# pylint: disable=F0401
from pybricks.ev3devices import Motor, ColorSensor                          # type: ignore
# pylint: enable=F0401

from .utils.PIDLoop import PIDLoop
from .utils.ColorInput import ColorInput
from ev3move import DoubleMotorBase

class LineEdge:           # Enum workaround (MicroPython does not support enums)
    LEFT = 0
    RIGHT = 1

class LineTrack(PIDLoop, ColorInput, DoubleMotorBase):

    def __init__(self,
                 speed: float,
                 trackingEdge: LineEdge,
                 sensor: ColorSensor,
                 threshold: int = None,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

        # Movement parameters
        self.speed = speed
        self.trackingEdge = trackingEdge

        # Hardware parameters
        ColorInput.__init__(self, sensor, threshold)
        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

        # PID parameters
        PIDLoop.__init__(self, threshold, kp, ki, kd, integralLimit, outputLimit)

    def runUntil(self, stopCondition):

        directionMultiplier = 1 if self.trackingEdge == LineEdge.LEFT else -1

        while not stopCondition():

            output = self.update(self.sensor.reflection() - self.threshold) * directionMultiplier

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)
