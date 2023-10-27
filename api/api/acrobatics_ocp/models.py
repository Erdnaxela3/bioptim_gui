from pydantic import BaseModel

from penalty.models import Objective, Constraint


class Somersault(BaseModel):
    nb_shooting_points: int
    nb_half_twists: int
    duration: float
    objectives: list[Objective]
    constraints: list[Constraint]
