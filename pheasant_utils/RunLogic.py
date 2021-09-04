# RunLogic.py
# Created on 9 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# For handling run logic.


# pylint: disable=F0401
from pybricks.parameters import Color                                       # type: ignore
# pylint: enable=F0401

# Positions where energy blocks can be deposited.
class DepositPoint:
    LEFT_HOUSE = hash("DepositPoint.LEFT_HOUSE")        # FIXME: Enum workaround
    TOP_HOUSE = hash("DepositPoint.TOP_HOUSE")
    RIGHT_HOUSE = hash("DepositPoint.RIGHT_HOUSE")
    STORAGE = hash("DepositPoint.STORAGE")

# Block colors and symbolic representations.
class BlockColor:

    # Colors
    BLUE = 0
    GREEN = 2
    YELLOW = 3

    # Symbols
    FRONT = 1           # FRONT and REAR are aliases for the colors they represent. Their values can be flipped when the
    REAR = 3            # robot realigns itself.
    SURPLUS = 1

class RunLogic:

    # Robot storage
    robotStorage = [BlockColor.YELLOW, BlockColor.YELLOW, BlockColor.SURPLUS, BlockColor.SURPLUS]

    # Run randomization
    houses = {DepositPoint.LEFT_HOUSE: [], DepositPoint.TOP_HOUSE: [], DepositPoint.RIGHT_HOUSE: []}

    @classmethod
    def blocksAtPoint(cls, point: DepositPoint):

        if point == DepositPoint.STORAGE:
            
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
