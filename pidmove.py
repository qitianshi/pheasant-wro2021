# pidmove.py
# Created on 7 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Module for PID-based movement. Includes programs for line tracking, line squaring, and gyro movement.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from enum import Enum, auto

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

class LineEdge(Enum):
    LEFT = auto()
    RIGHT = auto()

class LineTrack(PIDLoop):

    # TODO: Add default tuning values for line tracking
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 threshold: int,
                 trackingEdge: LineEdge,
                 port: Port,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT) -> None:

        super().__init__(threshold, kp, ki, kd)
        self.trackingEdge = trackingEdge
        self.port = port

class LineSquare(PIDLoop):
    
    # TODO: Add default tuning values for line squaring
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 threshold: int,
                 ports: (Port),
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT) -> None:

        super().__init__(threshold, kp, ki, kd)
        self.ports = ports

class GyroStraight(PIDLoop):
    
    # TODO: Add default tuning values for gyro straight
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 threshold: int,
                 port: Port,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT) -> None:

        super().__init__(threshold, kp, ki, kd)
        self.port = port
