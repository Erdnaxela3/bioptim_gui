from typing import Optional

from bioptim import Node, QuadratureRule
from bioptim.misc.fcn_enum import FcnEnum
from pydantic import BaseModel

from acrobatics_ocp.enums import *


class NbSomersaultsInput(BaseModel):
    nb_somersaults: int


class ModelPathInput(BaseModel):
    model_path: str


class FinalTimeInput(BaseModel):
    final_time: float


class FinalTimeMarginInput(BaseModel):
    final_time_margin: float


class PositionInput(BaseModel):
    position: Position


class SportTypeInput(BaseModel):
    sport_type: SportType


class PreferredTwistSideInput(BaseModel):
    preferred_twist_side: PreferredTwistSide


class NbShootingPoints(BaseModel):
    nb_shooting_points: int


class SomersaultDuration(BaseModel):
    duration: float


class NbHalfTwists(BaseModel):
    nb_half_twists: int


class Weight(BaseModel):
    weight: float


class ObjectiveTypeInput(BaseModel):
    objective_type: ObjectiveType


class PenaltyTypeInput(BaseModel):
    penalty_type: FcnEnum


class ArgumentRequest(BaseModel):
    key: str


class ArgumentResponse(BaseModel):
    key: str
    type: str
    value: int | float | str | list


class NodesInput(BaseModel):
    nodes: Node


class QuadraticInput(BaseModel):
    quadratic: bool


class ExpandInput(BaseModel):
    expand: bool


class TargetInput(BaseModel):
    target: Optional[list] = None


class DerivativeInput(BaseModel):
    derivative: bool


class IntegrationRuleInput(BaseModel):
    integration_rule: QuadratureRule


class MultiThreadInput(BaseModel):
    multi_thread: bool


class Penalty(BaseModel):
    penalty_type: GenericFcn
    nodes: Node
    quadratic: bool = True
    expand: bool = True
    target: Optional[list] = None
    derivative: bool = False
    integration_rule: QuadratureRule = QuadratureRule.RECTANGLE_LEFT
    multi_thread: bool = False
    arguments: dict


class Objective(Penalty):
    weight: float = 1.0
    objective_type: ObjectiveType = ObjectiveType.MAYER


class Constraint(Penalty):
    pass


class Somersault(BaseModel):
    nb_shooting_points: int
    nb_half_twists: int
    duration: float
    objectives: list[Objective]
    constraints: list[Constraint]
