#!/usr/bin/env pybricks-micropython

# WatchNxtColor.py
# Created on 18 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Displays the color detected by the NXT color sensor.


from pybricks.hubs import EV3Brick
from pybricks.nxtdevices import ColorSensor as NxtColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait

brick = EV3Brick()
sensor = NxtColorSensor(Port.S1)

while True:
    brick.screen.print(sensor.color())
    wait(50)
