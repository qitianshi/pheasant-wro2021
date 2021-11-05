# FrontClaw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for controlling the front claw.


from .Claw import Claw

class FrontClaw(Claw):

    ANGLE_RANGE = 950
    LOAD_MULTIPLIER = 1.055
    LIFTING_THRESHOLD = 0.78

    SINGLE_LOAD_SPEED = 900
    DOUBLE_LOAD_SPEED = 700

    @classmethod
    def lift(cls):
        cls.goTo(0.79)

    @classmethod
    def drop(cls):
        cls.goTo(0.74)

    @classmethod
    def collect(cls):
        cls.drop()

    @classmethod
    def openGate(cls):
        cls.goTo(0.02)

    @classmethod
    def closeGate(cls):
        cls.goTo(0.78)

    @classmethod
    def rubberDown(cls):
        cls.goTo(0.85)

    @classmethod
    def rubberUp(cls):
        cls.goTo(0.9)
