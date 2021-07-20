# FrontClaw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for controlling the front claw.


# pylint: disable=F0401
from pybricks.ev3devices import Motor                                       # type: ignore
from pybricks.tools import wait                                             # type: ignore
# pylint: enable=F0401

from .Claw import Claw

class FrontClaw(Claw):

    ANGLE_RANGE = 1224                          
    LOAD_MULTIPLIER = 1.05
    LIFTING_THRESHOLD = 0.72
    
    @classmethod
    def lift(cls):
        cls.goTo(0.86)

    @classmethod
    def collect(cls):
        cls.goTo(0.82)

    @classmethod
    def openGate(cls):
        cls.goTo(0.2)

    @classmethod
    def closeGate(cls):
        cls.goTo(0.8)
