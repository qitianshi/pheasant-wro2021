# Claw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base clase for claws.


from pybricks.ev3devices import Motor                                                     #pylint: disable=unused-import
from pybricks.tools import wait

class Claw:

    ANGLE_RANGE = None              # Use resetRaised() then resetLowered() and measure the difference in motor angle.
    LOAD_MULTIPLIER = None
    LIFTING_THRESHOLD = None

    SINGLE_LOAD_SPEED = None         # Speeds defined in subclasses.
    DOUBLE_LOAD_SPEED = None

    MOTOR = None

    loads = 0

    @classmethod
    def goTo(cls, amount: float):
        cls.MOTOR.run_target((cls.SINGLE_LOAD_SPEED if cls.loads < 2 else cls.DOUBLE_LOAD_SPEED), \
            cls.ANGLE_RANGE * amount * (1 if amount <= cls.LIFTING_THRESHOLD else cls.LOAD_MULTIPLIER ** cls.loads))

    @classmethod
    def drop(cls):
        cls.goTo(cls.LIFTING_THRESHOLD)

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

    @classmethod
    def measureAngleRange(cls, moveTime):

        """
        Measures the ANGLE_RANGE of the claw (for testing only).
        """

        print("-" * 10, "Begin measureAngleRange", sep='\n')

        results = []
        print("Full results:", end=' ')

        for _ in range(10):

            cls.MOTOR.dc(-40)
            wait(moveTime)
            cls.MOTOR.hold()
            wait(1000)

            cls.MOTOR.reset_angle(0)

            cls.MOTOR.dc(40)
            wait(moveTime)
            cls.MOTOR.hold()
            wait(1000)

            results.append(cls.MOTOR.angle())
            print(results[-1], end=' ')

        print("\nAverage:", sum(results) / 10)
