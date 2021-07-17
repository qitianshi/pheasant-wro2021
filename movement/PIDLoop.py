# PIDLoop.py
# Created on 7 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base clase for PID-based control systems.


class PIDLoop:

    INTEGRAL_LIMIT = None
    OUTPUT_LIMIT = None

    def __init__(self,
                 setpoint: int,
                 kp: float,
                 ki: float,
                 kd: float):

        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.prevError = 0
        self.integral = 0

    def update(self, error: float) -> float:

        # Proportional term
        pTerm = error * self.kp

        # Integral term
        self.integral += error
        iTerm = self.integral * self.ki
        if self.__class__.INTEGRAL_LIMIT != None:       # Applies integral limit, if set.
            self.integral = min(self.integral, self.__class__.INTEGRAL_LIMIT)
            self.integral = max(self.integral, self.__class__.INTEGRAL_LIMIT * -1)

        # Differential term
        dTerm = (error - self.prevError) * self.kd

        self.prevError = error

        # Applies output limit, if set.
        output = pTerm + iTerm + dTerm
        output = min(output, self.__class__.OUTPUT_LIMIT)
        output = max(output, self.__class__.OUTPUT_LIMIT * -1)

        return output

    @classmethod
    def setDefaultTuning(cls, kp: float, ki: float, kd: float):
        cls.kp_DEFAULT = kp
        cls.ki_DEFAULT = ki
        cls.kd_DEFAULT = kd

    @classmethod
    def setIntegralLimit(cls, limit: float):
        cls.INTEGRAL_LIMIT = limit

    @classmethod
    def setOutputLimit(cls, limit: float):
        cls.OUTPUT_LIMIT = limit
