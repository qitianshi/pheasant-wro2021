# FrontClaw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for controlling the front claw.


from .Claw import Claw

class FrontClaw(Claw):

    ANGLE_RANGE = 950
    LOAD_MULTIPLIER = 1.03
    LIFTING_THRESHOLD = 0.78

    SINGLE_LOAD_SPEED = 900
    DOUBLE_LOAD_SPEED = 700

    @classmethod
    def lift(cls, wait: bool = True):
        if cls.loads > 0:
            cls.goTo(0.81, wait)
        else:
            cls.closeGate(wait)

    @classmethod
    def drop(cls, wait: bool = True):
        cls.goTo(0.74, wait)

    @classmethod
    def collect(cls, wait: bool = True):
        cls.drop(wait)

    @classmethod
    def openGate(cls, wait: bool = True):
        cls.goTo(0.02, wait)

    @classmethod
    def closeGate(cls, wait: bool = True):
        cls.goTo(0.66, wait)

    @classmethod
    def rubberDown(cls, wait: bool = True):
        cls.goTo(0.83, wait)

    @classmethod
    def rubberUp(cls, wait: bool = True):
        cls.goTo(0.9, wait)
