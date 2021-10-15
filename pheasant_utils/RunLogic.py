# RunLogic.py
# Created on 9 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# For handling run logic.


from pybricks.parameters import Color

# Positions where energy blocks can be deposited.
class DepositPoint:
    LEFT_HOUSE = hash("LEFT_HOUSE")        #HACK: enum workaround.
    TOP_HOUSE = hash("TOP_HOUSE")
    RIGHT_HOUSE = hash("RIGHT_HOUSE")
    STORAGE_BATTERY = hash("STORAGE_BATTERY")

# Block colors and symbolic representations.
class BlockColor:

    # Values are used to sort preferred deposit order.

    # Colors
    BLUE = 0            # On front claw
    GREEN = 2           # On rear claw
    YELLOW = 3

    # Symbols
    SURPLUS = 1
    FRONT = SURPLUS                        # FRONT and REAR are aliases for the colors they represent. Their values
    REAR = YELLOW                          # can be flipped when the robot realigns its undercarriage storage.

    @classmethod
    def flipUndercarriageStorage(cls):
        cls.FRONT, cls.REAR = cls.REAR, cls.FRONT

class RunLogic:

    # Robot undercarriage storage
    undercarriageStorage = [BlockColor.YELLOW, BlockColor.YELLOW, BlockColor.SURPLUS, BlockColor.SURPLUS]

    # Run randomization
    houses = {DepositPoint.LEFT_HOUSE: [], DepositPoint.TOP_HOUSE: [], DepositPoint.RIGHT_HOUSE: []}

    @classmethod
    def blocksAtPoint(cls, point: DepositPoint):

        if point == DepositPoint.STORAGE_BATTERY:

            flattenedHouses = (color for house in cls.houses.values() for color in house)
            missingColor = None
            for i in (BlockColor.BLUE, BlockColor.YELLOW, BlockColor.GREEN):
                if flattenedHouses.count(i) == 1:
                    missingColor = i
                    break

            return sorted([BlockColor.SURPLUS, missingColor])

        elif len(cls.houses[point]) == 2:
            return sorted(cls.houses[point])
        else:
            return sorted(cls.houses[point].append(BlockColor.SURPLUS))

    @staticmethod
    def convertEv3ColorToBlockColor(color: Color) -> BlockColor:

        if color == Color.GREEN:
            return BlockColor.GREEN
        elif color == Color.BLUE:
            return BlockColor.BLUE
        elif color == Color.YELLOW:
            return BlockColor.YELLOW
        else:
            return None
