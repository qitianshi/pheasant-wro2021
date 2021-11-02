# main.py
# Created on 6 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Procedures for run.


#region Start-up

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.iodevices import Ev3devSensor
from pybricks.parameters import Port, Stop, Direction, Color
from pybricks.tools import wait

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

#endregion

#region Procedures

def scanHouseBlocksProcedure(thisHouse: utils.DepositPoint, gyroAngle: int, stopCondition, thenHoldMotors: bool):

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
            utils.RunLogic.houses[thisHouse].append(utils.RunLogic.convertEv3ColorToBlockColor(utils.SideScan.color()))
            previouslyNextToHouseBlock = True
        elif previouslyNextToHouseBlock and not currentlyNextToHouseBlock:
            previouslyNextToHouseBlock = False

    if thenHoldMotors:
        DRIVE_BASE.hold()

    # To handle the case where there are more than two blocks detected. If this happenes, it's likely that .presence()
    # returned False erroneously. Keeping the first and last two colors is the best simple approach.
    if len(utils.RunLogic.houses[thisHouse]) > 2:
        print("Error while scanning: unexpected number of blocks;", utils.RunLogic.houses[thisHouse])
        utils.RunLogic.houses[thisHouse] = [utils.RunLogic.houses[thisHouse][0], utils.RunLogic.houses[thisHouse][-1]]

    print("House colors:", utils.RunLogic.houses[thisHouse])       #FIXME: Prints numbers; implement str representation.

def gyroStraightToBlackLineWithSensorCheckProcedure(speed: int, gyroAngle: int):

    # Checks which sensors can be used to find the black line.
    useLeftSensor = LEFT_COLOR.color() in (Color.WHITE, Color.BLUE, Color.YELLOW)       # Checks that sensor is not over
    useRightSensor = RIGHT_COLOR.color() in (Color.WHITE, Color.BLUE, Color.YELLOW)     # the black line.

    #TODO: Add code to handle the case where both left and right sensors are rejected.

    # Travels to the black line.
    ev3pid.GyroStraight(speed, gyroAngle).runUntil(lambda: (useLeftSensor and LEFT_COLOR.color() == Color.BLACK) or \
        (useRightSensor and RIGHT_COLOR.color() == Color.BLACK))
    DRIVE_BASE.hold()

