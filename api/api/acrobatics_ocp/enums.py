from enum import Enum


class PreferredTwistSide(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class SportType(str, Enum):
    TRAMPOLINE = "trampoline"


class Position(str, Enum):
    STRAIGHT = "straight"
    TUCK = "tuck"
    PIKE = "pike"


class MinimizeOrMaximize(str, Enum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class ObjectiveType(str, Enum):
    MAYER = "mayer"
    LAGRANGE = "lagrange"


class PenaltyFcn(str, Enum):
    pass


class GenericFcn(PenaltyFcn):
    minimize_angular_momentum = "MINIMIZE_ANGULAR_MOMENTUM"
    minimize_com_position = "MINIMIZE_COM_POSITION"
    minimize_com_velocity = "MINIMIZE_COM_VELOCITY"
    minimize_linear_momentum = "MINIMIZE_LINEAR_MOMENTUM"
    minimize_control = "MINIMIZE_CONTROL"
    minimize_power = "MINIMIZE_POWER"
    minimize_states = "MINIMIZE_STATES"
    minimize_markers = "MINIMIZE_MARKERS"
    minimize_markers_acceleration = "MINIMIZE_MARKERS_ACCELERATION"
    minimize_markers_velocity = "MINIMIZE_MARKERS_VELOCITY"
    minimize_segment_rotation = "MINIMIZE_SEGMENT_ROTATION"
    minimize_segment_velocity = "MINIMIZE_SEGMENT_VELOCITY"
    proportional_control = "PROPORTIONAL_CONTROL"
    proportional_state = "PROPORTIONAL_STATE"
    superimpose_markers = "SUPERIMPOSE_MARKERS"
    track_marker_with_segment_axis = "TRACK_MARKER_WITH_SEGMENT_AXIS"
    track_segment_with_custom_rt = "TRACK_SEGMENT_WITH_CUSTOM_RT"
    track_vector_orientations_from_markers = "TRACK_VECTOR_ORIENTATIONS_FROM_MARKERS"
    minimize_time = "MINIMIZE_TIME"
    minimize_q_dot = "MINIMIZE_Q_DOT"


class ConstraintFcn(PenaltyFcn):
    time_constraint = "TIME_CONSTRAINT"
    continuity = "CONTINUITY"
    track_power = "TRACK_POWER"
