# PIDLoop.py
# Created on 7 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base clase for PID-based control systems.


class PIDLoop:

    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    INTEGRAL_LIMIT_DEFAULT = None
    OUTPUT_LIMIT_DEFAULT = None

    def __init__(self,
                 setpoint: int,
                 kp: float,
                 ki: float,
                 kd: float,
                 integralLimit: float,
                 outputLimit: float):

        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integralLimit = integralLimit
        self.outputLimit = outputLimit

        self.prevError = 0
        self.integral = 0

    def update(self, error: float) -> float:

        # Proportional term
        pTerm = error * self.kp

        # Integral term
        self.integral += error
        iTerm = self.integral * self.ki
        if self.integralLimit != None:       # Applies integral limit, if set.
            self.integral = min(self.integral, self.integralLimit)
            self.integral = max(self.integral, self.integralLimit * -1)

        # Differential term
        dTerm = (error - self.prevError) * self.kd

        self.prevError = error

        output = pTerm + iTerm + dTerm
        if self.outputLimit != None:                    # Applies output limit, if set.
            output = min(output, self.outputLimit)
            output = max(output, self.outputLimit * -1)

        return output

    @classmethod
    def setDefaultTuning(cls, kp: float, ki: float, kd: float):
        cls.kp_DEFAULT = kp
        cls.ki_DEFAULT = ki
        cls.kd_DEFAULT = kd

    @classmethod
    def setDefaultIntegralLimit(cls, limit: float):
        cls.INTEGRAL_LIMIT_DEFAULT = limit

    @classmethod
    def setDefaultOutputLimit(cls, limit: float):
        cls.OUTPUT_LIMIT_DEFAULT = limit
