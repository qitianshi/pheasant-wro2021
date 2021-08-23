#!/usr/bin/env pybricks-micropython

# main.py
# Created on 6 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Main program.


#region Start-up

# pylint: disable=F0401
from pybricks.hubs import EV3Brick                                          # type: ignore
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor              # type: ignore
from pybricks.iodevices import Ev3devSensor                                 # type: ignore
from pybricks.parameters import Port, Stop, Direction, Color                # type: ignore
from pybricks.tools import wait                                             # type: ignore
# pylint: enable=F0401

import ev3move
import ev3pid
import pheasant_utils as utils

# Constants
LEFT_THRESHOLD = 47
RIGHT_THRESHOLD = 48

# Initialize hardware
brick = EV3Brick()
sideColor = Ev3devSensor(Port.S1)
leftColor = ColorSensor(Port.S2)
rightColor = ColorSensor(Port.S3)
gyro = GyroSensor(Port.S4, Direction.COUNTERCLOCKWISE)
leftMotor = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
rightMotor = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
driveBase = ev3move.TwoWheelDrive(leftMotor, rightMotor)

# Initialize ev3pid package settings
ev3pid.DoubleMotorBase.setDefaultMotors(leftMotor, rightMotor)
ev3pid.GyroInput.setDefaultSensor(gyro)
ev3pid.ColorInput.setKnownThresholds(([leftColor, LEFT_THRESHOLD], [rightColor, RIGHT_THRESHOLD]))
ev3pid.DoubleColorInput.setDefaultSensors(leftColor, rightColor)
ev3pid.GyroStraight.setDefaultTuning(22, 0.2, 100000)
ev3pid.GyroStraight.setDefaultIntegralLimit(100)
ev3pid.GyroStraight.setDefaultOutputLimit(1000)
ev3pid.GyroTurn.setDefaultTuning(23, 0, 100000, 12, 0, 100000)
ev3pid.LineSquare.setDefaultTuning(20, 0, 100000)
ev3pid.LineSquare.setDefaultOutputLimit(60)
ev3pid.LineTrack.setDefaultTuning(1.8, 0.0002, 1)
ev3pid.LineTrack.setDefaultIntegralLimit(50)

# Initialize pheasant_utils package settings
utils.FrontClaw.MOTOR = Motor(Port.A)
utils.FrontClaw.MOTOR.reset_angle(utils.FrontClaw.ANGLE_RANGE)
utils.RearClaw.MOTOR = Motor(Port.D, positive_direction=Direction.COUNTERCLOCKWISE)
utils.RearClaw.MOTOR.reset_angle(utils.RearClaw.ANGLE_RANGE)

# Variables
blocks = []

# Preflight checks
if brick.battery.voltage() < 7600:      # In millivolts.

    print("Low battery.")

    from sys import exit
    exit()

#endregion

def moveForwardTillGreenThenTurn():

    # Moves forward until robot reaches the green area.
    ev3pid.GyroStraight(800, 0).runUntil(lambda: driveBase.angle() > 360)
    ev3pid.LineTrack(400, ev3pid.LineEdge.RIGHT, rightColor).runUntil(lambda: leftColor.color() == Color.GREEN)

    # Turns around to align with blocks at left house.
    driveBase.reset_angle(0)
    driveBase.run_angle(100, 30, wait=True)
    ev3pid.GyroTurn(-90, False, True).run()
    driveBase.run_time(-400, 1000, wait=True)

def scanBlocksAtLeftHouse():

    # Scans the first block
    wait(50)
    firstColor = utils.sideScanColor(sideColor)
    firstColor = firstColor if firstColor != Color.BLACK else None
    blocks.append([firstColor])

    # Drives forward until it goes past the first block. If no block is present, this step is skipped.
    driveBase.reset_angle()
    while not utils.sideScanPresence(sideColor):
        driveBase.run(200)

    # Drives forward to scan the second block.
    driveBase.run(200)
    secondColor = []
    while not (leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK):

        measuredColor = utils.sideScanColor(sideColor)

        if measuredColor != None and measuredColor != Color.BLACK:
            secondColor.append(measuredColor)

    if len(secondColor) == 0:
        blocks[0].append(None)
    else:
        # Finds the most frequent color. The sensor sometimes detects a wrong color when it is sensing the edge of the
        # block.
        blocks[0].append(max(set(secondColor), key=secondColor.count))

    print("Left house:", blocks[0])

