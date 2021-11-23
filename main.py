# main.py
# Created on 6 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Procedures for run.


#region Start-up

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.iodevices import Ev3devSensor
from pybricks.parameters import Port, Direction, Color
from pybricks.tools import wait

import ev3move
import ev3pid
import pheasant_utils as utils

# Constants
LEFT_THRESHOLD = 47
RIGHT_THRESHOLD = 42
BLACK_VALUE = 15
WHITE_VALUE = 75

# Initialize hardware
BRICK = EV3Brick()
LEFT_COLOR = ColorSensor(Port.S2)
RIGHT_COLOR = ColorSensor(Port.S3)
GYRO = GyroSensor(Port.S4, Direction.COUNTERCLOCKWISE)
LEFT_MOTOR = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
LEFT_MOTOR.control.limits(speed=1500)
RIGHT_MOTOR = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
RIGHT_MOTOR.control.limits(speed=1500)
DRIVE_BASE = ev3move.TwoWheelDrive(LEFT_MOTOR, RIGHT_MOTOR)

# Initialize ev3pid package settings
ev3pid.DoubleMotorBase.setDefaultMotors(LEFT_MOTOR, RIGHT_MOTOR)
ev3pid.GyroInput.setDefaultSensor(GYRO)
ev3pid.ColorInput.setKnownThresholds(([LEFT_COLOR, LEFT_THRESHOLD], [RIGHT_COLOR, RIGHT_THRESHOLD]))
ev3pid.DoubleColorInput.setDefaultSensors(LEFT_COLOR, RIGHT_COLOR)
ev3pid.GyroStraight.setDefaultTuning(22, 0, 100)
ev3pid.GyroTurn.setDefaultTuning(kpSingle=20, kiSingle=1, kdSingle=400,
                                 kpDouble=14, kiDouble=1, kdDouble=200)
ev3pid.GyroTurn.setDefaultOutputLimit(limitSingle=500, limitDouble=400)
ev3pid.GyroTurn.setDefaultIntegralLimit(limitSingle=20, limitDouble=10)
ev3pid.LineSquare.setDefaultTuning(3, 0.03, 30)
ev3pid.LineSquare.setDefaultOutputLimit(60)
ev3pid.LineSquare.setDefaultIntegralLimit(60)
ev3pid.LineTrack.setDefaultTuning(1.5, 0.002, 250)

# Initialize pheasant_utils package settings
utils.FrontClaw.MOTOR = Motor(Port.A)
utils.FrontClaw.MOTOR.reset_angle(utils.FrontClaw.ANGLE_RANGE)
utils.RearClaw.MOTOR = Motor(Port.D, positive_direction=Direction.COUNTERCLOCKWISE)
utils.RearClaw.MOTOR.reset_angle(utils.RearClaw.ANGLE_RANGE)
utils.SideScan.sensor = Ev3devSensor(Port.S1)

#endregion

#region Procedures

def scanHouseBlocksProcedure(thisHouse: utils.DepositPoint,
                             gyroAngle: int,
                             stopCondition,
                             thenHoldMotors: bool,
                             speed: int = 600):

    # Drives to top house while scanning.
    gyroStraightController = ev3pid.GyroStraight(None, gyroAngle)

    previouslyNextToHouseBlock = False
    while not stopCondition():

        # Control gyro straight
        gyroStraightControllerOutput = gyroStraightController.rawControllerOutput()
        LEFT_MOTOR.run(speed - gyroStraightControllerOutput)
        RIGHT_MOTOR.run(speed + gyroStraightControllerOutput)

        # Scans house blocks.
        currentlyNextToHouseBlock = utils.SideScan.presence()
        if (not previouslyNextToHouseBlock) and currentlyNextToHouseBlock:
            utils.RunLogic.houses[thisHouse].append(utils.RunLogic.convertEv3ColorToBlockColor(utils.SideScan.color()))
            previouslyNextToHouseBlock = True
        elif previouslyNextToHouseBlock and not currentlyNextToHouseBlock:
            previouslyNextToHouseBlock = False

    if thenHoldMotors:
        DRIVE_BASE.hold()
        wait(50)

    # To handle the case where there are more than two blocks detected. If this happenes, it's likely that .presence()
    # returned False erroneously. Keeping the first and last two colors is the best simple approach.
    if len(utils.RunLogic.houses[thisHouse]) > 2:
        print("Error while scanning: unexpected number of blocks;", utils.RunLogic.houses[thisHouse])
        utils.RunLogic.houses[thisHouse] = [utils.RunLogic.houses[thisHouse][0], utils.RunLogic.houses[thisHouse][-1]]

    print("House colors:", utils.RunLogic.houses[thisHouse])       #FIXME: Prints numbers; implement str representation.

