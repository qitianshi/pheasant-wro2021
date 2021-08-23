# Logic.py
# Created on 9 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# For handling run logic.


# pylint: disable=F0401
from pybricks.parameters import Color                                       # type: ignore
# pylint: enable=F0401

class Logic:

    # Robot storage
    blocks = []

    # Run randomization
    surplus = None
    houses = {}

    # Positions where energy blocks can be deposited (enum workaround).
    class DepositPoint:

        LEFT_HOUSE = 0
        TOP_HOUSE = 1
        RIGHT_HOUSE = 2
        STORAGE = 3

    @classmethod
    def blockDeposit(cls, point: DepositPoint):
        
        """
        Gives the correct placement of blocks for each house and the storage battery.

        :param depositPoint: The requested deposit point.
        :return: The placement of energy blocks for the requested deposit point.
        :rtype: (Color, Color)
        """

        result = []

        for i in cls.houses:
            if len(i) == 2:
                result.append(i)
            else:
                # For the house that only has one requirement block, the other energy type will be the surplus.
                result.append((i, cls.surplus))

        # To find the energy type that is only requested once.
        flattenedHouses = (item for sublist in cls.houses for item in sublist)
        missingColor = None
        for i in (Color.BLUE, Color.YELLOW, Color.GREEN):
            if flattenedHouses.count(i) == 1:
                missingColor = i
                break

        # For the battery.
        result.append((cls.surplus, missingColor))

        return result
