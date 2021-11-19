# DoubleColorInput.py
# Created on 27 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for ev3pid modules involving double color sensors.


from pybricks.ev3devices import ColorSensor

from .ColorInput import ColorInput                                           # pylint: disable=relative-beyond-top-level

class DoubleColorInput(ColorInput):

    DEFAULT_LEFT_COLOR = None
    DEFAULT_RIGHT_COLOR = None

    def __init__(self, leftSensor: ColorSensor, rightSensor: ColorSensor, leftThreshold: int, rightThreshold: int):

        self.leftSensor = leftSensor if leftSensor is not None else self.__class__.DEFAULT_LEFT_COLOR
        self.rightSensor = rightSensor if rightSensor is not None else self.__class__.DEFAULT_RIGHT_COLOR

        self.leftThreshold = leftThreshold if leftThreshold is not None else \
            self.__class__.checkKnownThresholds(self.leftSensor)
        self.rightThreshold = rightThreshold if rightThreshold is not None else \
            self.__class__.checkKnownThresholds(self.rightSensor)

    @classmethod
    def setDefaultSensors(cls, leftSensor: ColorSensor, rightSensor: ColorSensor):
        cls.DEFAULT_LEFT_COLOR = leftSensor
        cls.DEFAULT_RIGHT_COLOR = rightSensor