def driveBackAndCollectGreenBlocksProcedure(moveBackDegrees, finalClawPosition):

    # Collect left-most green energy blocks.
    utils.RearClaw.collect()

    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(-300, 180).runUntil(lambda: DRIVE_BASE.angle() < -1 * moveBackDegrees)
    DRIVE_BASE.hold()

    utils.RearClaw.loads += 1
    finalClawPosition()

    wait(50)

def gyroStraightToBlackLineWithSensorCheckProcedure(speed: int, gyroAngle: int):

    # # Checks which sensors can be used to find the black line.
    # useLeftSensor = LEFT_COLOR.reflection() > LEFT_THRESHOLD       # Checks that sensor is not over the black line.
    # useRightSensor = RIGHT_COLOR.reflection() > RIGHT_THRESHOLD

    # if not useLeftSensor and not useRightSensor:

    #     print("WARNING: gyroStraightToBlackLineWithSensorCheckProcedure rejected both sensors.")

    #     gyroStraightToBlackLine = ev3pid.GyroStraight(speed, gyroAngle)
    #     gyroStraightToBlackLine.runUntil(lambda: LEFT_COLOR.reflection() < BLACK_VALUE and \
    #         RIGHT_COLOR.reflection() < BLACK_VALUE)
    #     gyroStraightToBlackLine.runUntil(lambda: LEFT_COLOR.color() == Color.WHITE or \
    #         RIGHT_COLOR.color() == Color.WHITE)

    # else:

    #     ev3pid.GyroStraight(speed, gyroAngle).runUntil(lambda: (useLeftSensor and LEFT_COLOR.reflection() < \
    #         BLACK_VALUE) or (useRightSensor and RIGHT_COLOR.reflection() < BLACK_VALUE))
    #     DRIVE_BASE.hold()

    ev3pid.GyroStraight(speed, gyroAngle).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK and \
        RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    wait(10)

