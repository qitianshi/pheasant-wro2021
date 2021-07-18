#!/usr/bin/env pybricks-micropython

# main.py
# Created on 6 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Main program.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.nxtdevices import ColorSensor as NxtColorSensor               # type: ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color        # type: ignore
from pybricks.tools import wait, StopWatch, DataLog                         # type: ignore
from pybricks.robotics import DriveBase                                     # type: ignore
# pylint: enable=F0401

import movement
import runlogic

# Initialize PID settings
movement.LineTrack.setDefaultTuning(1.8, 0.0002, 1)
movement.LineTrack.setDefaultIntegralLimit(50)
movement.LineSquare.setDefaultTuning(20, 0, 10000000)
movement.LineSquare.setDefaultOutputLimit(60)
movement.GyroStraight.setDefaultTuning(22, 0.2, 10000000)
movement.GyroStraight.setDefaultIntegralLimit(100)
movement.GyroStraight.setDefaultOutputLimit(1000)
movement.GyroTurn.setDefaultTuning(23, 0, 10000000, 12, 0, 10000000)

# Initialize hardware
brick = EV3Brick()
frontColor = NxtColorSensor(Port.S1)
leftColor = ColorSensor(Port.S2)
rightColor = ColorSensor(Port.S3)
gyro = GyroSensor(Port.S4, Direction.COUNTERCLOCKWISE)
# frontClaw = Motor(Port.A)
leftMotor = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
rightMotor = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
rearClaw = Motor(Port.D)
drive = movement.TwoWheelDrive(leftMotor, rightMotor)

# Constants
LEFT_THRESHOLD = 47
RIGHT_THRESHOLD = 48

# Variables
blocks = []

def moveForwardTillGreenThenTurn():

    # Moves forward until robot reaches the green area.
    movement.GyroStraight(0, 800, lambda: leftMotor.angle() > 360, gyro, leftMotor, rightMotor)
    movement.LineTrack(RIGHT_THRESHOLD, movement.LineEdge.RIGHT, 400, lambda: leftColor.color() == Color.GREEN, rightColor, leftMotor, rightMotor)

    # Turns around to align with blocks at left house.
    drive.reset_angle(0)
    drive.run_angle(100, 30, wait=True)
    movement.GyroTurn(-90, False, True, gyro, leftMotor, rightMotor)
    drive.run_time(-400, 1000, wait=True)

def scanBlocksAtLeftHouse():

    # Scans the first block
    wait(50)
    firstColor = frontColor.color()
    firstColor = firstColor if firstColor != Color.BLACK else None
    blocks.append([firstColor])

    # Drives forward until it goes past the first block. If no block is present, this step is skipped.
    gyro.reset_angle(-90)
    drive.reset_angle()
    while frontColor.color() != Color.BLACK:
        drive.run(200)

    # Drives forward to scan the second block.
    drive.run(200)
    secondColor = []
    while not (leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK):

        measuredColor = frontColor.color()

        if measuredColor != None and measuredColor != Color.BLACK:
            secondColor.append(measuredColor)
    
    drive.hold()

    blocks[0].append(max(set(secondColor), key=secondColor.count))      # Finds the most frequent color. The sensor sometimes detects a wrong color when it is sensing the edge of the block.
    print("Left house:", blocks[0])

moveForwardTillGreenThenTurn()
scanBlocksAtLeftHouse()

wait(1000)
