# GyroTurn.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements turning by angle using a gyroscopic sensor.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase

from .GyroStraight import GyroStraight

class GyroTurn(GyroStraight):

    # TODO: Add default tuning values for gyro turn.
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 port: Port,
                 angle: int,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT):

        # Lambda expression for stop condition may need to be modified for its margin of error.
        super().__init__(port, 0, lambda: abs(GyroSensor.angle() - angle) < 1, angle, kp, ki, kd)

        self.__run()

    # TODO: Implement movement control.
    def __run(self):
        pass
