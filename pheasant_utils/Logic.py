# Logic.py
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

class Logic:

    # Robot storage
    robotStorage = []

    # Run randomization
    surplus = None
    houses = {DepositPoint.LEFT_HOUSE: [], DepositPoint.TOP_HOUSE: [], DepositPoint.RIGHT_HOUSE: []}

    @classmethod
    def blocksAtPoint(cls, point: DepositPoint):

        if point == DepositPoint.STORAGE:
            
            flattenedHouses = (color for house in cls.houses.values() for color in house)
            missingColor = None
            for i in (Color.BLUE, Color.YELLOW, Color.GREEN):
                if flattenedHouses.count(i) == 1:
                    missingColor = i
                    break

            return [cls.surplus, missingColor]

        elif len(cls.houses[point]) == 2:
            return cls.houses[point]
        else:
            return cls.houses[point].append(cls.surplus)