class EnergyBlockDeposition:

    """
    Procedures for depositing energy blocks.

    ## Discussion
    Before the procedure, ensure that `FrontClaw` position is set to `lift` and `RearClaw` is set to `closeGate`; ensure
    that the robot is at an accetaple neutral point; and ensure that pheasant_utils.RunLogic stores the correct values.

    The robot may rotate up to 360 deg in either direction. Following the procedure, backtrack to a safe position, and
    gyro turn to the original angle or align to some known direction to reset the gyro.

    DRIVE_BASE will be reset during the procedure. Gyro angle will not.
    """

    class FacingDirection:
        TOWARDS = hash("TOWARDS")                 #HACK: enum workaround
        AWAY = hash("AWAY")

    def __init__(self, point: utils.DepositPoint, gyroAngle: int):

        # self.requirements = utils.RunLogic.blocksAtPoint(point)       # Manually programmed for qualifying round.

        # Randomizations for qualifying round.
        if point == utils.DepositPoint.LEFT_HOUSE:
            self.requirements = [utils.BlockColor.SURPLUS, utils.BlockColor.YELLOW]     # .FRONT, .REAR
        elif point == utils.DepositPoint.TOP_HOUSE:
            self.requirements = [utils.BlockColor.GREEN, utils.BlockColor.YELLOW]       # .GREEN, .REAR
        elif point == utils.DepositPoint.RIGHT_HOUSE:
            self.requirements = [utils.BlockColor.SURPLUS, utils.BlockColor.GREEN]      # .FRONT, .GREEN
        elif point == utils.DepositPoint.STORAGE_BATTERY:
            self.requirements = [utils.BlockColor.BLUE, utils.BlockColor.BLUE]          # .BLUE, .BLUE

        self.gyroAngle = gyroAngle
        self.currentlyFacing = self.__class__.FacingDirection.TOWARDS
        self.didTurnAround = False

        self.mustDumpBlue = False           #TODO: Update mustDumpBlue condition

        DRIVE_BASE.reset_angle()

    def __returnToNeutralPoint(self):

        if self.currentlyFacing == self.__class__.FacingDirection.TOWARDS:
            ev3pid.GyroStraight(-200, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() < 0)
            DRIVE_BASE.hold()

        else:
            ev3pid.GyroStraight(200, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() > 0)
            DRIVE_BASE.hold()

    def __turnAround(self):

        multiplier = 1 if self.currentlyFacing == self.__class__.FacingDirection.TOWARDS else -1

        DRIVE_BASE.run_angle(multiplier * 200 * -1, 120)

        ev3pid.GyroTurn(self.gyroAngle + 90 * multiplier, True, False, kp=20).run()
        ev3pid.GyroTurn(self.gyroAngle + 180 * multiplier, False, True, kp=20).run()

        self.gyroAngle += 180 * multiplier
        self.currentlyFacing = self.__class__.FacingDirection.AWAY if \
            self.currentlyFacing == self.__class__.FacingDirection.TOWARDS else self.__class__.FacingDirection.TOWARDS
        self.didTurnAround = True

        DRIVE_BASE.reset_angle()

    def __getGreenClaw(self, count: int):

        # Drives to the deposition zone.
        ev3pid.GyroStraight(-200, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() <= -200)
        DRIVE_BASE.hold()
        utils.RearClaw.drop()
        wait(500)

        # If only 1 of 2 blocks is needed, the robot must pick up one set of blocks.
        if count == 1 and utils.RearClaw.loads == 2:
            DRIVE_BASE.run_angle(100, 40)
            utils.RearClaw.closeGate()

        utils.RearClaw.loads -= count

        self.__returnToNeutralPoint()
        utils.RearClaw.closeGate()

    def __getBlueClaw(self, count: int):

        # Drives to the deposition zone.
        ev3pid.GyroStraight(200, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() >= 260)
        DRIVE_BASE.hold()
        utils.FrontClaw.drop()
        wait(500)

        # If only 1 of 2 blocks is needed, the robot must pick up one set of blocks.
        if count == 1 and utils.FrontClaw.loads == 2:
            DRIVE_BASE.run_angle(-100, 40)
            utils.FrontClaw.lift()

        utils.FrontClaw.loads -= count

        self.__returnToNeutralPoint()
        utils.FrontClaw.lift()

    def __getFrontStore(self, count: int):

        #FIXME: Doesn't work with wall at storage battery.

        # Block distance: -45 deg
        # Claw distance: -70 deg

        gyroStraightBackwardsToGrabBlocks = ev3pid.GyroStraight(-200, self.gyroAngle)

        # Drives backwards to realign blocks in undercarriage storage.
        totalBackDist = -40 - 45 * (5 - len(utils.RunLogic.undercarriageStorage))
        gyroStraightBackwardsToGrabBlocks.runUntil(lambda: DRIVE_BASE.angle() < totalBackDist)
        DRIVE_BASE.hold()
        wait(100)

        # Drives backwards and grabs blocks.
        utils.FrontClaw.rubberUp()
        totalBackDist += -75 - 45 * (count - 1)
        gyroStraightBackwardsToGrabBlocks.speed = -100
        gyroStraightBackwardsToGrabBlocks.runUntil(lambda: DRIVE_BASE.angle() < totalBackDist)
        DRIVE_BASE.hold()
        wait(100)
        utils.FrontClaw.rubberDown()

        # Deposits blocks
        ev3pid.GyroStraight(400, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() >= 275)
        DRIVE_BASE.hold()
        wait(100)
        utils.FrontClaw.rubberUp()

        # Secures subsequent blocks
        DRIVE_BASE.run_angle(-200, 100)
        utils.FrontClaw.rubberDown()
        self.__returnToNeutralPoint()
        utils.FrontClaw.lift()

        for _ in range(count):
            utils.RunLogic.undercarriageStorage.pop()

    def __getRearStore(self, count: int):

        #FIXME: Doesn't work with wall at storage battery.

        # Block distance: -45 deg

        gyroStraightForwardsToGrabBlocks = ev3pid.GyroStraight(175, self.gyroAngle)

        # Drives forwards to realign blocks in undercarriage storage.
        totalForwardsDist = 40 + 45 * (5 - len(utils.RunLogic.undercarriageStorage))
        gyroStraightForwardsToGrabBlocks.runUntil(lambda: DRIVE_BASE.angle() > totalForwardsDist)
        DRIVE_BASE.hold()
        wait(100)
        DRIVE_BASE.run_angle(-100, 10)

        # Drives forwards and grabs blocks.
        utils.RearClaw.openGate()
        wait(100)
        totalForwardsDist += 40 + 45 * (count - 1)
        gyroStraightForwardsToGrabBlocks.speed = 100
        gyroStraightForwardsToGrabBlocks.runUntil(lambda: DRIVE_BASE.angle() > totalForwardsDist)
        DRIVE_BASE.hold()
        wait(100)
        utils.RearClaw.closeGate()

        # Deposits blocks
        ev3pid.GyroStraight(-300, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() <= -300)
        DRIVE_BASE.hold()
        utils.RearClaw.openGate()

        # Secures subsequent blocks
        DRIVE_BASE.run_angle(150, 50)
        utils.RearClaw.closeGate()
        self.__returnToNeutralPoint()

        for _ in range(count):
            utils.RunLogic.undercarriageStorage.pop(0)

    def run(self):

        # Each deposit function assumes that the robot is facing the correct direction.

        print("Depositing:", self.requirements)

        # Resets claws.
        utils.FrontClaw.lift()
        utils.RearClaw.closeGate()

        # The robot must dump its front claw first.
        if self.mustDumpBlue:

            #TODO: Turn robot and dump claw
            pass

        if self.requirements == [utils.BlockColor.BLUE, utils.BlockColor.FRONT]:
            self.__getBlueClaw(1)
            self.__getFrontStore(1)

        elif self.requirements == [utils.BlockColor.GREEN, utils.BlockColor.REAR]:
            self.__turnAround()
            self.__getGreenClaw(1)
            self.__getRearStore(1)

        elif self.requirements == [utils.BlockColor.FRONT, utils.BlockColor.REAR]:
            self.__getFrontStore(1)
            self.__turnAround()
            self.__getRearStore(1)

        elif self.requirements == [utils.BlockColor.BLUE, utils.BlockColor.GREEN]:
            self.__getBlueClaw(1)
            self.__turnAround()
            self.__getGreenClaw(1)

        elif self.requirements == [utils.BlockColor.BLUE, utils.BlockColor.REAR]:
            self.__getBlueClaw(1)
            self.__turnAround()
            self.__getRearStore(1)

        elif self.requirements == [utils.BlockColor.FRONT, utils.BlockColor.GREEN]:
            self.__getFrontStore(1)
            self.__turnAround()
            self.__getGreenClaw(1)

        elif self.requirements == [utils.BlockColor.BLUE, utils.BlockColor.BLUE]:
            self.__getBlueClaw(2)

        elif self.requirements == [utils.BlockColor.GREEN, utils.BlockColor.GREEN]:
            self.__turnAround()
            self.__getGreenClaw(2)

        elif self.requirements == [utils.BlockColor.FRONT, utils.BlockColor.FRONT]:
            self.__getFrontStore(2)

        elif self.requirements == [utils.BlockColor.REAR, utils.BlockColor.REAR]:
            self.__turnAround()
            self.__getRearStore(2)

        if self.mustDumpBlue:
            #TODO: Recollect dumped blue.
            pass

        # Returns to the original orientation.
        if self.didTurnAround:
            self.__turnAround()

        DRIVE_BASE.reset_angle()

        print("Deposit complete.")

