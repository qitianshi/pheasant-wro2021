#!/usr/bin/env pybricks-micropython

# WatchNxtColor.py
# Created on 18 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Displays the color detected by the NXT color sensor.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.nxtdevices import ColorSensor as NxtColorSensor               # type: ignore
from pybricks.parameters import Port                                        # type: ignore
from pybricks.tools import wait                                             # type: ignore
# pylint: enable=F0401

brick = EV3Brick()
sensor = NxtColorSensor(Port.S1)

while True:
    brick.screen.print(sensor.color())
    wait(50)
