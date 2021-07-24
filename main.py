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

import ev3move
import ev3pid
import pheasant_utils as utils

# Initialize hardware
brick = EV3Brick()
sideColor = NxtColorSensor(Port.S1)
leftColor = ColorSensor(Port.S2)
rightColor = ColorSensor(Port.S3)
gyro = GyroSensor(Port.S4, Direction.COUNTERCLOCKWISE)
leftMotor = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
rightMotor = Motor(Port.C, positive_direction=Direction.CLOCKWISE)

# Initialize ev3pid package settings
ev3pid.DoubleMotorBase.setDefaultMotors(leftMotor, rightMotor)
ev3pid.GyroMovement.setDefaultGyroSensor(gyro)
ev3pid.GyroStraight.setDefaultTuning(22, 0.2, 10000000)
ev3pid.GyroStraight.setDefaultIntegralLimit(100)
ev3pid.GyroStraight.setDefaultOutputLimit(1000)
ev3pid.GyroTurn.setDefaultTuning(23, 0, 10000000, 12, 0, 10000000)
ev3pid.LineSquare.setDefaultTuning(20, 0, 10000000)
ev3pid.LineSquare.setDefaultOutputLimit(60)
ev3pid.LineTrack.setDefaultTuning(1.8, 0.0002, 1)
ev3pid.LineTrack.setDefaultIntegralLimit(50)
driveBase = ev3move.TwoWheelDrive(leftMotor, rightMotor)

# Initialize pheasant_utils package settings
utils.FrontClaw.MOTOR = Motor(Port.A)
utils.FrontClaw.MOTOR.reset_angle(utils.FrontClaw.ANGLE_RANGE)
utils.RearClaw.MOTOR = Motor(Port.D, positive_direction=Direction.COUNTERCLOCKWISE)
utils.RearClaw.MOTOR.reset_angle(utils.RearClaw.ANGLE_RANGE)

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
    ev3pid.GyroStraight(0, 800).run(lambda: driveBase.angle() > 360)
    ev3pid.LineTrack(RIGHT_THRESHOLD, ev3pid.LineEdge.RIGHT, 400, rightColor).run(lambda: leftColor.color() == Color.GREEN)

    # Turns around to align with blocks at left house.
    driveBase.reset_angle(0)
    driveBase.run_angle(100, 30, wait=True)
    ev3pid.GyroTurn(-90, False, True)
    driveBase.run_time(-400, 1000, wait=True)

def scanBlocksAtLeftHouse():

    # Scans the first block
    wait(50)
    firstColor = sideColor.color()
    firstColor = firstColor if firstColor != Color.BLACK else None
    blocks.append([firstColor])

    # Drives forward until it goes past the first block. If no block is present, this step is skipped.
    driveBase.reset_angle()
    while sideColor.color() != Color.BLACK:
        driveBase.run(200)

    # Drives forward to scan the second block.
    driveBase.run(200)
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
    driveBase.reset_angle()
    driveBase.run_target(100, 170)

    # Turns, then squares with the line.
    ev3pid.GyroTurn(-170, False, True)
    ev3pid.GyroTurn(-180, False, True)
    ev3pid.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, ev3pid.LinePosition.BEHIND, leftColor, rightColor)

    # Drives forwards to collect the blocks.
    driveBase.reset_angle()
    ev3pid.GyroStraight(-180, 300).run(lambda: driveBase.angle() > 100)                   # Move forward to get off the black line.
    ev3pid.GyroStraight(-180, 300).run(lambda: rightColor.color() == Color.BLACK)
    driveBase.reset_angle()
    ev3pid.GyroStraight(-180, 300).run(lambda: driveBase.angle() > 220)
    driveBase.hold()

    # Lowers the front claw.
    utils.FrontClaw.closeGate()

    # Returns to the line.
    ev3pid.GyroStraight(-180, -300).run(lambda: rightColor.color() == Color.BLACK)
    driveBase.hold()
    wait(50)

