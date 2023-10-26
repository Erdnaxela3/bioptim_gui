from enum import Enum


class PreferredTwistSide(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class SportType(str, Enum):
    TRAMPOLINE = "trampoline"
    DIVING = "diving"


class Position(str, Enum):
    STRAIGHT = "straight"
    TUCK = "tuck"
    PIKE = "pike"


class ObjectiveType(str, Enum):
    MAYER = "mayer"
    LAGRANGE = "lagrange"
