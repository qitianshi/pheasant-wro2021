# GyroStraight.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements straight-line movement using a gyroscopic sensor.


from pybricks.ev3devices import Motor, GyroSensor
from pybricks.parameters import Port
from .PIDLoop import PIDLoop

class GyroStraight(PIDLoop):

    # TODO: Add default tuning values for gyro straight.
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 port: Port,
                 speed: float,
                 stopCondition,
                 angle: int,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT) -> None:

        self.port = port
        self.speed = speed
        self.stopCondition = stopCondition
        super().__init__(angle, kp, ki, kd)

        self.__run()

    # TODO: Implement movement control.
    def __run(self):
        while not self.stopCondition:
            pass
