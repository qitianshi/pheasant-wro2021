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
sideColor = NxtColorSensor(Port.S1)
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

# Preflight checks
if brick.battery.voltage() < 7500:      # In millivolts.

    print("Low battery.")

    from sys import exit
    exit()

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
    firstColor = sideColor.color()
    firstColor = firstColor if firstColor != Color.BLACK else None
    blocks.append([firstColor])

    # Drives forward until it goes past the first block. If no block is present, this step is skipped.
    gyro.reset_angle(-90)
    drive.reset_angle()
    while sideColor.color() != Color.BLACK:
        drive.run(200)

    # Drives forward to scan the second block.
    drive.run(200)
    secondColor = []
    while not (leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK):

        measuredColor = sideColor.color()

        if measuredColor != None and measuredColor != Color.BLACK:
            secondColor.append(measuredColor)

    if len(secondColor) == 0:
        blocks[0].append(None)
    else:
        # Finds the most frequent color. The sensor sometimes detects a wrong color when it is sensing the edge of the block.
        blocks[0].append(max(set(secondColor), key=secondColor.count))

    print("Left house:", blocks[0])

def collectYellowSurplusAndLeftBlocks():

    # Drives forward to align with blocks.
    drive.reset_angle()
    drive.run_target(100, 170)

    # Turns, then squares with the line.
    movement.GyroTurn(-170, False, True, gyro, leftMotor, rightMotor)
    movement.GyroTurn(-180, False, True, gyro, leftMotor, rightMotor, 20)
    movement.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, movement.LinePosition.BEHIND, leftColor, rightColor, leftMotor, rightMotor)

    # Drives forwards to collect the blocks.
    drive.reset_angle()
    movement.GyroStraight(-180, 300, lambda: drive.angle() > 100, gyro, leftMotor, rightMotor)                   # Move forward to get off the black line.
    movement.GyroStraight(-180, 300, lambda: rightColor.color() == Color.BLACK, gyro, leftMotor, rightMotor)
    drive.reset_angle()
    movement.GyroStraight(-180, 300, lambda: drive.angle() > 220, gyro, leftMotor, rightMotor)
    drive.hold()

    # TODO: Lower the front claw.

    # Returns to the line.
    movement.GyroStraight(-180, -300, lambda: rightColor.color() == Color.BLACK, gyro, leftMotor, rightMotor)
    drive.hold()
    wait(50)

def rotateSolarPanels():

    # Turns to align to black line for line tracking.
    drive.reset_angle()
    drive.run_angle(200, 60)
    movement.GyroTurn(-90, True, True, gyro, leftMotor, rightMotor)

    # Travels to solar panels.
    movement.LineTrack(LEFT_THRESHOLD, movement.LineEdge.RIGHT, 300, lambda: rightColor.color() == Color.BLACK, leftColor, leftMotor, rightMotor)
    drive.reset_angle()
    movement.LineTrack(LEFT_THRESHOLD, movement.LineEdge.RIGHT, 100, lambda: drive.angle() > 100, leftColor, leftMotor, rightMotor)
    drive.hold()

    # Turns to solar panels.
    movement.GyroTurn(-180, True, True, gyro, leftMotor, rightMotor)

    # TODO: Rotate solar panels.

    # Returns to line.
    movement.GyroStraight(-180, -300, lambda: leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK, gyro, leftMotor, rightMotor)
    drive.hold()

def collectYellowRightBlocks():

    # Turns to align to black line for line tracking.
    drive.reset_angle()
    drive.run_angle(200, 60)
    movement.GyroTurn(-90, True, True, gyro, leftMotor, rightMotor)

    # Reverses to align with vertical line.
    movement.GyroStraight(-90, -100, lambda: rightColor.color() == Color.BLACK, gyro, leftMotor, rightMotor)

    # Travels to yellow blocks.
    drive.reset_angle()
    movement.LineTrack(LEFT_THRESHOLD, movement.LineEdge.RIGHT, 300, lambda: drive.angle() > 430, leftColor, leftMotor, rightMotor)    
    movement.GyroStraight(-90, 100, lambda: drive.angle() > 560, gyro, leftMotor, rightMotor)
    drive.hold()

    # Turns and collects.
    movement.GyroTurn(-180, True, True, gyro, leftMotor, rightMotor)
    drive.hold()
    wait(50)
    drive.reset_angle()
    movement.GyroStraight(-180, 300, lambda: drive.angle() > 220, gyro, leftMotor, rightMotor)
    drive.hold()

    # TODO: Lower claw
    wait(100)

    # Returns to the line.
    movement.GyroStraight(-180, -300, lambda: drive.angle() < 50, gyro, leftMotor, rightMotor)
    drive.hold()
    wait(50)

def collectGreenSurplus():
    
    # Turn to point side sensor at surplus green blocks.
    for _ in range(2):      # Performs turn twice to ensure accuracy.
        movement.GyroTurn(-90, False, True, gyro, leftMotor, rightMotor)
    drive.hold()
    wait(50)

    # Drives forward while sensing if the surplus energy blocks are present.
    drive.reset_angle()
    drive.run_angle(200, 340, then=Stop.HOLD, wait=False)
    surplusAtGreen = False
    wait(10)                            # Waits before running loop to allow motors to start moving.
    while drive.angle() < 340:
        if sideColor.color() != None or sideColor.color() != Color.BLACK:
            surplusAtGreen = True
    if surplusAtGreen:
        print("Surplus at green.")

    # Turns to face the blocks
    movement.GyroTurn(0, False, True, gyro, leftMotor, rightMotor)

    # Drives forwards to collect.
    movement.GyroStraight(0, 300, lambda: leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK, gyro, leftMotor, rightMotor)
    drive.hold()

    # Turns and travels towards green energy blocks.
    movement.GyroTurn(90, True, False, gyro, leftMotor, rightMotor)
    movement.LineTrack(RIGHT_THRESHOLD, movement.LineEdge.LEFT, 200, lambda: leftColor.color() == Color.BLACK, rightColor, leftMotor, rightMotor)
    drive.hold()

def collectGreenBlocks():
    
    # Turn to collect right-most green blocks.
    while leftColor.reflection() < LEFT_THRESHOLD:
        drive.run(-100)
    drive.hold()
    movement.GyroTurn(0, True, True, gyro, leftMotor, rightMotor)
    drive.hold()

    # Line square to black line.
    movement.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, movement.LinePosition.BEHIND, leftColor, rightColor, leftMotor, rightMotor)

    # TODO: Collect green blocks.
    wait(100)

    # Travel to left-most green blocks.
    movement.GyroTurn(90, True, False, gyro, leftMotor, rightMotor)
    drive.reset_angle()
    movement.GyroStraight(90, 200, lambda: drive.angle() > 100, gyro, leftMotor, rightMotor)
    drive.hold()
    movement.GyroTurn(0, True, True, gyro, leftMotor, rightMotor)
    movement.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, movement.LinePosition.BEHIND, leftColor, rightColor, leftMotor, rightMotor)

    # TODO: Collect green blocks.
    wait(100)

    # Turn towards right side of playfield.
    movement.GyroTurn(-90, False, True, gyro, leftMotor, rightMotor)
    movement.GyroStraight(-90, -100, lambda: rightColor.color() == Color.BLACK, gyro, leftMotor, rightMotor)
    drive.hold()

moveForwardTillGreenThenTurn()
scanBlocksAtLeftHouse()
collectYellowSurplusAndLeftBlocks()
rotateSolarPanels()
collectYellowRightBlocks()
collectGreenSurplus()
collectGreenBlocks()

wait(1000)
