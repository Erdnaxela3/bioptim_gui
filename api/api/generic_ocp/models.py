from pydantic import BaseModel

from penalty.models import Objective, Constraint


class Phase(BaseModel):
    nb_shooting_points: int
    duration: float
    dynamics: str
    objectives: list[Objective]
    constraints: list[Constraint]