def rotateSolarPanels():

    # Turns to align to black line for line tracking.
    driveBase.reset_angle()
    driveBase.run_angle(200, 60)
    ev3pid.GyroTurn(-90, True, True)

    # Travels to solar panels.
    ev3pid.LineTrack(LEFT_THRESHOLD, ev3pid.LineEdge.RIGHT, 300, leftColor).run(lambda: rightColor.color() == Color.BLACK)
    driveBase.reset_angle()
    ev3pid.LineTrack(LEFT_THRESHOLD, ev3pid.LineEdge.RIGHT, 75, leftColor).run(lambda: driveBase.angle() > 100)
    driveBase.hold()
    wait(20)

    # Turns to solar panels.
    ev3pid.GyroTurn(0, True, True)
    wait(50)
    ev3pid.GyroTurn(0, True, True)

    # Rotates solar panels.
    utils.RearClaw.resetLowered()
    driveBase.reset_angle()
    ev3pid.GyroStraight(0, -100).run(lambda: driveBase.angle() < -120)
    ev3pid.GyroTurn(5, True, True)
    wait(10)
    ev3pid.GyroTurn(-5, True, True)
    wait(10)
    ev3pid.GyroTurn(0, True, True)
    utils.RearClaw.resetRaised()

    # Returns to line.
    ev3pid.GyroStraight(-180, -300).run(lambda: leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK)
    driveBase.hold()

def collectYellowRightBlocks():

    # Turns to align to black line for line tracking.
    driveBase.reset_angle()
    driveBase.run_angle(200, 60)
    ev3pid.GyroTurn(-90, True, True)

    # Reverses to align with vertical line.
    ev3pid.GyroStraight(-90, -100).run(lambda: rightColor.color() == Color.BLACK)

    # Travels to yellow blocks.
    driveBase.reset_angle()
    ev3pid.LineTrack(LEFT_THRESHOLD, ev3pid.LineEdge.RIGHT, 300, leftColor).run(lambda: driveBase.angle() > 430)    
    ev3pid.GyroStraight(-90, 100).run(lambda: driveBase.angle() > 560)
    driveBase.hold()

    # Turns and collects.
    utils.FrontClaw.resetRaised()
    ev3pid.GyroTurn(-180, True, True, kp=9)
    driveBase.hold()
    wait(50)
    driveBase.reset_angle()
    ev3pid.GyroStraight(-180, 300).run(lambda: driveBase.angle() > 220)
    driveBase.hold()
    utils.FrontClaw.closeGate()

    # Returns to the line.
    ev3pid.GyroStraight(-180, -300).run(lambda: driveBase.angle() < 50)
    driveBase.hold()
    wait(50)

def collectGreenSurplus():
    
    # Turns to point side sensor at surplus green blocks.
    for _ in range(2):      # Performs turn twice to ensure accuracy.
        ev3pid.GyroTurn(-90, False, True)
        wait(20)
    driveBase.hold()
    wait(50)

    # Drives forward while sensing if the surplus energy blocks are present.
    driveBase.reset_angle()
    driveBase.run_angle(200, 340, then=Stop.HOLD, wait=False)
    surplusAtGreen = False
    wait(10)                            # Waits before running loop to allow motors to start moving.
    while driveBase.angle() < 340:
        if sideColor.color() != None and sideColor.color() != Color.BLACK:
            surplusAtGreen = True
    if surplusAtGreen:
        print("Surplus at green.")

    # Turns to face the blocks
    ev3pid.GyroTurn(0, False, True)

    # Drives forwards to collect.
    utils.FrontClaw.openGate()
    ev3pid.GyroStraight(0, 300).run(lambda: leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK)
    driveBase.hold()
    utils.FrontClaw.closeGate()