def collectYellowSurplusAndLeftBlocks():

    # Drives forward to align with blocks.
    driveBase.reset_angle()
    driveBase.run_target(100, 170)

    # Turns, then squares with the line.
    ev3pid.GyroTurn(-170, False, True).run()
    ev3pid.GyroTurn(-180, False, True).run()
    ev3pid.LineSquare(ev3pid.LinePosition.BEHIND).run()

    # Drives forwards to collect the blocks.
    driveBase.reset_angle()
    ev3pid.GyroStraight(300, -180).runUntil(lambda: driveBase.angle() > 100)   # Move forward to get off the black line.
    ev3pid.GyroStraight(300, -180).runUntil(lambda: rightColor.color() == Color.BLACK)
    driveBase.reset_angle()
    ev3pid.GyroStraight(300, -180).runUntil(lambda: driveBase.angle() > 220)
    driveBase.hold()

    # Lowers the front claw.
    utils.FrontClaw.closeGate()

    # Returns to the line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: rightColor.color() == Color.BLACK)
    driveBase.hold()
    wait(50)

def rotateSolarPanels():

    # Turns to align to black line for line tracking.
    driveBase.reset_angle()
    driveBase.run_angle(200, 60)
    ev3pid.GyroTurn(-90, True, True).run()

    # Travels to solar panels.
    ev3pid.LineTrack(300, ev3pid.LineEdge.RIGHT, leftColor).runUntil(lambda: rightColor.color() == Color.BLACK)
    driveBase.reset_angle()
    ev3pid.LineTrack(75, ev3pid.LineEdge.RIGHT, leftColor).runUntil(lambda: driveBase.angle() > 90)
    driveBase.hold()
    wait(20)

    # Turns to solar panels.
    ev3pid.GyroTurn(0, True, True).run()
    wait(50)
    ev3pid.GyroTurn(0, True, True).run()

    # Rotates solar panels.
    utils.RearClaw.resetLowered()
    driveBase.reset_angle()
    ev3pid.GyroStraight(-100, 0).runUntil(lambda: driveBase.angle() < -120)
    ev3pid.GyroTurn(5, True, True).run()
    wait(10)
    ev3pid.GyroTurn(-5, True, True).run()
    wait(10)
    ev3pid.GyroTurn(0, True, True).run()
    utils.RearClaw.resetRaised()

    # Returns to line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: leftColor.color() == Color.BLACK or rightColor.color() == \
        Color.BLACK)
    driveBase.hold()

def collectYellowRightBlocks():

    # Turns to align to black line for line tracking.
    driveBase.reset_angle()
    driveBase.run_angle(200, 60)
    ev3pid.GyroTurn(-90, True, True).run()

    # Reverses to align with vertical line.
    ev3pid.GyroStraight(-100, -90).runUntil(lambda: rightColor.color() == Color.BLACK)

    # Travels to yellow blocks.
    driveBase.reset_angle()
    ev3pid.LineTrack(300, ev3pid.LineEdge.RIGHT, leftColor).runUntil(lambda: driveBase.angle() > 430)    
    ev3pid.GyroStraight(100, -90).runUntil(lambda: driveBase.angle() > 560)
    driveBase.hold()

    # Turns and collects.
    utils.FrontClaw.resetRaised()
    ev3pid.GyroTurn(-180, True, True, kp=9).run()
    driveBase.hold()
    wait(50)
    driveBase.reset_angle()
    ev3pid.GyroStraight(300, -180).runUntil(lambda: driveBase.angle() > 220)
    driveBase.hold()
    utils.FrontClaw.closeGate()

    # Returns to the line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: driveBase.angle() < 50)
    driveBase.hold()
    wait(50)

def collectGreenSurplus():
    
    # Turns to point side sensor at surplus green blocks.
    for _ in range(2):      # Performs turn twice to ensure accuracy.
        ev3pid.GyroTurn(-90, False, True).run()
        wait(20)
    driveBase.hold()
    wait(50)

    # Drives forward while sensing if the surplus energy blocks are present.
    driveBase.reset_angle()
    driveBase.run_angle(200, 340, then=Stop.HOLD, wait=False)
    surplusAtGreen = False
    wait(10)                            # Waits before running loop to allow motors to start moving.
    while driveBase.angle() < 340:
        if (not surplusAtGreen) and utils.sideScanPresence(sideColor):
            surplusAtGreen = True
    if surplusAtGreen:
        print("Surplus at green.")

    # Turns to face the blocks
    ev3pid.GyroTurn(0, False, True).run()

    # Drives forwards to collect.
    utils.FrontClaw.openGate()
    ev3pid.GyroStraight(300, 0).runUntil(lambda: leftColor.color() == Color.BLACK or rightColor.color() == Color.BLACK)
    driveBase.hold()
    utils.FrontClaw.closeGate()

