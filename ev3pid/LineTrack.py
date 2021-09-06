# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line-tracking using a reflected light intensity sensor.


from pybricks.ev3devices import Motor, ColorSensor

from .utils.PIDController import PIDController
from .utils.ColorInput import ColorInput
from ev3move import DoubleMotorBase

# The edge of the black line that the sensor follows.
class LineEdge:
    LEFT = hash("LineEdge.LEFT")        # HACK: Enum workaround.
    RIGHT = hash("LineEdge.RIGHT")

class LineTrack(PIDController, ColorInput, DoubleMotorBase):

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
        PIDController.__init__(self, threshold, kp, ki, kd, integralLimit, outputLimit)

    def runUntil(self, stopCondition):
        while not stopCondition():

            output = self.update(self.sensor.reflection() - self.threshold) * \
                (1 if self.trackingEdge == LineEdge.LEFT else -1)

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)

    def rawControllerOutput(self):
        return self.update(self.sensor.reflection() - self.threshold) * \
            (1 if self.trackingEdge == LineEdge.LEFT else -1)
