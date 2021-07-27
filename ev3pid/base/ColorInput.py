# ColorInput.py
# Created on 27 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for ev3pid modules involving a color sensor.


# pylint: disable=F0401
from pybricks.ev3devices import ColorSensor                                 # type: ignore
# pylint: enable=F0401

class ColorInput:

    KNOWN_THRESHOLDS = {}
    DEFAULT_COLOR = None

    def __init__(self, sensor, threshold):

        self.sensor = sensor if sensor != None else self.__class__.DEFAULT_COLOR
        self.threshold = threshold if threshold != None else self.__class__.thresholdSearch(sensor)

    @classmethod
    def setKnownSensorThresholds(cls, sensorThresholds):
        cls.KNOWN_THRESHOLDS.update(sensorThresholds)

    @classmethod
    def thresholdSearch(cls, sensor: ColorSensor):
        try:
            return cls.KNOWN_THRESHOLDS[sensor]
        except KeyError:
            return None