def collectGreenBlocks():

    def driveBackAndCollectGreenBlocks(moveBackDegrees):

        # Collect left-most green energy blocks.
        utils.RearClaw.collect()

        driveBase.reset_angle()
        ev3pid.GyroStraight(-150, 180).runUntil(lambda: driveBase.angle() < -1 * moveBackDegrees)
        driveBase.hold()

        utils.RearClaw.loads += 1
        utils.RearClaw.lift()

        wait(100)

    # Turns and travels towards green energy blocks.
    ev3pid.GyroStraight(-150, 0).runUntil(lambda: leftColor.color() == Color.GREEN or rightColor.color() == Color.GREEN)
    driveBase.hold()
    ev3pid.GyroTurn(90, True, False).run()
    ev3pid.LineTrack(200, ev3pid.LineEdge.RIGHT, leftColor).runUntil(lambda: rightColor.color() == Color.BLACK)
    # driveBase.run_angle(100, 10)
    driveBase.hold()
    wait(10)
    ev3pid.GyroTurn(180, True, True).run()
    driveBase.hold()

    driveBackAndCollectGreenBlocks(150)

    # Travels to right-most green blocks.
    ev3pid.GyroTurn(270, True, False).run()
    driveBase.reset_angle()
    ev3pid.LineTrack(200, ev3pid.LineEdge.LEFT, rightColor).runUntil(lambda: driveBase.angle() > 125)
    driveBase.hold()
    ev3pid.GyroTurn(180, True, True).run()
    driveBase.hold()

    driveBackAndCollectGreenBlocks(115)

    # Turns towards right side of playfield.
    driveBase.reset_angle()
    driveBase.run_angle(100, -35)
    wait(100)
    ev3pid.GyroTurn(270, True, False).run()

def collectBlueSurplus():
    
    # Travels to blue area.
    driveBase.reset_angle()
    lineTrackGreenZoneToBlue = ev3pid.LineTrack(600, ev3pid.LineEdge.LEFT, rightColor)
    lineTrackGreenZoneToBlue.runUntil(lambda: driveBase.angle() > 1080)
    lineTrackGreenZoneToBlue.speed = 250
    lineTrackGreenZoneToBlue.runUntil(lambda: leftColor.color() == Color.BLACK)
    driveBase.hold()

    # Drives to surplus blocks.
    wait(10)
    ev3pid.GyroTurn(360, True, True).run()
    driveBase.reset_angle()
    ev3pid.GyroStraight(-400, 360).runUntil(lambda: driveBase.angle() < -400)

    # Scans for surplus blocks.
    driveBase.run(-200)
    surplusAtBlue = False
    while leftColor.color() != Color.BLACK or rightColor.color() != Color.BLACK:
        if utils.sideScanPresence(sideColor):
            surplusAtBlue = True
    driveBase.hold()

    ev3pid.LineSquare(ev3pid.LinePosition.BEHIND).run()

    # Collects blue surplus, if present.
    if surplusAtBlue:

        print("Surplus at blue.")

        # Aligns to blue surplus.
        driveBase.run_angle(100, 65)
        utils.FrontClaw.resetRaised()
        ev3pid.GyroTurn(450, True, True).run()
        driveBase.reset_angle()

        # Drives forward to collect blocks.
        ev3pid.GyroStraight(350, 450).runUntil(lambda: driveBase.angle() > 250)

        # Lowers the claw.
        utils.FrontClaw.closeGate()

        # Returns to save point.
        ev3pid.GyroStraight(-200, 450).runUntil(lambda: driveBase.angle() < -120)
        ev3pid.GyroStraight(100, 450).runUntil(lambda: driveBase.angle() > -90)
        ev3pid.GyroTurn(360, True, True).run()
        ev3pid.LineSquare(ev3pid.LinePosition.BEHIND).run()

moveForwardTillGreenThenTurn()
scanBlocksAtLeftHouse()
collectYellowSurplusAndLeftBlocks()
rotateSolarPanels()
collectYellowRightBlocks()
collectGreenSurplus()
collectGreenBlocks()
collectBlueSurplus()

wait(1000)
