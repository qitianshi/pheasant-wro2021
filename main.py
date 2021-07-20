#!/usr/bin/env pybricks-micropython

# main.py
# Created on 6 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Main program.


# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.nxtdevices import ColorSensor as NxtColorSensor               # type: ignore
from pybricks.parameters import Port, Stop, Direction, Color                # type: ignore
from pybricks.tools import wait                                             # type: ignore
# pylint: enable=F0401

import movement
import pheasant_utils

# Initialize hardware
brick = EV3Brick()
sideColor = NxtColorSensor(Port.S1)
leftColor = ColorSensor(Port.S2)
rightColor = ColorSensor(Port.S3)
gyro = GyroSensor(Port.S4, Direction.COUNTERCLOCKWISE)
frontClaw = Motor(Port.A)
leftMotor = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
rightMotor = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
rearClaw = Motor(Port.D)

# Initialize movement package settings
movement.DoubleMotorMovement.setDefaultMotors(leftMotor, rightMotor)
movement.GyroMovement.setDefaultGyroSensor(gyro)
movement.GyroStraight.setDefaultTuning(22, 0.2, 10000000)
movement.GyroStraight.setDefaultIntegralLimit(100)
movement.GyroStraight.setDefaultOutputLimit(1000)
movement.GyroTurn.setDefaultTuning(23, 0, 10000000, 12, 0, 10000000)
movement.LineSquare.setDefaultTuning(20, 0, 10000000)
movement.LineSquare.setDefaultOutputLimit(60)
movement.LineTrack.setDefaultTuning(1.8, 0.0002, 1)
movement.LineTrack.setDefaultIntegralLimit(50)
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
    movement.GyroStraight(0, 800, lambda: drive.angle() > 360)
    movement.LineTrack(RIGHT_THRESHOLD, movement.LineEdge.RIGHT, 400, lambda: leftColor.color() == Color.GREEN, rightColor)

    # Turns around to align with blocks at left house.
    drive.reset_angle(0)
    drive.run_angle(100, 30, wait=True)
    movement.GyroTurn(-90, False, True)
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
    movement.GyroTurn(-170, False, True)
    movement.GyroTurn(-180, False, True)
    movement.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, movement.LinePosition.BEHIND, leftColor, rightColor)

    # Drives forwards to collect the blocks.
    drive.reset_angle()
    movement.GyroStraight(-180, 300, lambda: drive.angle() > 100)                   # Move forward to get off the black line.
    movement.GyroStraight(-180, 300, lambda: rightColor.color() == Color.BLACK)
    drive.reset_angle()
    movement.GyroStraight(-180, 300, lambda: drive.angle() > 220)
    drive.hold()

    # TODO: Lower the front claw.

    # Returns to the line.
    movement.GyroStraight(-180, -300, lambda: rightColor.color() == Color.BLACK)
    drive.hold()
    wait(50)

def rotateSolarPanels():

    # Turns to align to black line for line tracking.
    drive.reset_angle()
    drive.run_angle(200, 60)
    movement.GyroTurn(-90, True, True)

    # Travels to solar panels.
    movement.LineTrack(LEFT_THRESHOLD, movement.LineEdge.RIGHT, 300, lambda: rightColor.color() == Color.BLACK, leftColor)
    drive.reset_angle()
    movement.LineTrack(LEFT_THRESHOLD, movement.LineEdge.RIGHT, 100, lambda: drive.angle() > 100, leftColor)
    drive.hold()

    # Turns to solar panels.
    movement.GyroTurn(-180, True, True)

    # TODO: Rotate solar panels.

    # Returns to line.
    movement.GyroStraight(-180, -300, lambda: leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK)
    drive.hold()

def collectYellowRightBlocks():

    # Turns to align to black line for line tracking.
    drive.reset_angle()
    drive.run_angle(200, 60)
    movement.GyroTurn(-90, True, True)

    # Reverses to align with vertical line.
    movement.GyroStraight(-90, -100, lambda: rightColor.color() == Color.BLACK)

    # Travels to yellow blocks.
    drive.reset_angle()
    movement.LineTrack(LEFT_THRESHOLD, movement.LineEdge.RIGHT, 300, lambda: drive.angle() > 430, leftColor)    
    movement.GyroStraight(-90, 100, lambda: drive.angle() > 560)
    drive.hold()

    # Turns and collects.
    movement.GyroTurn(-180, True, True)
    drive.hold()
    wait(50)
    drive.reset_angle()
    movement.GyroStraight(-180, 300, lambda: drive.angle() > 220)
    drive.hold()

    # TODO: Lower claw
    wait(100)

    # Returns to the line.
    movement.GyroStraight(-180, -300, lambda: drive.angle() < 50)
    drive.hold()
    wait(50)

