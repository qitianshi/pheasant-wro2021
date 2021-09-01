# RunLogic.py
# Created on 9 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# For handling run logic.


# pylint: disable=F0401
from pybricks.parameters import Color                                       # type: ignore
# pylint: enable=F0401

# Positions where energy blocks can be deposited (enum workaround).
class DepositPoint:
    LEFT_HOUSE = 0
    TOP_HOUSE = 1
    RIGHT_HOUSE = 2
    STORAGE = 3

# Block colors and symbolic representations (enum workaround).
class BlockColor:

    # Colors
    GREEN = 0
    BLUE = 1
    YELLOW = 2

    # Symbols
    SURPLUS = 3
    FRONT = 4
    REAR = 5

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

            return [BlockColor.SURPLUS, missingColor]

        elif len(cls.houses[point]) == 2:
            return cls.houses[point]
        else:
            return cls.houses[point].append(BlockColor.SURPLUS)

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
