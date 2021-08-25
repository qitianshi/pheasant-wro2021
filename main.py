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
BRICK = EV3Brick()
LEFT_COLOR = ColorSensor(Port.S2)
RIGHT_COLOR = ColorSensor(Port.S3)
GYRO = GyroSensor(Port.S4, Direction.COUNTERCLOCKWISE)
LEFT_MOTOR = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
RIGHT_MOTOR = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
DRIVE_BASE = ev3move.TwoWheelDrive(LEFT_MOTOR, RIGHT_MOTOR)

# Initialize ev3pid package settings
ev3pid.DoubleMotorBase.setDefaultMotors(LEFT_MOTOR, RIGHT_MOTOR)
ev3pid.GyroInput.setDefaultSensor(GYRO)
ev3pid.ColorInput.setKnownThresholds(([LEFT_COLOR, LEFT_THRESHOLD], [RIGHT_COLOR, RIGHT_THRESHOLD]))
ev3pid.DoubleColorInput.setDefaultSensors(LEFT_COLOR, RIGHT_COLOR)
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
utils.SideScan.sensor = Ev3devSensor(Port.S1)

# Variables
blocks = []

# Preflight checks
if BRICK.battery.voltage() < 7600:      # In millivolts.

    print("Low battery.")

    from sys import exit
    exit()

def partialRunStartupProcedure():

    # Gyro
    GYRO.reset_angle(360)

    # Claws
    utils.RearClaw.loads = 2
    utils.RearClaw.lift()
    utils.FrontClaw.closeGate()

#endregion

def moveForwardTillGreenThenTurn():

    # Moves forward until robot reaches the green area.
    ev3pid.GyroStraight(800, 0).runUntil(lambda: DRIVE_BASE.angle() > 360)
    ev3pid.LineTrack(400, ev3pid.LineEdge.RIGHT, RIGHT_COLOR).runUntil(lambda: LEFT_COLOR.color() == Color.GREEN)

    # Turns around to align with blocks at left house.
    DRIVE_BASE.reset_angle(0)
    DRIVE_BASE.run_angle(100, 30, wait=True)
    ev3pid.GyroTurn(-90, False, True).run()
    DRIVE_BASE.run_time(-400, 1000, wait=True)

def scanBlocksAtLeftHouse():

    # Scans the first block
    wait(50)
    firstColor = utils.SideScan.color()
    firstColor = firstColor if firstColor != Color.BLACK else None
    blocks.append([firstColor])

    # Drives forward until it goes past the first block. If no block is present, this step is skipped.
    DRIVE_BASE.reset_angle()
    while not utils.SideScan.presence():
        DRIVE_BASE.run(200)

    # Drives forward to scan the second block.
    DRIVE_BASE.run(200)
    secondColor = []
    while not (LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == Color.BLACK):

        measuredColor = utils.SideScan.color()

        if measuredColor != None and measuredColor != Color.BLACK:
            secondColor.append(measuredColor)

    if len(secondColor) == 0:
        blocks[0].append(None)
    else:
        # Finds the most frequent color. The sensor sometimes detects a wrong color when it is sensing the edge of the
        # block.
        blocks[0].append(max(set(secondColor), key=secondColor.count))

    print("Left house:", blocks[0])

def collectYellowSurplusAndLeftEnergy():

    # Drives forward to align with blocks.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_target(100, 170)

    # Turns, then squares with the line.
    ev3pid.GyroTurn(-170, False, True).run()
    ev3pid.GyroTurn(-180, False, True).run()
    ev3pid.LineSquare(ev3pid.LinePosition.BEHIND).run()

    # Drives forwards to collect the blocks.
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(300, -180).runUntil(lambda: DRIVE_BASE.angle() > 100)   # Move forward to get off the black line.
    ev3pid.GyroStraight(300, -180).runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(300, -180).runUntil(lambda: DRIVE_BASE.angle() > 220)
    DRIVE_BASE.hold()

    # Lowers the front claw.
    utils.FrontClaw.closeGate()

    # Returns to the line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    wait(50)

