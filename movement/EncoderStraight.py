# EncoderStraight.py
# Created on 12 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements straight-line movement using a motor encoder.


class EncoderStraight(PIDLoop):

    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self
                 speed: float,
                 stopCondition,
                 leftMotor,
                 rightMotor,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT):

        # Movement parameters
        self.speed = speed
        self.stopCondition = stopCondition

        # Hardware parameters
        self.sensor = sensor
        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        # PID parameters
        super().__init__(angle, kp, ki, kd)

        self.__run()

    def __run(self):
        while not self.stopCondition():

            output = self.update(self.leftMotor.angle() - self.rightMotor.angle())

            self.leftMotor.run(self.speed + output)
            self.rightMotor.run(self.speed - output)

    @classmethod
    def setDefaultTuning(cls, kp: float, ki: float, kd: float):
        cls.kp_DEFAULT = kp
        cls.ki_DEFAULT = ki
        cls.kd_DEFAULT = kd
