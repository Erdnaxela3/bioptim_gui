from bioptim_gui_api.variables.straight_acrobatics_variables import (
    StraightAcrobaticsVariables,
)


class PikeAcrobaticsVariables(StraightAcrobaticsVariables):
    X = 0
    Y = 1
    Z = 2
    Xrot = 3
    Yrot = 4
    Zrot = 5
    ZrotRightUpperArm = 6
    YrotRightUpperArm = 7
    ZrotRightLowerArm = 8
    XrotRightLowerArm = 9
    ZrotLeftUpperArm = 10
    YrotLeftUpperArm = 11
    ZrotLeftLowerArm = 12
    XrotLeftLowerArm = 13
    XrotUpperLegs = 14
    YrotUpperLegs = 15
    XrotLowerLegs = 16

    nb_q, nb_qdot, nb_tau = 17, 17, 11
