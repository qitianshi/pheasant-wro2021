# RearClaw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for controlling the rear claw.


from .Claw import Claw

class RearClaw(Claw):

    ANGLE_RANGE = 310
    LOAD_MULTIPLIER = 1.1
    LIFTING_THRESHOLD = 0.25

    SINGLE_LOAD_SPEED = 400
    DOUBLE_LOAD_SPEED = 300

    @classmethod
    def lift(cls):
        cls.goTo(0.52)

    @classmethod
    def collect(cls):
        cls.goTo(0.31)
