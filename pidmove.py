# pidmove.py
# Created on 7 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Module for movement based on PID. Includes programs for line tracking, line squaring, and gyro movement.


from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase

class PIDLoop:
    pass

class LineTrack(PIDLoop):
    pass

class LineSquare(PIDLoop):
    pass

class GyroStraight(PIDLoop):
    pass