def rotateSolarPanels():

    # Turns to align to black line for line tracking.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(200, 60)
    ev3pid.GyroTurn(-90, True, True).run()

    # Travels to solar panels.
    ev3pid.LineTrack(300, ev3pid.LineEdge.RIGHT, LEFT_COLOR).runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.reset_angle()
    ev3pid.LineTrack(75, ev3pid.LineEdge.RIGHT, LEFT_COLOR).runUntil(lambda: DRIVE_BASE.angle() > 90)
    DRIVE_BASE.hold()
    wait(20)

    # Turns to solar panels.
    ev3pid.GyroTurn(0, True, True).run()
    wait(50)
    ev3pid.GyroTurn(0, True, True).run()

    # Rotates solar panels.
    utils.RearClaw.resetLowered()
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(-100, 0).runUntil(lambda: DRIVE_BASE.angle() < -120)
    ev3pid.GyroTurn(5, True, True).run()
    wait(10)
    ev3pid.GyroTurn(-5, True, True).run()
    wait(10)
    ev3pid.GyroTurn(0, True, True).run()
    utils.RearClaw.resetRaised()

    # Returns to line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == \
        Color.BLACK)
    DRIVE_BASE.hold()

def collectYellowRightEnergy():

    # Turns to align to black line for line tracking.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(200, 60)
    ev3pid.GyroTurn(-90, True, True).run()

    # Reverses to align with vertical line.
    ev3pid.GyroStraight(-100, -90).runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)

    # Travels to yellow blocks.
    DRIVE_BASE.reset_angle()
    ev3pid.LineTrack(300, ev3pid.LineEdge.RIGHT, LEFT_COLOR).runUntil(lambda: DRIVE_BASE.angle() > 430)
    ev3pid.GyroStraight(100, -90).runUntil(lambda: DRIVE_BASE.angle() > 560)
    DRIVE_BASE.hold()

    # Turns and collects.
    utils.FrontClaw.resetRaised()
    ev3pid.GyroTurn(-180, True, True, kp=9).run()
    DRIVE_BASE.hold()
    wait(50)
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(300, -180).runUntil(lambda: DRIVE_BASE.angle() > 220)
    DRIVE_BASE.hold()
    utils.FrontClaw.closeGate()

    # Returns to the line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: DRIVE_BASE.angle() < 50)
    DRIVE_BASE.hold()
    wait(50)

def collectGreenSurplus():

    # Turns to point side sensor at surplus green blocks.
    for _ in range(2):      # Performs turn twice to ensure accuracy.
        ev3pid.GyroTurn(-90, False, True).run()
        wait(20)
    DRIVE_BASE.hold()
    wait(50)

    # Drives forward while sensing if the surplus energy blocks are present.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(200, 340, then=Stop.HOLD, wait=False)
    surplusAtGreen = False
    wait(10)                            # Waits before running loop to allow motors to start moving.
    while DRIVE_BASE.angle() < 340:
        if (not surplusAtGreen) and utils.SideScan.presence():
            surplusAtGreen = True
    if surplusAtGreen:
        print("Surplus at green.")

    # Turns to face the blocks
    ev3pid.GyroTurn(0, False, True).run()

    # Drives forwards to collect.
    utils.FrontClaw.openGate()
    ev3pid.GyroStraight(300, 0).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    utils.FrontClaw.closeGate()

