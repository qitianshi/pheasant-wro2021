# TwoWheelDrive.py
# Created on 18 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Drive functions for two-wheel drive robots. Emulates the behavior and functionality of the methods in the built-in
# ev3devices.Motor class.


from pybricks.ev3devices import Motor
from pybricks.parameters import Stop

from .utils.DoubleMotorBase import DoubleMotorBase

class TwoWheelDrive(DoubleMotorBase):

    def __init__(self,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None):

        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

    def speed(self):
        return (self.leftMotor.speed() + self.rightMotor.speed()) / 2

    def angle(self):
        return (self.leftMotor.angle() + self.rightMotor.angle()) / 2

    def reset_angle(self, angle: int = 0):
        self.leftMotor.reset_angle(angle)
        self.rightMotor.reset_angle(angle)

    def hold(self):
        self.leftMotor.hold()
        self.rightMotor.hold()

    def run(self, speed):
        self.leftMotor.run(speed)
        self.rightMotor.run(speed)

    def run_time(self, speed, time, then=Stop.HOLD, wait=True):
        self.leftMotor.run_time(speed, time, then=then, wait=False)
        self.rightMotor.run_time(speed, time, then=then, wait=wait)

    def run_angle(self, speed, rotation_angle, then=Stop.HOLD, wait=True):
        self.leftMotor.run_angle(speed, rotation_angle, then=then, wait=False)
        self.rightMotor.run_angle(speed, rotation_angle, then=then, wait=wait)

    def run_target(self, speed, target_angle, then=Stop.HOLD, wait=True):
        self.leftMotor.run_target(speed, target_angle, then=then, wait=False)
        self.rightMotor.run_target(speed, target_angle, then=then, wait=wait)

    def dc(self, duty):
        self.leftMotor.dc(duty)
        self.rightMotor.dc(duty)
