# LineTrack.py
# Created on 8 Jul 2021 for Team Pheasant.
# Copyright © 2021 Qi Tianshi. All rights reserved.

# Implements line alignment using two reflected light intensity sensors.


from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from .PIDLoop import PIDLoop

class LineSquare(PIDLoop):

    # TODO: Add default tuning values for line squaring.
    kp_DEFAULT = None
    ki_DEFAULT = None
    kd_DEFAULT = None

    def __init__(self,
                 ports: (Port),
                 threshold: int,
                 kp: float = kp_DEFAULT,
                 ki: float = ki_DEFAULT,
                 kd: float = kd_DEFAULT) -> None:

        self.ports = ports
        super().__init__(threshold, kp, ki, kd)

        self.__run()

    # TODO: Implement movement control.
    def __run(self):
        pass
