# BlockPlacement.py
# Created on 9 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Computes placement of energy unit blocks.

# pylint: disable=F0401
from pybricks.parameters import Color       # type: ignore
# pylint: enable=F0401

def blockPlacement(surplusColor, houses):
    
    """
    Gives the correct placement of blocks for each house and the storage battery.

    :param surplusColor: The color of the surplus energy.
    :type surplusColor: Color
    :param houses: The energy requirement of each house, arranged from left to right.
    :type houses: ((Color, Color), (Color, Color), (Color, Color))
    :return: The placement of energy blocks for each house and the storage battery, arranged from the left house to the right house, then the storage battery.
    :rtype: [(Color, Color), (Color, Color), (Color, Color), (Color, Color)]
    """

    result = []

    for i in houses:
        if len(i) == 2:
            result.append(i)
        else:
            result.append((i, surplusColor))        # For the house that only has one requirement block, the other energy type will be the surplus.

    # To find the energy type that is only requested once.
    flattenedHouses = (item for sublist in houses for item in sublist)
    missingColor = None
    for i in (Color.BLUE, Color.YELLOW, Color.GREEN):
        if flattenedHouses.count(i) == 1:
            missingColor = i
            break

    # For the battery.
    result.append((surplusColor, missingColor))

    return result
