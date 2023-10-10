from bioptim import QuadratureRule, Node
from pydantic import BaseModel

from acrobatics_ocp.enums import (
    Position,
    SportType,
    PreferredTwistSide,
    ObjectiveType,
    GenericFcn,
    ConstraintFcn,
    PenaltyFcn,
)


class NbSomersaultsRequest(BaseModel):
    nb_somersaults: int


class ModelPathRequest(BaseModel):
    model_path: str


class FinalTimeRequest(BaseModel):
    final_time: float


class FinalTimeMarginRequest(BaseModel):
    final_time_margin: float


class PositionRequest(BaseModel):
    position: Position


class SportTypeRequest(BaseModel):
    sport_type: SportType


class PreferredTwistSideRequest(BaseModel):
    preferred_twist_side: PreferredTwistSide


class NbShootingPointsRequest(BaseModel):
    nb_shooting_points: int


class SomersaultDurationRequest(BaseModel):
    duration: float


class NbHalfTwistsRequest(BaseModel):
    nb_half_twists: int


class NodesRequest(BaseModel):
    nodes: Node


class QuadraticRequest(BaseModel):
    quadratic: bool


class ExpandRequest(BaseModel):
    expand: bool


class TargetRequest(BaseModel):
    target: list = None


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
    penalty_type: PenaltyFcn


class ConstraintFcnRequest(BaseModel):
    penalty_type: ConstraintFcn


class ObjectiveFcnRequest(BaseModel):
    penalty_type: GenericFcn


class ArgumentRequest(BaseModel):
    key: str
