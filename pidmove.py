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

    # TODO: Add default tuning values for line tracking.
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 trackingEdge: LineEdge,
                 port: Port,
                 speed: float,
                 stopCondition: function,
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

    def __run(self):
        while not self.stopCondition:
            pass

class LineSquare(PIDLoop):
    
    # TODO: Add default tuning values for line squaring.
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 ports: (Port),
                 threshold: int,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT) -> None:

        self.ports = ports
        super().__init__(threshold, kp, ki, kd)

        self.__run()

    def __run(self):
        pass

class GyroStraight(PIDLoop):
    
    # TODO: Add default tuning values for gyro straight.
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 port: Port,
                 speed: float,
                 stopCondition: function,
                 angle: int,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT) -> None:

        self.port = port
        self.speed = speed
        self.stopCondition = stopCondition
        super().__init__(angle, kp, ki, kd)

        self.__run()

    def __run(self):
        while not self.stopCondition:
            pass

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

        super().__init__(port, 0, lambda: abs(GyroSensor.angle() - angle) < 1, angle, kp, ki, kd)       # Lambda expression for stop condition may need to be modified for its margin of error.

        self.__run()

    def __run(self):
        pass
