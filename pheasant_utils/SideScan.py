# SideScan.py
# Created on 19 Aug 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for scanning block color and presence using the side color sensor.


from pybricks.iodevices import Ev3devSensor                                              # pylint: disable=unused-import
from pybricks.parameters import Color

class SideScan:

    sensor = None

    @classmethod
    def color(cls):

        r, g, b = cls.sensor.read('RGB-RAW')

        if r - b >= 3 and r - g >= 3:
            return Color.YELLOW
        if b - r >= 3 and b - g >= 3:
            return Color.BLUE
        if g - r >= 3 and g - b >= 3:
            return Color.GREEN

    @classmethod
    def presence(cls):
        r, g, b = cls.sensor.read('RGB-RAW')
        return r + g + b > 15
