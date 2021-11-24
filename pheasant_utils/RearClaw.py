# RearClaw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for controlling the rear claw.


from .Claw import Claw

class RearClaw(Claw):

    ANGLE_RANGE = 310
    LOAD_MULTIPLIER = 1.09
    LIFTING_THRESHOLD = 0.27

    SINGLE_LOAD_SPEED = 250
    DOUBLE_LOAD_SPEED = 150

    @classmethod
    def lift(cls, wait: bool = True):
        cls.goTo(0.39, wait)

    @classmethod
    def drop(cls, wait: bool = True):
        cls.goTo(0.21, wait)

    @classmethod
    def collect(cls, wait: bool = True):
        cls.goTo(0.34, wait)

    @classmethod
    def openGate(cls, wait: bool = True):
        cls.MOTOR.run_target((cls.SINGLE_LOAD_SPEED if cls.loads < 2 else cls.DOUBLE_LOAD_SPEED), \
            cls.ANGLE_RANGE * 0.65, wait=wait)                                  # To bypass load multiplier.

    @classmethod
    def closeGate(cls, wait: bool = True):
        cls.MOTOR.run_target((cls.SINGLE_LOAD_SPEED if cls.loads < 2 else cls.DOUBLE_LOAD_SPEED),
            cls.ANGLE_RANGE * 0.44, wait=wait)                                  # To bypass load multiplier.
