# FrontClaw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for controlling the front claw.


# pylint: disable=F0401
from pybricks.ev3devices import Motor                                       # type: ignore
# pylint: enable=F0401

class FrontClaw:

    MOTOR = None
    SPEED = 400
    
    @classmethod
    def lift(cls):
        pass

    @classmethod
    def lower(cls):
        pass

    @classmethod
    def resetMax(cls):
        pass

    @classmethod
    def resetMin(cls):
        pass

    @classmethod
    def openGate(cls):
        pass