def preciseLineSquaringProcedure(linePosition: ev3pid.LinePosition):

    for _ in range(3):

        ev3pid.LineSquare(linePosition).run()

        if LEFT_COLOR.reflection() == LEFT_THRESHOLD and RIGHT_COLOR.reflection() == RIGHT_THRESHOLD:
            break

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

    def __init__(self, point: utils.DepositPoint, gyroAngle: int, finallyFacing: FacingDirection):

        # self.requirements = utils.RunLogic.blocksAtPoint(point)

        # Preprogrammed block colors since randomizations are known.
        if point == utils.DepositPoint.TOP_HOUSE:
            self.requirements = sorted([utils.BlockColor.GREEN, utils.BlockColor.FRONT])
        elif point == utils.DepositPoint.RIGHT_HOUSE:
            self.requirements = sorted([utils.BlockColor.GREEN, utils.BlockColor.REAR])
        elif point == utils.DepositPoint.LEFT_HOUSE:
            self.requirements = sorted([utils.BlockColor.FRONT, utils.BlockColor.REAR])
        elif point == utils.DepositPoint.STORAGE_BATTERY:
            self.requirements = sorted([utils.BlockColor.BLUE, utils.BlockColor.BLUE])

        self.point = point
        self.gyroAngle = gyroAngle
        self.currentlyFacing = EnergyBlockDeposition.FacingDirection.TOWARDS
        self.finallyFacing = finallyFacing

        self.mustDumpBlue = False           #TODO: Update mustDumpBlue condition

        DRIVE_BASE.reset_angle()

    def __returnToNeutralPoint(self):

        if self.currentlyFacing == EnergyBlockDeposition.FacingDirection.TOWARDS:
            ev3pid.GyroStraight(-300, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() < 0)
            DRIVE_BASE.hold()

        else:
            ev3pid.GyroStraight(300, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() > 0)
            DRIVE_BASE.hold()

    def __turnAround(self, precisely: bool = False):

        # TEST CODE
        precisely = False

        multiplier = 1 if self.currentlyFacing == EnergyBlockDeposition.FacingDirection.TOWARDS else -1

        DRIVE_BASE.run_angle(multiplier * 300 * -1, 120)

        if precisely:
            ev3pid.GyroTurn(self.gyroAngle + 90 * multiplier, True, False).run()
            ev3pid.GyroTurn(self.gyroAngle + 180 * multiplier, False, True).run()
        else:
            ev3pid.GyroTurn(self.gyroAngle + 180 * multiplier, True, True).run()
            DRIVE_BASE.run_angle(multiplier * 300 * -1, 180)         # Compensates for lost distance.

        self.gyroAngle += 180 * multiplier
        self.currentlyFacing = EnergyBlockDeposition.FacingDirection.AWAY if \
            self.currentlyFacing == EnergyBlockDeposition.FacingDirection.TOWARDS else \
            EnergyBlockDeposition.FacingDirection.TOWARDS

        DRIVE_BASE.reset_angle()

    @staticmethod
    def __moveClawAtCustomSpeed(claw, amount: float, speedMultiple: float):

        if claw.loads == 2:
            claw.DOUBLE_LOAD_SPEED = int(claw.DOUBLE_LOAD_SPEED * speedMultiple)
            claw.goTo(amount)
            claw.DOUBLE_LOAD_SPEED = int(claw.DOUBLE_LOAD_SPEED / speedMultiple)

        else:
            claw.SINGLE_LOAD_SPEED = int(claw.SINGLE_LOAD_SPEED * speedMultiple)
            claw.goTo(amount)
            claw.SINGLE_LOAD_SPEED = int(claw.SINGLE_LOAD_SPEED / speedMultiple)

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

        if self.point == utils.DepositPoint.STORAGE_BATTERY:

            # Must slow down for high angle raise, otherwise the upper blocks fall off.
            self.__moveClawAtCustomSpeed(utils.FrontClaw, 0.95, 0.25)

        # Drives to the deposition zone.
        ev3pid.GyroStraight(300 if self.point == utils.DepositPoint.STORAGE_BATTERY else 150,\
            self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() >= 260)
        DRIVE_BASE.hold()

        if self.point == utils.DepositPoint.STORAGE_BATTERY:
            self.__moveClawAtCustomSpeed(utils.FrontClaw, 0.74, 0.75)

        else:
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

        gyroStraightBackwardsToGrabBlocks = ev3pid.GyroStraight(-300, self.gyroAngle)

        # Drives backwards to realign blocks in undercarriage storage.
        totalBackDist = -40 - 45 * (5 - len(utils.RunLogic.undercarriageStorage))
        gyroStraightBackwardsToGrabBlocks.runUntil(lambda: DRIVE_BASE.angle() < totalBackDist)
        DRIVE_BASE.hold()
        wait(50)

        # Drives backwards and grabs blocks.
        utils.FrontClaw.rubberUp()
        totalBackDist += -75 - 45 * (count - 1)
        gyroStraightBackwardsToGrabBlocks.speed = -100
        gyroStraightBackwardsToGrabBlocks.runUntil(lambda: DRIVE_BASE.angle() < totalBackDist)
        DRIVE_BASE.hold()
        wait(50)
        utils.FrontClaw.rubberDown()

        # Deposits blocks
        ev3pid.GyroStraight(400, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() >= 375)
        DRIVE_BASE.hold()
        wait(50)
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
        wait(50)
        DRIVE_BASE.run_angle(-100, 10)

        # Drives forwards and grabs blocks.
        utils.RearClaw.openGate()
        wait(50)
        totalForwardsDist += 40 + 45 * (count - 1)
        gyroStraightForwardsToGrabBlocks.speed = 100
        gyroStraightForwardsToGrabBlocks.runUntil(lambda: DRIVE_BASE.angle() > totalForwardsDist)
        DRIVE_BASE.hold()
        wait(50)
        utils.RearClaw.closeGate()

        # Deposits blocks
        ev3pid.GyroStraight(-400, self.gyroAngle).runUntil(lambda: DRIVE_BASE.angle() <= -320)
        DRIVE_BASE.hold()
        utils.RearClaw.openGate()

        # Secures subsequent blocks
        DRIVE_BASE.run_angle(150, 50)
        utils.RearClaw.closeGate()
        DRIVE_BASE.run_angle(-200, 100)
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
            self.__turnAround(precisely=True)
            self.__getGreenClaw(1)
            self.__getRearStore(1)

        elif self.requirements == [utils.BlockColor.FRONT, utils.BlockColor.REAR]:

            if len(utils.RunLogic.undercarriageStorage) == 2:
                self.__getFrontStore(2)

            else:
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
        if self.finallyFacing != self.currentlyFacing:
            self.__turnAround(precisely=False)

        DRIVE_BASE.reset_angle()

        print("Deposit complete.")

