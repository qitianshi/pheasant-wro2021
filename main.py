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
ev3pid.GyroTurn.setDefaultTuning(22, 0, 100000, 12, 0, 100000)
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

# Preflight checks
if BRICK.battery.voltage() < 7750:      # In millivolts.

    print("Low battery.")

    from sys import exit
    exit()

#endregion

#region Procedures

# To initialize hardware and run variables when the robot starts from a save point on the field instead of the start
# zone. Comment out the call to this function if running from the start zone.
def partialRunStartupProcedure():

    print("-" * 10, "Begin partialRunStartupProcedure", sep='\n')

    # Claws
    utils.RearClaw.loads = 2
    utils.RearClaw.lift()
    utils.FrontClaw.loads = 1
    utils.FrontClaw.closeGate()

    wait(15000)

    # Gyro
    GYRO.reset_angle(270)

    # Run variables
    # utils.Logic.robotStorage = []
    # utils.Logic.houses = {utils.DepositPoint.LEFT_HOUSE: [],
    #                       utils.DepositPoint.TOP_HOUSE: [],
    #                       utils.DepositPoint.RIGHT_HOUSE: []}

def scanHouseBlocksProcedure(house: utils.DepositPoint, gyroAngle: int, stopCondition, thenHoldMotors: bool):

    MOVE_SPEED = 400

    # Drives to top house while scanning.
    gyroStraightController = ev3pid.GyroStraight(None, gyroAngle)

    previouslyNextToHouseBlock = False
    while not stopCondition():

        # Control gyro straight
        gyroStraightControllerOutput = gyroStraightController.rawControllerOutput()
        LEFT_MOTOR.run(MOVE_SPEED - gyroStraightControllerOutput)
        RIGHT_MOTOR.run(MOVE_SPEED + gyroStraightControllerOutput)

        # Scans house blocks.
        currentlyNextToHouseBlock = utils.SideScan.presence()
        if (not previouslyNextToHouseBlock) and currentlyNextToHouseBlock:
            utils.RunLogic.houses[house].append(utils.SideScan.color())
            previouslyNextToHouseBlock = True
        elif previouslyNextToHouseBlock and not currentlyNextToHouseBlock:
            previouslyNextToHouseBlock = False

    if thenHoldMotors:
        DRIVE_BASE.hold()

    # To handle the case where there are more than two blocks detected. If this happenes, it's likely that .presence()
    # returned False erroneously. Keeping the first and last two colors is the best simple approach.
    if len(utils.RunLogic.houses[house]) > 2:
        print("Error while scanning: unexpected number of blocks;", utils.RunLogic.houses[house])
        utils.RunLogic.houses[house] = [utils.RunLogic.houses[house][0], utils.RunLogic.houses[house][-1]]

    print("House colors:", utils.RunLogic.houses[house])

#endregion

def moveToLeftHouse():

    print("-" * 10, "Begin moveForwardTillGreenThenTurn", sep='\n')

    # Moves forward until robot reaches the green area.
    ev3pid.GyroStraight(800, 0).runUntil(lambda: DRIVE_BASE.angle() > 360)
    ev3pid.LineTrack(400, ev3pid.LineEdge.RIGHT, RIGHT_COLOR).runUntil(lambda: LEFT_COLOR.color() == Color.GREEN)

    # Turns around to align with blocks at left house.
    DRIVE_BASE.reset_angle(0)
    DRIVE_BASE.run_angle(100, 30)
    ev3pid.GyroTurn(-90, False, True).run()
    DRIVE_BASE.run_time(-400, 1000)

def scanBlocksAtLeftHouse():

    print("-" * 10, "Begin scanBlocksAtLeftHouse", sep='\n')

    scanHouseBlocksProcedure(utils.DepositPoint.LEFT_HOUSE, 90, \
                             lambda: LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == Color.BLACK, False)

