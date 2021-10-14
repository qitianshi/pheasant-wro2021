# GyroInput.py
# Created on 19 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for ev3pid modules involving a gyro sensor.


from pybricks.ev3devices import GyroSensor

class GyroInput:

    DEFAULT_GYRO = None

    def __init__(self, sensor: GyroSensor):

        # Resolves optional arguments with default values.
        self.sensor = sensor if sensor is not None else self.__class__.DEFAULT_GYRO

    @classmethod
    def setDefaultSensor(cls, sensor: GyroSensor):
        cls.DEFAULT_GYRO = sensor