#endregion

#region Mission run

def scanBlocksAtLeftHouse():

    print("-" * 10, "scanBlocksAtLeftHouse")

    # Moves forward.
    gyroStraightForwardsToLeftHouse = ev3pid.GyroStraight(1200, 0)
    gyroStraightForwardsToLeftHouse.runUntil(lambda: DRIVE_BASE.angle() > 600)
    gyroStraightForwardsToLeftHouse.speed = 700
    gyroStraightForwardsToLeftHouse.runUntil(lambda: DRIVE_BASE.angle() > 890)
    DRIVE_BASE.hold()
    wait(25)

    # Turns around to align with blocks at left house.
    ev3pid.GyroTurn(-90, False, True).run()
    DRIVE_BASE.run_time(-1000, 750)

    DRIVE_BASE.reset_angle()
    GYRO.reset_angle(-90)
    scanHouseBlocksProcedure(utils.DepositPoint.LEFT_HOUSE, -90, lambda: DRIVE_BASE.angle() > 100, False)
    ev3pid.GyroStraight(450, -90).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK)

def collectYellowSurplusAndLeftEnergy():

    print("-" * 10, "collectYellowSurplusAndLeftEnergy")

    # Drives forward to align with blocks.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_target(200, 120)
    wait(25)

    # Turns, then aligns to black line.
    ev3pid.GyroTurn(-180, False, True).run()
    ev3pid.GyroStraight(-350, -180).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or \
        RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    utils.RearClaw.closeGate(wait=False)

    # Drives forwards to collect the blocks.
    DRIVE_BASE.reset_angle()
    gyroStraightForwardsUntilLeftEnergy = ev3pid.GyroStraight(600, -180)
    gyroStraightForwardsUntilLeftEnergy.runUntil(lambda: DRIVE_BASE.angle() > 600)      # Moves off the black line.
    gyroStraightForwardsUntilLeftEnergy.speed = 400
    gyroStraightForwardsUntilLeftEnergy.runUntil(lambda: DRIVE_BASE.angle() > 810)
    DRIVE_BASE.hold()

    # Lowers the front claw.
    utils.FrontClaw.closeGate()
    wait(100)

    # Returns to the line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: DRIVE_BASE.angle() < 580)
    DRIVE_BASE.hold()
    wait(25)

def rotateSolarPanels():

    print("-" * 10, "rotateSolarPanels")

    # Turns to align to black line for line tracking.
    ev3pid.GyroTurn(-90, True, True).run()

    # Travels to solar panels.
    ev3pid.LineTrack(300, ev3pid.LineEdge.RIGHT, LEFT_COLOR).runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    GYRO.reset_angle(-90)
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(75, 80)

    # Turns to solar panels.
    ev3pid.GyroTurn(0, True, True).run(precisely=True)
    utils.RearClaw.minimum()

    # Rotates solar panels.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(-150, 140)
    DRIVE_BASE.hold()
    utils.RearClaw.closeGate()

    # Returns to line.
    ev3pid.GyroStraight(-300, -180).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or \
        RIGHT_COLOR.color() == Color.BLACK)

def collectYellowRightEnergy():

    print("-" * 10, "collectYellowRightEnergy")

    # Turns to align to black line for line tracking.
    DRIVE_BASE.reset_angle()
    DRIVE_BASE.run_angle(300, 110)
    ev3pid.GyroTurn(-90, True, True).run()

    # Reverses to align with vertical line.
    ev3pid.GyroStraight(-500, -90).runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    utils.FrontClaw.maximum(wait=False)
    wait(50)

    # Travels to yellow blocks.
    DRIVE_BASE.reset_angle()
    ev3pid.LineTrack(800, ev3pid.LineEdge.RIGHT, LEFT_COLOR).runUntil(lambda: DRIVE_BASE.angle() > 430)
    DRIVE_BASE.run_target(300, 560)
    DRIVE_BASE.hold()

    # Turns and collects.
    ev3pid.GyroTurn(-180, True, True).run()
    wait(25)
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(400, -180).runUntil(lambda: DRIVE_BASE.angle() > 120)
    DRIVE_BASE.hold()
    utils.FrontClaw.closeGate()

