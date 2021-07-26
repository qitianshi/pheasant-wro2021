# PIDLoop.py
# Created on 7 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base class for ev3pid modules involving PID-based control.


class PIDLoop:

    # Class attributes to be implemented in subclasses
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

        # Resolves optional arguments with default values.
        kp = kp if kp != None else self.__class__.kp_DEFAULT
        ki = ki if ki != None else self.__class__.ki_DEFAULT
        kd = kd if kd != None else self.__class__.kd_DEFAULT
        integralLimit = integralLimit if integralLimit != None else self.__class__.INTEGRAL_LIMIT_DEFAULT
        integralLimit = outputLimit if outputLimit != None else self.__class__.OUTPUT_LIMIT_DEFAULT

        # PID parameters
        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integralLimit = integralLimit
        self.outputLimit = outputLimit

        # PID loop terms
        self.prevError = 0
        self.integral = 0

    def update(self, error: float) -> float:

        # Proportional term
        pTerm = error * self.kp

        # Integral term
        self.integral += error
        iTerm = self.integral * self.ki
        if self.integralLimit != None:          # Applies integral limit, if set.
            self.integral = min(self.integral, self.integralLimit)
            self.integral = max(self.integral, self.integralLimit * -1)

        # Differential term
        dTerm = (error - self.prevError) * self.kd

        self.prevError = error

        output = pTerm + iTerm + dTerm
        if self.outputLimit != None:            # Applies output limit, if set.
            output = min(output, self.outputLimit)
            output = max(output, self.outputLimit * -1)

        return output

    def reset(self):
        self.integral = 0
        self.prevError = 0

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
