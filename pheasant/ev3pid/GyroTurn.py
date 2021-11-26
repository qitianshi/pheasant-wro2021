# GyroTurn.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements turning by angle using a gyroscopic sensor.


from pybricks.ev3devices import Motor, GyroSensor

from ev3move import DoubleMotorBase
from .utils.PIDController import PIDController
from .utils.GyroInput import GyroInput

class GyroTurn(PIDController, GyroInput, DoubleMotorBase):

    # Different tuning values used depending on the number of wheels being driven for turning.

    # For single motor turning
    kp_SINGLE_DEFAULT = None
    ki_SINGLE_DEFAULT = None
    kd_SINGLE_DEFAULT = None
    INTEGRAL_LIMIT_SINGLE_DEFAULT = None
    OUTPUT_LIMIT_SINGLE_DEFAULT = None

    # For double motor turning
    kp_DOUBLE_DEFAULT = None
    ki_DOUBLE_DEFAULT = None
    kd_DOUBLE_DEFAULT = None
    INTEGRAL_LIMIT_DOUBLE_DEFAULT = None
    OUTPUT_LIMIT_DOUBLE_DEFAULT = None

    def __init__(self,
                 angle: int,
                 leftDriven: bool,
                 rightDriven: bool,
                 sensor: GyroSensor = None,
                 leftMotor: Motor = None,
                 rightMotor: Motor = None,
                 kp: float = None,
                 ki: float = None,
                 kd: float = None,
                 integralLimit: float = None,
                 outputLimit: float = None):

        # Resolves optional arguments with default values.
        if leftDriven and rightDriven:
            kp = kp if kp is not None else GyroTurn.kp_DOUBLE_DEFAULT
            ki = ki if ki is not None else GyroTurn.ki_DOUBLE_DEFAULT
            kd = kd if kd is not None else GyroTurn.kd_DOUBLE_DEFAULT
            integralLimit = integralLimit if integralLimit is not None else GyroTurn.INTEGRAL_LIMIT_DOUBLE_DEFAULT
            outputLimit = outputLimit if outputLimit is not None else GyroTurn.OUTPUT_LIMIT_DOUBLE_DEFAULT
        else:
            kp = kp if kp is not None else GyroTurn.kp_SINGLE_DEFAULT
            ki = ki if ki is not None else GyroTurn.ki_SINGLE_DEFAULT
            kd = kd if kd is not None else GyroTurn.kd_SINGLE_DEFAULT
            integralLimit = integralLimit if integralLimit is not None else GyroTurn.INTEGRAL_LIMIT_SINGLE_DEFAULT
            outputLimit = outputLimit if outputLimit is not None else GyroTurn.OUTPUT_LIMIT_SINGLE_DEFAULT

        # Angle parameters
        self.angle = angle

        # Movement parameters
        self.leftDriven = leftDriven
        self.rightDriven = rightDriven

        # Hardware parameters
        GyroInput.__init__(self, sensor)
        DoubleMotorBase.__init__(self, leftMotor, rightMotor)

        # PID parameters
        super().__init__(angle, kp, ki, kd, integralLimit, outputLimit)

    def run(self, precisely: bool = False):

        ANGLE_TOLERANCE = 0 if precisely else 1
        EXIT_SPEED = 0 if precisely else 25

        while not (abs(self.sensor.angle() - self.angle) <= ANGLE_TOLERANCE and \
            abs(self.leftMotor.speed()) <= EXIT_SPEED and abs(self.rightMotor.speed()) <= EXIT_SPEED):

            output = self.update(self.sensor.angle() - self.angle)

            self.leftMotor.run(self.leftDriven * output * -1)
            self.rightMotor.run(self.rightDriven * output)

        self.leftMotor.hold()
        self.rightMotor.hold()

    def rawControllerOutput(self):
        return self.update(self.sensor.angle() - self.angle)

    @classmethod
    def setDefaultTuning(cls,
                         kpSingle: float,
                         kiSingle: float,
                         kdSingle: float,
                         kpDouble: float,
                         kiDouble: float,
                         kdDouble: float):

        cls.kp_SINGLE_DEFAULT = kpSingle
        cls.ki_SINGLE_DEFAULT = kiSingle
        cls.kd_SINGLE_DEFAULT = kdSingle

        cls.kp_DOUBLE_DEFAULT = kpDouble
        cls.ki_DOUBLE_DEFAULT = kiDouble
        cls.kd_DOUBLE_DEFAULT = kdDouble

    @classmethod
    def setDefaultIntegralLimit(cls, limitSingle: float, limitDouble: float):
        cls.INTEGRAL_LIMIT_SINGLE_DEFAULT = limitSingle
        cls.INTEGRAL_LIMIT_DOUBLE_DEFAULT = limitDouble

    @classmethod
    def setDefaultOutputLimit(cls, limitSingle: float, limitDouble: float):
        cls.OUTPUT_LIMIT_SINGLE_DEFAULT = limitSingle
        cls.OUTPUT_LIMIT_DOUBLE_DEFAULT = limitDouble