def collectGreenSurplus():

    print("-" * 10, "collectGreenSurplus")

    # Aligns to green surplus blocks.
    ev3pid.GyroTurn(-90, False, True).run()
    wait(25)
    DRIVE_BASE.reset_angle()
    gyroStraightForwardsToAlignGreenSurplus = ev3pid.GyroStraight(500, -90)
    gyroStraightForwardsToAlignGreenSurplus.runUntil(lambda: DRIVE_BASE.angle() > 290)
    gyroStraightForwardsToAlignGreenSurplus.speed = 250
    gyroStraightForwardsToAlignGreenSurplus.runUntil(lambda: DRIVE_BASE.angle() > 340)
    DRIVE_BASE.hold()
    wait(25)
    ev3pid.GyroTurn(0, False, True).run()
    DRIVE_BASE.reset_angle()

    # Drives forwards to collect.
    utils.FrontClaw.maximum(wait=False)
    gyroStraightForwardsToCollectGreenSurplus = ev3pid.GyroStraight(700, 0)
    gyroStraightForwardsToCollectGreenSurplus.runUntil(lambda: DRIVE_BASE.angle() > 400)
    gyroStraightForwardsToCollectGreenSurplus.speed = 400
    gyroStraightForwardsToCollectGreenSurplus.runUntil(lambda: RIGHT_COLOR.reflection() < BLACK_VALUE)
    DRIVE_BASE.hold()
    utils.FrontClaw.closeGate(wait=False)
    preciseLineSquaringProcedure(ev3pid.LinePosition.BEHIND)
    wait(25)
    GYRO.reset_angle(0)
    DRIVE_BASE.reset_angle()

def collectGreenEnergy():

    print("-" * 10,  "collectGreenEnergy")

    # Turns and travels towards green energy blocks.
    DRIVE_BASE.run_target(250, -85)
    ev3pid.GyroTurn(90, True, False).run()
    ev3pid.LineTrack(300, ev3pid.LineEdge.RIGHT, LEFT_COLOR).runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    wait(50)
    ev3pid.GyroTurn(180, True, True).run(precisely=True)
    DRIVE_BASE.hold()

    driveBackAndCollectGreenBlocksProcedure(160, utils.RearClaw.closeGate)

    # Travels to right-most green blocks.
    ev3pid.GyroTurn(270, True, False).run()
    wait(50)
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(300, 270).runUntil(lambda: DRIVE_BASE.angle() > 120)
    DRIVE_BASE.hold()
    wait(25)
    ev3pid.GyroTurn(180, True, True).run(precisely=True)
    DRIVE_BASE.hold()

    driveBackAndCollectGreenBlocksProcedure(90, lambda: utils.RearClaw.goTo(0.41))

    # Turns towards right side of playfield.
    DRIVE_BASE.run_angle(100, -80)
    wait(25)
    utils.RearClaw.closeGate()
    ev3pid.GyroTurn(270, True, False).run(precisely=True)

def scanBlocksAtRightHouse():

    print("-" * 10, "collectBlueSurplus")

    # Travels to blue area.
    DRIVE_BASE.reset_angle()
    lineTrackGreenZoneToBlue = ev3pid.LineTrack(900, ev3pid.LineEdge.RIGHT, LEFT_COLOR)
    lineTrackGreenZoneToBlue.runUntil(lambda: DRIVE_BASE.angle() > 700)
    lineTrackGreenZoneToBlue.speed = 300
    lineTrackGreenZoneToBlue.runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.run_angle(200, 30)
    wait(50)

    # # Turns and aligns to blocks.
    # utils.RearClaw.goTo(0.4)
    # ev3pid.GyroTurn(225, True, False).run()
    # DRIVE_BASE.run_angle(200, -75)
    # ev3pid.GyroTurn(270, False, True).run()
    # DRIVE_BASE.run_angle(300, -130)
    # wait(50)

    # scanHouseBlocksProcedure(utils.DepositPoint.RIGHT_HOUSE, 270, lambda: LEFT_COLOR.color() == Color.BLACK, True)