def collectYellowSurplusAndLeftEnergy():

    print("-" * 10, "Begin collectYellowSurplusAndLeftEnergy", sep='\n')

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

    print("-" * 10, "Begin rotateSolarPanels", sep='\n')

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

    print("-" * 10, "Begin collectYellowRightEnergy", sep='\n')

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

    print("-" * 10, "Begin collectGreenSurplus", sep='\n')

    # Turns to point side sensor at surplus green blocks.
    for _ in range(2):      # Performs turn twice to ensure accuracy.
        ev3pid.GyroTurn(-90, False, True).run()
        wait(20)
    DRIVE_BASE.hold()
    wait(50)

    # Drives forward while sensing if the surplus energy blocks are present.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(200, 340, then=Stop.HOLD, wait=True)

    # Turns to face the blocks
    ev3pid.GyroTurn(0, False, True).run()

    # Drives forwards to collect.
    utils.FrontClaw.openGate()
    ev3pid.GyroStraight(300, 0).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    utils.FrontClaw.closeGate()

def collectGreenEnergy():

    print("-" * 10, "Begin collectGreenEnergy", sep='\n')

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
    DRIVE_BASE.run_angle(100, -85)
    wait(50)
    ev3pid.GyroTurn(270, True, False).run()

def collectBlueSurplus():

    print("-" * 10, "Begin collectBlueSurplus", sep='\n')

    # Travels to blue area.
    DRIVE_BASE.reset_angle()
    lineTrackGreenZoneToBlue = ev3pid.LineTrack(600, ev3pid.LineEdge.RIGHT, LEFT_COLOR)
    lineTrackGreenZoneToBlue.runUntil(lambda: DRIVE_BASE.angle() > 810)
    lineTrackGreenZoneToBlue.speed = 250
    lineTrackGreenZoneToBlue.runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()

    # Aligns with blue surplus blocks.
    wait(10)
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(200, 60)
    ev3pid.GyroTurn(180, True, False).run()

    # Collects blue surplus.
    utils.FrontClaw.openGate()
    gyroStraightCollectBlueSurplus = ev3pid.GyroStraight(200, 180)
    gyroStraightCollectBlueSurplus.runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or \
        RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.reset_angle()
    gyroStraightCollectBlueSurplus.speed = 450
    gyroStraightCollectBlueSurplus.runUntil(lambda: DRIVE_BASE.angle() > 580)
    DRIVE_BASE.hold()
    utils.FrontClaw.closeGate()

    # Turns and aligns to upper blue energy blocks.
    ev3pid.GyroTurn(270, True, False, kp=15).run()
    ev3pid.GyroStraight(250, 270).runUntil(lambda: LEFT_COLOR.color() == Color.WHITE \
        or RIGHT_COLOR.color() == Color.WHITE)
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(100, 30)
    DRIVE_BASE.hold()

def collectBlueEnergy():

    print("-" * 10, "Begin collectBlueEnergy", sep='\n')

    # Lifts claw to collect upper blue energy blocks.
    utils.FrontClaw.loads += 1
    utils.FrontClaw.lift()

    # Drives to lower blue energy blocks.
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(-200, 270).runUntil(lambda: DRIVE_BASE.angle() < -175)
    DRIVE_BASE.hold()
    ev3pid.GyroTurn(360, True, False).run()
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(200, 360).runUntil(lambda: DRIVE_BASE.angle() > 210)
    DRIVE_BASE.hold()
    ev3pid.GyroTurn(270, True, False).run()

    # Turns and aligns to lower blue energy blocks.
    utils.FrontClaw.collect()
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(250, 270).runUntil(lambda: DRIVE_BASE.angle() > 90)
    DRIVE_BASE.hold()

def scanBlocksAtTopHouse():

    # Lifts claw to collect lower blue energy blocks.
    utils.FrontClaw.loads += 1
    utils.FrontClaw.lift()

    # Turns to top house.
    ev3pid.GyroTurn(450, False, True).run()

    scanHouseBlocksProcedure(utils.DepositPoint.TOP_HOUSE, 450, \
                             lambda: LEFT_COLOR.color() != Color.BLACK and RIGHT_COLOR.color() != Color.BLACK, True)

partialRunStartupProcedure()

# moveToLeftHouse()
# scanBlocksAtLeftHouse()
# collectYellowSurplusAndLeftEnergy()
# rotateSolarPanels()
# collectYellowRightEnergy()
# collectGreenSurplus()
# collectGreenEnergy()
# collectBlueSurplus()
# collectBlueEnergy()
scanBlocksAtTopHouse()

wait(1000)