#endregion

#region Mission run

def moveToLeftHouse():

    print("-" * 10, "moveForwardTillGreenThenTurn")

    # Moves forward until robot reaches the green area.
    ev3pid.GyroStraight(800, 0).runUntil(lambda: DRIVE_BASE.angle() > 360)
    ev3pid.LineTrack(400, ev3pid.LineEdge.RIGHT, RIGHT_COLOR).runUntil(lambda: LEFT_COLOR.color() == Color.GREEN)

    # Turns around to align with blocks at left house.
    DRIVE_BASE.reset_angle(0)
    DRIVE_BASE.run_angle(100, 30)
    ev3pid.GyroTurn(-90, False, True).run()
    DRIVE_BASE.run_time(-400, 1000)

def scanBlocksAtLeftHouse():

    print("-" * 10, "scanBlocksAtLeftHouse")

    scanHouseBlocksProcedure(utils.DepositPoint.LEFT_HOUSE, 90, \
                             lambda: LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == Color.BLACK, False)

def collectYellowSurplusAndLeftEnergy():

    print("-" * 10, "collectYellowSurplusAndLeftEnergy")

    # Drives forward to align with blocks.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_target(100, 170)

    # Turns, then squares with the line.
    ev3pid.GyroTurn(-170, False, True).run()
    ev3pid.GyroTurn(-180, False, True).run()
    ev3pid.LineSquare(ev3pid.LinePosition.BEHIND).run()

    # Drives forwards to collect the blocks.
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(300, -180).runUntil(lambda: DRIVE_BASE.angle() > 100)  # Move forward to get off the black line.
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

    print("-" * 10, "rotateSolarPanels")

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
    utils.RearClaw.minimum()
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(-100, 0).runUntil(lambda: DRIVE_BASE.angle() < -120)
    ev3pid.GyroTurn(5, True, True).run()
    wait(10)
    ev3pid.GyroTurn(-5, True, True).run()
    wait(10)
    ev3pid.GyroTurn(0, True, True).run()
    utils.RearClaw.maximum()

    # Returns to line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == \
        Color.BLACK)
    DRIVE_BASE.hold()