def collectBlueSurplus():

    # # Aligns with blue surplus blocks.
    # DRIVE_BASE.reset_angle()
    # DRIVE_BASE.run_angle(-200, 190)
    # wait(50)
    # ev3pid.GyroTurn(180, False, True).run()
    # utils.RearClaw.closeGate()

    ev3pid.GyroTurn(180, True, False).run()
    DRIVE_BASE.hold()
    preciseLineSquaringProcedure(ev3pid.LinePosition.AHEAD)
    GYRO.reset_angle(180)

    # Collects blue surplus.
    utils.FrontClaw.maximum(wait=False)
    # ev3pid.GyroStraight(-200, 180).runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or
    #     RIGHT_COLOR.color() == Color.BLACK)
    # gyroStraightToBlackLineWithSensorCheckProcedure(-200, 180)
    # DRIVE_BASE.hold()
    # wait(50)
    DRIVE_BASE.reset_angle()
    gyroStraightForwardsToCollectBlueSurplus =  ev3pid.GyroStraight(600, 180)
    gyroStraightForwardsToCollectBlueSurplus.runUntil(lambda: DRIVE_BASE.angle() > 300)
    gyroStraightForwardsToCollectBlueSurplus.speed = 400
    gyroStraightForwardsToCollectBlueSurplus.runUntil(lambda: DRIVE_BASE.angle() > 625)
    DRIVE_BASE.hold()
    wait(25)
    utils.FrontClaw.collect()

    # Turns and aligns to upper blue energy blocks.
    ev3pid.GyroTurn(270, True, True).run(precisely=True)
    while not (LEFT_COLOR.reflection() > WHITE_VALUE and RIGHT_COLOR.reflection() > WHITE_VALUE):
        DRIVE_BASE.run(200)
    DRIVE_BASE.hold()

def collectBlueEnergy():

    print("-" * 10, "collectBlueEnergy")

    # Collects upper blue energy blocks.
    ev3pid.GyroTurn(255, True, True).run(precisely=True)
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(400, 255).runUntil(lambda: DRIVE_BASE.angle() >= 190)
    DRIVE_BASE.hold()
    utils.FrontClaw.loads += 1
    utils.FrontClaw.lift()

    # Returns to center.
    ev3pid.GyroStraight(-500, 255).runUntil(lambda: DRIVE_BASE.angle() <= 0)
    DRIVE_BASE.hold()

    # Collects lower blue energy blocks.
    utils.FrontClaw.collect(wait=False)
    ev3pid.GyroTurn(285, True, True).run(precisely=True)
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(400, 285).runUntil(lambda: DRIVE_BASE.angle() >= 180)
    DRIVE_BASE.hold()

def scanBlocksAtTopHouse():

    print("-" * 10, "scanBlocksAtTopHouse")

    # Lifts claw to collect lower blue energy blocks.
    utils.FrontClaw.loads += 1
    utils.FrontClaw.lift()

    # Turns to top house.
    ev3pid.GyroTurn(450, True, True).run()
    DRIVE_BASE.reset_angle()

    # # Scans blocks at top house.
    # scanHouseBlocksProcedure(utils.DepositPoint.TOP_HOUSE, 450,
    #     lambda: LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == Color.BLACK, thenHoldMotors=False)
    # DRIVE_BASE.run_angle(200, 50)
    # wait(50)
    # utils.RunLogic.houses[utils.DepositPoint.TOP_HOUSE].reverse()       # Because the robot is scanning in reverse.

    # Move to top house
    gyroStraightForwardsToTopHouse = ev3pid.GyroStraight(1000, 450)
    gyroStraightForwardsToTopHouse.runUntil(lambda: DRIVE_BASE.angle() > 400)
    gyroStraightForwardsToTopHouse.speed = 500
    gyroStraightForwardsToTopHouse.runUntil(lambda: LEFT_COLOR.color() == Color.BLACK or \
        RIGHT_COLOR.color() == Color.BLACK)
    wait(25)
    preciseLineSquaringProcedure(ev3pid.LinePosition.BEHIND)
    GYRO.reset_angle(450)
    DRIVE_BASE.run_angle(-400, 100)

    # Moves to neutral position for block deposition.
    ev3pid.GyroTurn(540, True, False).run()
    utils.RearClaw.closeGate(wait=False)
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(-400, 540).runUntil(lambda: DRIVE_BASE.angle() < -250)
    DRIVE_BASE.hold()
    wait(50)

