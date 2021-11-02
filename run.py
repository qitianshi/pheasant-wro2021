#!/usr/bin/env pybricks-micropython

# run.py
# Created on 16 Oct 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Executes robot run.

# Only major changes to this file should be tracked by Git; minor changes for testing should not.
# To pause tracking, run `git update-index --skip-worktree run.py`.
# To resume, run `git update-index --no-skip-worktree run.py`.


from main import *                                              #pylint: disable=wildcard-import, unused-wildcard-import

def preflightChecks():

    if BRICK.battery.voltage() < 7750:      # In millivolts.

        print("Low battery.")

        from sys import exit                                                          #pylint: disable=redefined-builtin
        exit()

# To initialize hardware and run variables when the robot starts from a save point on the field instead of the start
# zone. Comment out the call to this function if running from the start zone.
def partialRunStartupProcedure():

    print("-" * 10, "partialRunStartupProcedure")

    # Claws
    utils.RearClaw.loads = 0
    # utils.RearClaw.collect()
    utils.FrontClaw.loads = 0
    # utils.FrontClaw.collect()
    if utils.RearClaw.loads > 0 or utils.FrontClaw.loads > 0:            # Delay for claw loading
        wait(10000)

    # Gyro
    GYRO.reset_angle(0)

    # Run variables
    utils.RunLogic.undercarriageStorage = []
    utils.RunLogic.houses = {utils.DepositPoint.LEFT_HOUSE: [],
                             utils.DepositPoint.TOP_HOUSE: [],
                             utils.DepositPoint.RIGHT_HOUSE: []}

preflightChecks()

# partialRunStartupProcedure()

moveToLeftHouse()
scanBlocksAtLeftHouse()
collectYellowSurplusAndLeftEnergy()
rotateSolarPanels()
collectYellowRightEnergy()
collectGreenSurplus()
collectGreenEnergy()
collectBlueSurplus()
collectBlueEnergy()
scanBlocksAtTopHouse()
depositBlocksAtTopHouse()
depositBlocksAtStorageBattery()
depositBlocksAtRightHouse()
depositBlocksAtLeftHouse()
returnToBase()

wait(1000)
