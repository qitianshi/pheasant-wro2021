# ColorInput.py
# Created on 27 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for ev3pid modules involving a color sensor.


# pylint: disable=F0401
from pybricks.ev3devices import ColorSensor                                 # type: ignore
# pylint: enable=F0401

class ColorInput:

    knownThresholds = {}

    @classmethod
    def setDefaultSensorThreshold(cls, sensorThresholds):
        cls.knownThresholds.update(sensorThresholds)

    @classmethod
    def thresholdSearch(cls, sensor: ColorSensor):
        try:
            return cls.knownThresholds[sensor]
        except KeyError:
            return None
