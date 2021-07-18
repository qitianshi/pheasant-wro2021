# TwoWheelDrive.py
# Created on 18 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Drive functions for two-wheel drive robots. Emulates the behavior and functionality of the methods in the built-in ev3devices.Motor class.


# pylint: disable=F0401
from pybricks.ev3devices import Motor                                       # type: ignore
from pybricks.parameters import Port, Stop, Direction                       # type: ignore
from pybricks.tools import wait                                             # type: ignore
# pylint: enable=F0401

class TwoWheelDrive:

    def __init__(self,
                 leftMotor: Motor,
                 rightMotor: Motor):

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

    def reset_angle(self, angle: int = 0):
        self.leftMotor.reset_angle(angle)
        self.rightMotor.reset_angle(angle)

    def hold(self):
        self.leftMotor.hold()
        self.rightMotor.hold()

    def run(self, speed):
        self.leftMotor.run(speed)
        self.rightMotor.run(speed)

    def run_time(self, speed, time, then=Stop.Hold, wait=True):
        self.leftMotor.run_time(speed, time, then=then, wait=False)
        self.rightMotor.run_time(speed, time, then=then, wait=wait)

    def run_angle(self, speed, rotation_angle, then=Stop.Hold, wait=True):
        self.leftMotor.run_angle(speed, rotation_angle, then=then, wait=False)
        self.rightMotor.run_angle(speed, rotation_angle, then=then, wait=wait)

    def run_target(self, speed, target_angle, then=Stop.Hold, wait=True):
        self.leftMotor.run_target(speed, target_angle, then=then, wait=False)
        self.rightMotor.run_target(speed, target_angle, then=then, wait=wait)
