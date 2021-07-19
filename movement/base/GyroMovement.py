# GyroMovement.py
# Created on 19 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for movement modules involving the gyro sensor.


# pylint: disable=F0401
from pybricks.ev3devices import GyroSensor                                  # type: ignore
# pylint: enable=F0401

class GyroMovement:
    
    DEFAULT_GYRO = None

    @classmethod
    def setDefaultGyro(cls, sensor: GyroSensor):
        cls.DEFAULT_GYRO = sensor
