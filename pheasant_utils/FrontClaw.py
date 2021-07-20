# FrontClaw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Programs for controlling the front claw.


# pylint: disable=F0401
from pybricks.ev3devices import Motor                                       # type: ignore
from pybricks.parameters import Port                                        # type: ignore
from pybricks.tools import wait                                             # type: ignore
# pylint: enable=F0401

class FrontClaw:

    MOTOR = None
    SPEED = 400
    ANGLE_RANGE = 1224                          # Use resetRaised() then resetLowered() and measure the difference in motor angle.
    LOAD_MULTIPLIER = 1.05
    LIFTING_THRESHOLD = 0.72

    loads = 0

    @classmethod
    def goTo(cls, amount: float):
        cls.MOTOR.run_target(cls.SPEED, cls.ANGLE_RANGE * amount * (1 if amount <= cls.LIFTING_THRESHOLD else cls.LOAD_MULTIPLIER ** cls.loads))
    
    @classmethod
    def lift(cls):
        cls.goTo(0.86)

    @classmethod
    def collectWind(cls):
        cls.goTo(0.82)

    @classmethod
    def drop(cls):
        cls.goTo(cls.LIFTING_THRESHOLD)

    @classmethod
    def openGate(cls):
        cls.goTo(0.2)

    @classmethod
    def closeGate(cls):
        cls.goTo(0.8)

    @classmethod
    def resetRaised(cls):

        # Quickly goes near the maximum position.
        cls.MOTOR.run_target(600, cls.ANGLE_RANGE - 100)

        # Slowly goes to the max position.
        cls.MOTOR.dc(40)                        # Outputs by duty cycle to bypass speed control.
        wait(1250)
        cls.MOTOR.hold()

        wait(50)
        cls.MOTOR.reset_angle(cls.ANGLE_RANGE)

    @classmethod
    def resetLowered(cls):
        
        # Quickly goes near the minimum position.
        cls.MOTOR.run_target(600, 100)

        # Slowly goes to the max position.
        cls.MOTOR.dc(-40)                       # Outputs by duty cycle to bypass speed control.
        wait(1250)
        cls.MOTOR.hold()

        wait(50)
        cls.MOTOR.reset_angle(0)