def depositBlocksAtTopHouse():

    print("-" * 10, "depositBlocksAtTopHouse")

    EnergyBlockDeposition(utils.DepositPoint.TOP_HOUSE, 540, EnergyBlockDeposition.FacingDirection.AWAY).run()

    # Drives to storage battery.
    gyroStraightToBlackLineWithSensorCheckProcedure(speed=500, gyroAngle=720)
    if LEFT_COLOR.color() == Color.GREEN or RIGHT_COLOR.color() == Color.GREEN:
        while not (LEFT_COLOR.color() == Color.BLACK or RIGHT_COLOR.color() == Color.BLACK):
            DRIVE_BASE.run(-300)
    DRIVE_BASE.hold()
    preciseLineSquaringProcedure(ev3pid.LinePosition.BEHIND)
    GYRO.reset_angle(720)
    wait(50)

def depositBlocksAtStorageBattery():

    print("-" * 10, "depositBlocksAtStorageBattery")

    # Moves to neutral position for block deposition.
    DRIVE_BASE.reset_angle()
    ev3pid.GyroStraight(-200, 720).runUntil(lambda: DRIVE_BASE.angle() < -165)
    DRIVE_BASE.hold()

    EnergyBlockDeposition(utils.DepositPoint.STORAGE_BATTERY, 720, EnergyBlockDeposition.FacingDirection.TOWARDS).run()

    utils.FrontClaw.goTo(0.79)
    gyroStraightToBlackLineWithSensorCheckProcedure(speed=500, gyroAngle=720)

def depositBlocksAtRightHouse():

    print("-" * 10, "depositBlocksAtRightHouse")

    # Turns and tracks the black line to the right house.
    ev3pid.GyroTurn(630, False, True).run()
    DRIVE_BASE.reset_angle()
    lineTrackToRightHouse = ev3pid.LineTrack(800, ev3pid.LineEdge.RIGHT, LEFT_COLOR)
    lineTrackToRightHouse.runUntil(lambda: DRIVE_BASE.angle() > 360)
    lineTrackToRightHouse.speed = 400
    lineTrackToRightHouse.runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    DRIVE_BASE.hold()
    wait(25)

    # Moves to neutral position for block deposition.
    ev3pid.GyroTurn(720, True, True).run()
    gyroStraightToBlackLineWithSensorCheckProcedure(-500, 720)
    wait(50)

    EnergyBlockDeposition(utils.DepositPoint.RIGHT_HOUSE, 720, EnergyBlockDeposition.FacingDirection.AWAY).run()

    gyroStraightToBlackLineWithSensorCheckProcedure(-400, 900)
    preciseLineSquaringProcedure(ev3pid.LinePosition.BEHIND)
    GYRO.reset_angle(900)
    wait(50)

def depositBlocksAtLeftHouse():

    print("-" * 10, "depositBlocksAtLeftHouse")

    # Turns and tracks the black line to the left house.
    ev3pid.GyroTurn(810, False, True).run()
    DRIVE_BASE.reset_angle()
    lineTrackToLeftHouse = ev3pid.LineTrack(1000, ev3pid.LineEdge.RIGHT, LEFT_COLOR)
    lineTrackToLeftHouse.runUntil(lambda: DRIVE_BASE.angle() > 360)
    lineTrackToLeftHouse.runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    lineTrackToLeftHouse.runUntil(lambda: RIGHT_COLOR.color() == Color.WHITE)
    lineTrackToLeftHouse.runUntil(lambda: RIGHT_COLOR.color() == Color.BLACK)
    lineTrackTargetAngle = DRIVE_BASE.angle() + 550
    lineTrackToLeftHouse.speed = 600
    lineTrackToLeftHouse.runUntil(lambda: DRIVE_BASE.angle() >= lineTrackTargetAngle)
    LEFT_MOTOR.hold()

    # Moves to neutral position for block deposition.
    ev3pid.GyroTurn(720, False, True).run()

    gyroStraightToBlackLineWithSensorCheckProcedure(-500, 720)

    EnergyBlockDeposition(utils.DepositPoint.LEFT_HOUSE, 720, EnergyBlockDeposition.FacingDirection.TOWARDS).run()

def returnToStartZone():

    print("-" * 10, "returnToBase")

    utils.FrontClaw.MOTOR.dc(50)
    utils.RearClaw.MOTOR.dc(50)
    utils.FrontClaw.MOTOR.dc(50)
    utils.RearClaw.MOTOR.dc(50)

    # Returns to the start zone.
    ev3pid.GyroTurn(700, True, True).run()
    DRIVE_BASE.run_time(-1200, 2000)

#endregion
