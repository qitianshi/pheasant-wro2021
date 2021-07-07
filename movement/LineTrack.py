# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line-tracking movement using a reflected light intensity sensor.


from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from .PIDLoop import PIDLoop
from enum import Enum, auto

class LineEdge(Enum):
    LEFT = auto()
    RIGHT = auto()

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
                 kd: float = kd_DEFAULT) -> None:

        self.trackingEdge = trackingEdge
        self.port = port
        self.speed = speed
        self.stopCondition = stopCondition
        super().__init__(threshold, kp, ki, kd)

        self.__run()

    # TODO: Implement movement control.
    def __run(self):
        while not self.stopCondition:
            pass