def collectGreenBlocks():

    # Turns and travels towards green energy blocks.
    ev3pid.GyroStraight(0, -150).run(lambda: leftColor.color() == Color.GREEN or rightColor.color() == Color.GREEN)
    driveBase.hold()
    ev3pid.GyroTurn(90, True, False)
    ev3pid.LineTrack(LEFT_THRESHOLD, ev3pid.LineEdge.RIGHT, 200, leftColor).run(lambda: rightColor.color() == Color.BLACK)
    driveBase.hold()
    wait(10)
    ev3pid.GyroTurn(180, True, True)
    driveBase.hold()

    # Collect left green energy blocks.
    utils.RearClaw.collect()
    driveBase.reset_angle()
    ev3pid.GyroStraight(180, -200).run(lambda: driveBase.angle() < -155)
    driveBase.hold()
    utils.RearClaw.lift()

    # TODO: Not done.

    # # Line-squares to black line.
    # ev3pid.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, ev3pid.LinePosition.BEHIND, leftColor, rightColor)

    # # TODO: Collect green blocks.
    # wait(100)

    # # Travels to left-most green blocks.
    # ev3pid.GyroTurn(90, True, False)
    # drive.reset_angle()
    # ev3pid.GyroStraight(90, 200).run(lambda: drive.angle() > 100)
    # drive.hold()
    # ev3pid.GyroTurn(0, True, True)
    # ev3pid.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, ev3pid.LinePosition.BEHIND, leftColor, rightColor)
    # drive.run_angle(-100, 60)

    # # TODO: Collects green blocks.
    # wait(100)

    # # Turns towards right side of playfield.
    # ev3pid.GyroTurn(-90, False, True)
    # drive.hold()

def collectBlueSurplus():
    
    pass

    # TODO: Update to change to front claw.
    
    # # Travels to blue area.
    # drive.reset_angle()
    # ev3pid.LineTrack(RIGHT_THRESHOLD, ev3pid.LineEdge.LEFT, 600, rightColor).run(lambda: drive.angle() > 1500)
    # ev3pid.LineTrack(RIGHT_THRESHOLD, ev3pid.LineEdge.LEFT, 250, rightColor).run(lambda: leftColor.color() == Color.BLACK)
    # drive.hold()
    # drive.reset_angle()
    # drive.run_angle(100, 50)

    # # Drives to surplus blocks.
    # ev3pid.GyroTurn(0, True, True)
    # drive.hold()
    # wait(10)
    # drive.reset_angle()
    # ev3pid.GyroStraight(0, -400).run(lambda: drive.angle() < -400)

    # # Scans for surplus blocks.
    # drive.run(-200)
    # surplusAtBlue = False
    # while leftColor.color() != Color.BLACK or rightColor.color() != Color.BLACK:
    #     detectedColor = sideColor.color()
    #     if detectedColor != Color.BLACK and detectedColor != None:
    #         surplusAtBlue = True
    # drive.hold()

    # ev3pid.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, ev3pid.LinePosition.BEHIND, leftColor, rightColor)

    # # Collects blue surplus, if present.
    # if surplusAtBlue:

    #     print("Surplus at blue.")

    #     # Aligns to blue surplus.
    #     drive.run_angle(100, 65)
    #     ev3pid.GyroTurn(90, True, True)
    #     drive.reset_angle()

    #     # Drives forward to collect blocks.
    #     ev3pid.GyroStraight(90, 300).run(lambda: drive.angle() > 380)

    #     # TODO: Lower the claw.
    #     wait(100)

    #     # Returns to save point.
    #     ev3pid.GyroStraight(90, -300).run(lambda: drive.angle() < 125)
    #     ev3pid.GyroTurn(0, True, True)
    #     ev3pid.LineSquare(LEFT_THRESHOLD, RIGHT_THRESHOLD, ev3pid.LinePosition.BEHIND, leftColor, rightColor)

moveForwardTillGreenThenTurn()
scanBlocksAtLeftHouse()
collectYellowSurplusAndLeftBlocks()
rotateSolarPanels()
collectYellowRightBlocks()
collectGreenSurplus()
collectGreenBlocks()
collectBlueSurplus()

wait(1000)
