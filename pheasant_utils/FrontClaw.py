# FrontClaw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for controlling the front claw.


from .Claw import Claw

class FrontClaw(Claw):

    ANGLE_RANGE = 950
    LOAD_MULTIPLIER = 1.06
    LIFTING_THRESHOLD = 0.78

    SINGLE_LOAD_SPEED = 900
    DOUBLE_LOAD_SPEED = 700

    @classmethod
    def lift(cls):
        cls.goTo(0.83)

    @classmethod
    def drop(cls):
        cls.goTo(0.77)

    @classmethod
    def collect(cls):
        cls.goTo(0.77)

    @classmethod
    def openGate(cls):
        cls.goTo(0.07)

    @classmethod
    def closeGate(cls):
        cls.goTo(0.8)

    @classmethod
    def rubberDown(cls):
        cls.goTo(0.85)

    @classmethod
    def rubberUp(cls):
        cls.goTo(0.9)
