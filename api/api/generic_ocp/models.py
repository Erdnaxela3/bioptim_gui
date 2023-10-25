from typing import Optional

from bioptim import Node, QuadratureRule
from pydantic import BaseModel

from acrobatics_ocp.enums import *


class Penalty(BaseModel):
    penalty_type: str
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


class Phase(BaseModel):
    nb_shooting_points: int
    duration: float
    dynamics: str
    objectives: list[Objective]
    constraints: list[Constraint]
