#!/usr/bin/env pybricks-micropython

# ResetClaws.py
# Created on 21 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Resets both claws in the upwards position for mission run.


from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Direction
from pybricks.tools import wait

Motor(Port.A).dc(40)
Motor(Port.D, positive_direction=Direction.COUNTERCLOCKWISE).dc(40)
wait(3000)