def collectGreenSurplus():
    
    # Turns to point side sensor at surplus green blocks.
    for _ in range(2):      # Performs turn twice to ensure accuracy.
        movement.GyroTurn(-90, False, True)
    drive.hold()
    wait(50)

    # Drives forward while sensing if the surplus energy blocks are present.
    drive.reset_angle()
    drive.run_angle(200, 340, then=Stop.HOLD, wait=False)
    surplusAtGreen = False
    wait(10)                            # Waits before running loop to allow motors to start moving.
    while drive.angle() < 340:
        if sideColor.color() != None and sideColor.color() != Color.BLACK:
            surplusAtGreen = True
    if surplusAtGreen:
        print("Surplus at green.")

    # Turns to face the blocks
    movement.GyroTurn(0, False, True)

    # Drives forwards to collect.
    movement.GyroStraight(0, 300, lambda: leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK)
    drive.hold()

    # Turns and travels towards green energy blocks.
    movement.GyroTurn(90, True, False)
    movement.LineTrack(RIGHT_THRESHOLD, movement.LineEdge.LEFT, 200, lambda: leftColor.color() == Color.BLACK, rightColor)
    drive.hold()

def collectGreenBlocks():
    
    # Turns to collect right-most green blocks.
    while leftColor.reflection() < LEFT_THRESHOLD:
        drive.run(-100)
    drive.hold()
    movement.GyroTurn(0, True, True)
    drive.hold()

    # Line-squares to black line.
    movement.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, movement.LinePosition.BEHIND, leftColor, rightColor)

    # TODO: Collect green blocks.
    wait(100)

    # Travels to left-most green blocks.
    movement.GyroTurn(90, True, False)
    drive.reset_angle()
    movement.GyroStraight(90, 200, lambda: drive.angle() > 100)
    drive.hold()
    movement.GyroTurn(0, True, True)
    movement.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, movement.LinePosition.BEHIND, leftColor, rightColor)
    drive.run_angle(-100, 60)

    # TODO: Collects green blocks.
    wait(100)

    # Turns towards right side of playfield.
    movement.GyroTurn(-90, False, True)
    drive.hold()

def collectBlueSurplus():
    
    # Travels to blue area.
    drive.reset_angle()
    movement.LineTrack(RIGHT_THRESHOLD, movement.LineEdge.LEFT, 600, lambda: drive.angle() > 1500, rightColor)
    movement.LineTrack(RIGHT_THRESHOLD, movement.LineEdge.LEFT, 250, lambda: leftColor.color() == Color.BLACK, rightColor)
    drive.hold()
    drive.reset_angle()
    drive.run_angle(100, 50)

    # Drives to surplus blocks.
    movement.GyroTurn(0, True, True)
    drive.hold()
    wait(10)
    drive.reset_angle()
    movement.GyroStraight(0, -400, lambda: drive.angle() < -400)

    # Scans for surplus blocks.
    drive.run(-200)
    surplusAtBlue = False
    while leftColor.color() != Color.BLACK or rightColor.color() != Color.BLACK:
        detectedColor = sideColor.color()
        if detectedColor != Color.BLACK and detectedColor != None:
            surplusAtBlue = True
    drive.hold()

    movement.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, movement.LinePosition.BEHIND, leftColor, rightColor)

    # Collects blue surplus, if present.
    if surplusAtBlue:

        print("Surplus at blue.")

        # Aligns to blue surplus.
        drive.run_angle(100, 65)
        movement.GyroTurn(90, True, True)
        drive.reset_angle()

        # Drives forward to collect blocks.
        movement.GyroStraight(90, 300, lambda: drive.angle() > 380)

        # TODO: Lower the claw.
        wait(100)

        # Returns to save point.
        movement.GyroStraight(90, -300, lambda: drive.angle() < 125)
        movement.GyroTurn(0, True, True)
        movement.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, movement.LinePosition.BEHIND, leftColor, rightColor)

moveForwardTillGreenThenTurn()
scanBlocksAtLeftHouse()
collectYellowSurplusAndLeftBlocks()
rotateSolarPanels()
collectYellowRightBlocks()
collectGreenSurplus()
collectGreenBlocks()
collectBlueSurplus()

wait(1000)
