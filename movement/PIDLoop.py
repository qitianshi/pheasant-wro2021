# PIDLoop.py
# Created on 7 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Base clase for PID-based control systems.


class PIDLoop:

    def __init__(self,
                 setpoint: int,
                 kp: float,
                 ki: float,
                 kd: float):

        self.setpoint = setpoint
        self.kp = ki
        self.ki = ki
        self.kd = kd

        self.prevError = 0
        self.integral = 0

    def update(error):

        # Proportional term
        pTerm = self.kp * error

        # Integral term
        self.integral += error
        iTerm = self.integral * ki

        # Differential term
        dTerm = (error - self.prevError) * self.kd

        self.prevError = error

        return pTerm + iTerm + dTerm
