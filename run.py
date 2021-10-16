#!/usr/bin/env pybricks-micropython

# run.py
# Created on 16 Oct 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Executes robot run.

# Only major changes to this file should be tracked by Git; minor changes for testing should not.
# To pause tracking, run `git update-index --skip-worktree run.py`.


from main import *                           #pylint: disable=wildcard-import, unused-wildcard-import, redefined-builtin

# To initialize hardware and run variables when the robot starts from a save point on the field instead of the start
# zone. Comment out the call to this function if running from the start zone.
def partialRunStartupProcedure():

    print("-" * 10, "Begin partialRunStartupProcedure", sep='\n')

    # Delay for manual claw loading
    utils.FrontClaw.lift()
    utils.RearClaw.lift()
    wait(10000)

    # Claws
    utils.RearClaw.loads = 2
    utils.RearClaw.closeGate()
    utils.FrontClaw.loads = 2
    utils.FrontClaw.lift()

    # Gyro
    GYRO.reset_angle(0)

    # Run variables
    utils.RunLogic.undercarriageStorage = []
    utils.RunLogic.houses = {utils.DepositPoint.LEFT_HOUSE: [],
                             utils.DepositPoint.TOP_HOUSE: [],
                             utils.DepositPoint.RIGHT_HOUSE: []}

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

wait(1000)
