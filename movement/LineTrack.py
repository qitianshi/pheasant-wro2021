# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line-tracking movement using a reflected light intensity sensor.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase

from .PIDLoop import PIDLoop

class LineEdge():           # Enum workaround (MicroPython does not support enums).
    LEFT = 0
    RIGHT = 1

class LineTrack(PIDLoop):

    # TODO: Add default tuning values for line tracking.
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 trackingEdge: LineEdge,
                 port: Port,
                 speed: float,
                 stopCondition,
                 threshold: int,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT):

        self.trackingEdge = trackingEdge
        self.port = port
        self.speed = speed
        self.stopCondition = stopCondition
        super().__init__(threshold, kp, ki, kd)

        self.__run()

    # TODO: Implement movement control.
    def __run(self):
        while not self.stopCondition():
            pass
