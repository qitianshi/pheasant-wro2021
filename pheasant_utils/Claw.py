# Claw.py
# Created on 20 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base clase for claws.


from pybricks.ev3devices import Motor                                                     #pylint: disable=unused-import
from pybricks.tools import wait

class Claw:

    ANGLE_RANGE = None               # Use measureAngleRange() to find angle range.
    LOAD_MULTIPLIER = None
    LIFTING_THRESHOLD = None

    SINGLE_LOAD_SPEED = None         # Speeds defined in subclasses.
    DOUBLE_LOAD_SPEED = None

    MOTOR: Motor = None

    loads = 0

    @classmethod
    def goTo(cls, amount: float):
        cls.MOTOR.run_target((cls.SINGLE_LOAD_SPEED if cls.loads < 2 else cls.DOUBLE_LOAD_SPEED), \
            cls.ANGLE_RANGE * amount * (1 if amount <= cls.LIFTING_THRESHOLD else cls.LOAD_MULTIPLIER ** cls.loads))

    @classmethod
    def maximum(cls):
        cls.MOTOR.dc(50)

    @classmethod
    def minimum(cls):
        cls.MOTOR.dc(-50)

    @classmethod
    def measureAngleRange(cls, moveTime):

        """
        Measures the ANGLE_RANGE of the claw (for testing only).
        """

        #FIXME: The motor occasionally fails to move for an unknown reason. A workaround is currently implemented to
        #       skip erroneous results.

        results = []
        print("Full results:", end=' ')

        while len(results) < 10:

            cls.MOTOR.dc(-40)
            wait(moveTime)
            cls.MOTOR.hold()
            wait(1000)

            cls.MOTOR.reset_angle(0)

            cls.MOTOR.dc(40)
            wait(moveTime)
            cls.MOTOR.hold()
            wait(1000)

            angle = cls.MOTOR.angle()
            if angle != 0:                      # Skips erroneous results (see fixme above).
                results.append(angle)
                print(results[-1], end=' ')

        print("\nAverage:", sum(results) / len(results))
