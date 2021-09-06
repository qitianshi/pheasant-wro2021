# ColorInput.py
# Created on 27 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for ev3pid modules involving a color sensor.


from pybricks.ev3devices import ColorSensor


# TODO: Implement this. It's proposed that the port ID of the sensor be used to create the hash, but it's not
#       immediately obvious how to accesss it.
# Extends pybricks.ev3devices.ColorSensor class with __hash__ method to enable its use as a dictionary key.
# class ev3ColorSensorHashabilityExtension(ColorSensor):

#     def __hash__(self):
#         pass

class ColorInput:

    # HACK: This is a workaround. It should ideally be a dictionary with ColorSensor instances as the key and threshold
    #       being the value.
    # A 2D array containing length-2 subarrays, the first element being a ColorSensor instance and the second being the
    # threshold.
    KNOWN_THRESHOLDS = []

    DEFAULT_COLOR = None

    def __init__(self, sensor, threshold):

        self.sensor = sensor if sensor != None else self.__class__.DEFAULT_COLOR
        self.threshold = threshold if threshold != None else self.__class__.checkKnownThresholds(self.sensor)

    @classmethod
    def setDefaultSensor(cls, sensor: ColorSensor):
        cls.DEFAULT_COLOR = sensor

    @classmethod
    def setKnownThresholds(cls, sensorThresholds):

        #TODO: Add functionality to allow overwriting known thresholds.

        cls.KNOWN_THRESHOLDS.extend(sensorThresholds)

    @classmethod
    def checkKnownThresholds(cls, sensor: ColorSensor):

        # HACK: Inelegant implementation.

        knownSensors = [i[0] for i in cls.KNOWN_THRESHOLDS]

        if sensor in knownSensors:
            return cls.KNOWN_THRESHOLDS[knownSensors.index(sensor)][1]
        else:
            return None

        # try:
        #     return cls.KNOWN_THRESHOLDS[sensor]
        # except KeyError:
        #     return None