def collectYellowRightEnergy():

    print("-" * 10, "collectYellowRightEnergy")

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
    utils.FrontClaw.maximum()
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

    print("-" * 10, "collectGreenSurplus")

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
    ev3pid.GyroStraight(300, 0).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK \
        or RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    utils.FrontClaw.closeGate()

def collectGreenEnergy():

    print("-" * 10,  "collectGreenEnergy")

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
    ev3pid.GyroStraight(-150, 0).runUntil(lambda: LEFT_COLOR.color() == Color.GREEN \
        or RIGHT_COLOR.color() == Color.GREEN)
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

    print("-" * 10, "collectBlueSurplus")

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

    print("-" * 10, "collectBlueEnergy")

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

    print("-" * 10, "scanBlocksAtTopHouse")

    # Lifts claw to collect lower blue energy blocks.
    utils.FrontClaw.loads += 1
    utils.FrontClaw.lift()

    # Turns to top house.
    ev3pid.GyroTurn(450, False, True).run()

    scanHouseBlocksProcedure(utils.DepositPoint.TOP_HOUSE, 450,
        lambda: LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == Color.BLACK, thenHoldMotors=True)

    # Turns and aligns to proceeds to black line.
    ev3pid.GyroTurn(540, True, True).run()
    DRIVE_BASE.reset_angle()
    gyroStraightBackwardsToBlackLine = ev3pid.GyroStraight(-1000, 540)
    gyroStraightBackwardsToBlackLine.runUntil(lambda: DRIVE_BASE.angle() < -650)
    gyroStraightBackwardsToBlackLine.speed = -200
    gyroStraightBackwardsToBlackLine.runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    wait(100)

def depositBlocksAtTopHouse():

    print("-" * 10, "depositBlocksAtTopHouse")

    # Moves to neutral position for block deposition.
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(300, 540).runUntil(lambda: DRIVE_BASE.angle() > 500)
    DRIVE_BASE.hold()

    EnergyBlockDeposition(utils.DepositPoint.TOP_HOUSE, 540).run()

    gyroStraightToBlackLineWithSensorCheckProcedure(300, 720)
    wait(100)

def depositBlocksAtStorageBattery():

    print("-" * 10, "depositBlocksAtStorageBattery")

    # Moves to neutral position for block deposition.
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(-200, 720).runUntil(lambda: DRIVE_BASE.angle() < -200)
    DRIVE_BASE.hold()

    EnergyBlockDeposition(utils.DepositPoint.STORAGE_BATTERY, 720).run()

    gyroStraightToBlackLineWithSensorCheckProcedure(300, 720)
    wait(100)

def depositBlocksAtRightHouse():

    print("-" * 10, "depositBlocksAtRightHouse")

#endregion
