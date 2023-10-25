from typing import Optional

from bioptim import QuadratureRule, Node
from pydantic import BaseModel

from acrobatics_ocp.enums import (
    Position,
    SportType,
    PreferredTwistSide,
    ObjectiveType,
)


class NbPhasesRequest(BaseModel):
    nb_phases: int


class ModelPathRequest(BaseModel):
    model_path: str


class NbShootingPointsRequest(BaseModel):
    nb_shooting_points: int


class PhaseDurationRequest(BaseModel):
    duration: float


class NodesRequest(BaseModel):
    nodes: Node


class QuadraticRequest(BaseModel):
    quadratic: bool


class ExpandRequest(BaseModel):
    expand: bool


class TargetRequest(BaseModel):
    target: Optional[list] = None


class DerivativeRequest(BaseModel):
    derivative: bool


class IntegrationRuleRequest(BaseModel):
    integration_rule: QuadratureRule


class MultiThreadRequest(BaseModel):
    multi_thread: bool


class WeightRequest(BaseModel):
    weight: float


class ObjectiveTypeRequest(BaseModel):
    objective_type: ObjectiveType


class PenaltyTypeRequest(BaseModel):
    penalty_type: str


class ConstraintFcnRequest(BaseModel):
    penalty_type: str


class ObjectiveFcnRequest(BaseModel):
    penalty_type: str


class ArgumentRequest(BaseModel):
    type: str
    value: int | float | str | list | None