def collectGreenEnergy():

    def driveBackAndCollectGreenBlocks(moveBackDegrees):

        # Collect left-most green energy blocks.
        utils.RearClaw.collect()

        DRIVE_BASE.reset_angle()
        ev3pid.GyroStraight(-150, 180).runUntil(lambda: DRIVE_BASE.angle() < -1 * moveBackDegrees)
        DRIVE_BASE.hold()

        utils.RearClaw.loads += 1
        utils.RearClaw.lift()

        wait(100)

    # Turns and travels towards green energy blocks.
    ev3pid.GyroStraight(-150, 0).runUntil(lambda: LEFT_COLOR.color() == Color.GREEN or RIGHT_COLOR.color() == Color.GREEN)
    DRIVE_BASE.hold()
    ev3pid.GyroTurn(90, True, False).run()
    ev3pid.LineTrack(200, ev3pid.LineEdge.RIGHT, LEFT_COLOR).runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    # driveBase.run_angle(100, 10)
    DRIVE_BASE.hold()
    wait(10)
    ev3pid.GyroTurn(180, True, True).run()
    DRIVE_BASE.hold()

    driveBackAndCollectGreenBlocks(150)

    # Travels to right-most green blocks.
    ev3pid.GyroTurn(270, True, False).run()
    DRIVE_BASE.reset_angle()
    ev3pid.LineTrack(200, ev3pid.LineEdge.LEFT, RIGHT_COLOR).runUntil(lambda: DRIVE_BASE.angle() > 125)
    DRIVE_BASE.hold()
    ev3pid.GyroTurn(180, True, True).run()
    DRIVE_BASE.hold()

    driveBackAndCollectGreenBlocks(115)

    # Turns towards right side of playfield.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(100, -35)
    wait(100)
    ev3pid.GyroTurn(270, True, False).run()

def collectBlueSurplus():

    # Travels to blue area.
    DRIVE_BASE.reset_angle()
    lineTrackGreenZoneToBlue = ev3pid.LineTrack(600, ev3pid.LineEdge.LEFT, RIGHT_COLOR)
    lineTrackGreenZoneToBlue.runUntil(lambda: DRIVE_BASE.angle() > 1080)
    lineTrackGreenZoneToBlue.speed = 250
    lineTrackGreenZoneToBlue.runUntil(lambda: LEFT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()

    # Drives to surplus blocks.
    wait(10)
    ev3pid.GyroTurn(360, True, True).run()
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(-400, 360).runUntil(lambda: DRIVE_BASE.angle() < -400)

    # Scans for surplus blocks.
    DRIVE_BASE.run(-200)
    surplusAtBlue = False
    while LEFT_COLOR.color() != Color.BLACK or RIGHT_COLOR.color() != Color.BLACK:
        if utils.SideScan.presence():
            surplusAtBlue = True
    DRIVE_BASE.hold()

    ev3pid.LineSquare(ev3pid.LinePosition.BEHIND).run()

    # Collects blue surplus, if present.
    if surplusAtBlue:

        print("Surplus at blue.")

        # Aligns to blue surplus.
        DRIVE_BASE.run_angle(100, 65)
        utils.FrontClaw.resetRaised()
        ev3pid.GyroTurn(450, True, True).run()
        DRIVE_BASE.reset_angle()

        # Drives forward to collect blocks.
        ev3pid.GyroStraight(350, 450).runUntil(lambda: DRIVE_BASE.angle() > 250)

        # Lowers the claw.
        utils.FrontClaw.closeGate()

        # Returns to save point.
        ev3pid.GyroStraight(-200, 450).runUntil(lambda: DRIVE_BASE.angle() < -120)
        ev3pid.GyroStraight(100, 450).runUntil(lambda: DRIVE_BASE.angle() > -90)
        ev3pid.GyroTurn(360, True, True).run()
        ev3pid.LineSquare(ev3pid.LinePosition.BEHIND).run()

def collectBlueEnergy():

    # Turns towards top blue energy
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(200, 360).runUntil(lambda: DRIVE_BASE.angle() > 100)
    DRIVE_BASE.hold()
    wait(10)
    ev3pid.GyroTurn(270, True, False).run()

    # Drives forwards and lift claw
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(200, 270).runUntil(lambda: DRIVE_BASE.angle() > 100)
    DRIVE_BASE.hold()
    utils.FrontClaw.loads += 1
    utils.FrontClaw.lift()

    # TODO: Finish blue energy collection

partialRunStartupProcedure()

# moveForwardTillGreenThenTurn()
# scanBlocksAtLeftHouse()
# collectYellowSurplusAndLeftEnergy()
# rotateSolarPanels()
# collectYellowRightEnergy()
# collectGreenSurplus()
# collectGreenEnergy()
# collectBlueSurplus()
collectBlueEnergy()

wait(1000)
