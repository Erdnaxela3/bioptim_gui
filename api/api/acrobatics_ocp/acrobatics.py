import inspect
import json

import bioptim
from bioptim import ObjectiveFcn
from fastapi import APIRouter, HTTPException

from acrobatics_ocp.acrobatics_responses import *
import acrobatics_ocp.acrobatics_code_generation as acrobatics_code_generation
import acrobatics_ocp.acrobatics_somersaults as acrobatics_somersaults

router = APIRouter(
    prefix="/acrobatics",
    tags=["acrobatics"],
    responses={404: {"description": "Not found"}},
)
router.include_router(acrobatics_code_generation.router)
router.include_router(
    acrobatics_somersaults.router,
    prefix="/somersaults_info",
    tags=["somersaults"],
    responses={404: {"description": "Not found"}},
)

datafile = "acrobatics_data.json"

default_objective = {
    "objective_type": "lagrange",
    "penalty_type": "MINIMIZE_CONTROL",
    "nodes": "all_shooting",
    "quadratic": True,
    "expand": True,
    "target": None,
    "derivative": False,
    "integration_rule": "rectangle_left",
    "multi_thread": False,
    "weight": 1.0,
    "arguments": [
        {"name": "key", "value": "tau", "type": "string"},
    ],
}

default_constraint = {
    "penalty_type": "TIME_CONSTRAINT",
    "nodes": "end",
    "quadratic": True,
    "expand": True,
    "target": None,
    "derivative": False,
    "integration_rule": "rectangle_left",
    "multi_thread": False,
    "arguments": [],
}

default_somersaults_info = {
    "nb_shooting_points": 24,
    "nb_half_twists": 0,
    "duration": 1.0,
    "objectives": [
        {
            "objective_type": "lagrange",
            "penalty_type": "MINIMIZE_CONTROL",
            "nodes": "all_shooting",
            "quadratic": True,
            "expand": True,
            "target": None,
            "derivative": False,
            "integration_rule": "rectangle_left",
            "multi_thread": False,
            "weight": 100.0,
            "arguments": [
                {"name": "key", "value": "tau", "type": "string"},
            ],
        },
        {
            "objective_type": "mayer",
            "penalty_type": "MINIMIZE_TIME",
            "nodes": "end",
            "quadratic": True,
            "expand": True,
            "target": None,
            "derivative": False,
            "integration_rule": "rectangle_left",
            "multi_thread": False,
            "weight": 1.0,
            "arguments": [
                {"name": "min_bound", "value": 0.9, "type": "float"},
                {"name": "max_bound", "value": 1.1, "type": "float"},
            ],
        },
    ],
    "constraints": [],
}

min_to_originial_dict = {
    "MINIMIZE_ANGULAR_MOMENTUM": "MINIMIZE_ANGULAR_MOMENTUM",
    "MINIMIZE_COM_POSITION": "MINIMIZE_COM_POSITION",
    "MINIMIZE_COM_VELOCITY": "MINIMIZE_COM_VELOCITY",
    "MINIMIZE_CONTROL": "MINIMIZE_CONTROL",
    "MINIMIZE_LINEAR_MOMENTUM": "MINIMIZE_LINEAR_MOMENTUM",
    "MINIMIZE_MARKERS": "MINIMIZE_MARKERS",
    "MINIMIZE_MARKERS_ACCELERATION": "MINIMIZE_MARKERS_ACCELERATION",
    "MINIMIZE_MARKERS_VELOCITY": "MINIMIZE_MARKERS_VELOCITY",
    "MINIMIZE_POWER": "MINIMIZE_POWER",
    "MINIMIZE_QDDOT": "MINIMIZE_QDDOT",
    "MINIMIZE_SEGMENT_ROTATION": "MINIMIZE_SEGMENT_ROTATION",
    "MINIMIZE_SEGMENT_VELOCITY": "MINIMIZE_SEGMENT_VELOCITY",
    "MINIMIZE_STATE": "MINIMIZE_STATE",
    "MINIMIZE_TIME": "MINIMIZE_TIME",
    "PROPORTIONAL_CONTROL": "PROPORTIONAL_CONTROL",
    "PROPORTIONAL_STATE": "PROPORTIONAL_STATE",
    "MINIMIZE_MARKER_DISTANCE": "SUPERIMPOSE_MARKERS",
    "ALIGN_MARKER_WITH_SEGMENT_AXIS": "TRACK_MARKER_WITH_SEGMENT_AXIS",
    "ALIGN_SEGMENT_WITH_CUSTOM_RT": "TRACK_SEGMENT_WITH_CUSTOM_RT",
    "ALIGN_MARKERS_WITH_VECTOR": "TRACK_VECTOR_ORIENTATIONS_FROM_MARKERS",
}

max_to_originial_dict = {
    "MAXIMIZE_ANGULAR_MOMENTUM": "MINIMIZE_ANGULAR_MOMENTUM",
    "MAXIMIZE_COM_POSITION": "MINIMIZE_COM_POSITION",
    "MAXIMIZE_COM_VELOCITY": "MINIMIZE_COM_VELOCITY",
    "MAXIMIZE_CONTROL": "MINIMIZE_CONTROL",
    "MAXIMIZE_LINEAR_MOMENTUM": "MINIMIZE_LINEAR_MOMENTUM",
    "MAXIMIZE_MARKERS": "MINIMIZE_MARKERS",
    "MAXIMIZE_MARKERS_ACCELERATION": "MINIMIZE_MARKERS_ACCELERATION",
    "MAXIMIZE_MARKERS_VELOCITY": "MINIMIZE_MARKERS_VELOCITY",
    "MAXIMIZE_POWER": "MINIMIZE_POWER",
    "MAXIMIZE_QDDOT": "MINIMIZE_QDDOT",
    "MAXIMIZE_SEGMENT_ROTATION": "MINIMIZE_SEGMENT_ROTATION",
    "MAXIMIZE_SEGMENT_VELOCITY": "MINIMIZE_SEGMENT_VELOCITY",
    "MAXIMIZE_STATE": "MINIMIZE_STATE",
    "MAXIMIZE_TIME": "MINIMIZE_TIME",
    "PROPORTIONAL_CONTROL": "PROPORTIONAL_CONTROL",
    "PROPORTIONAL_STATE": "PROPORTIONAL_STATE",
    "MAXIMIZE_MARKER_DISTANCE": "SUPERIMPOSE_MARKERS",
    "MARKER_AWAY_FROM_SEGMENT_AXIS": "TRACK_MARKER_WITH_SEGMENT_AXIS",
    "SEGMENT_PERPENDICULAR_WITH_CUSTOM_RT": "TRACK_SEGMENT_WITH_CUSTOM_RT",
    "ALIGN_MARKERS_WITH_VECTOR_PERPENDICULAR": "TRACK_VECTOR_ORIENTATIONS_FROM_MARKERS",
}

min_to_max_dict = {
    "MINIMIZE_ANGULAR_MOMENTUM": "MAXIMIZE_ANGULAR_MOMENTUM",
    "MINIMIZE_COM_POSITION": "MAXIMIZE_COM_POSITION",
    "MINIMIZE_COM_VELOCITY": "MAXIMIZE_COM_VELOCITY",
    "MINIMIZE_CONTROL": "MAXIMIZE_CONTROL",
    "MINIMIZE_LINEAR_MOMENTUM": "MAXIMIZE_LINEAR_MOMENTUM",
    "MINIMIZE_MARKERS": "MAXIMIZE_MARKERS",
    "MINIMIZE_MARKERS_ACCELERATION": "MAXIMIZE_MARKERS_ACCELERATION",
    "MINIMIZE_MARKERS_VELOCITY": "MAXIMIZE_MARKERS_VELOCITY",
    "MINIMIZE_POWER": "MAXIMIZE_POWER",
    "MINIMIZE_QDDOT": "MAXIMIZE_QDDOT",
    "MINIMIZE_SEGMENT_ROTATION": "MAXIMIZE_SEGMENT_ROTATION",
    "MINIMIZE_SEGMENT_VELOCITY": "MAXIMIZE_SEGMENT_VELOCITY",
    "MINIMIZE_STATE": "MAXIMIZE_STATE",
    "MINIMIZE_TIME": "MAXIMIZE_TIME",
    "PROPORTIONAL_CONTROL": "PROPORTIONAL_CONTROL",
    "PROPORTIONAL_STATE": "PROPORTIONAL_STATE",
    "MINIMIZE_MARKER_DISTANCE": "MAXIMIZE_MARKER_DISTANCE",
    "ALIGN_MARKER_WITH_SEGMENT_AXIS": "MARKER_AWAY_FROM_SEGMENT_AXIS",
    "ALIGN_SEGMENT_WITH_CUSTOM_RT": "SEGMENT_PERPENDICULAR_WITH_CUSTOM_RT",
    "ALIGN_MARKERS_WITH_VECTOR": "ALIGN_MARKERS_WITH_VECTOR_PERPENDICULAR",
}

max_to_min_dict = {v: k for k, v in min_to_max_dict.items()}


def get_args(penalty_fcn) -> list:
    penalty_fcn = penalty_fcn.value[0]
    # arguments
    arg_specs = inspect.getfullargspec(penalty_fcn)
    defaults = arg_specs.defaults
    arguments = arg_specs.annotations

    formatted_arguments = [
        {"name": k, "value": None, "type": str(v)} for k, v in arguments.items()
    ]

    if defaults:
        l_defaults = len(defaults)
        for i in range(l_defaults):
            formatted_arguments[i]["value"] = defaults[i]

    formatted_arguments = [
        arg
        for arg in formatted_arguments
        if arg["name"] not in ("_", "penalty", "controller")
    ]

    return formatted_arguments


def obj_arguments(objective_type: str, penalty_type: str) -> list:
    penalty_type = penalty_type.upper().replace(" ", "_")
    if objective_type == "mayer":
        penalty_fcn = getattr(ObjectiveFcn.Mayer, penalty_type)
    elif objective_type == "lagrange":
        penalty_fcn = getattr(ObjectiveFcn.Lagrange, penalty_type)
    else:
        raise HTTPException(404, f"{objective_type} not found")

    arguments = get_args(penalty_fcn)
    return arguments


def constraint_arguments(penalty_type: str) -> list:
    penalty_type = penalty_type.upper().replace(" ", "_")
    try:
        penalty_fcn = getattr(bioptim.ConstraintFcn, penalty_type)
    except AttributeError:
        raise HTTPException(404, f"{penalty_type} not found")

    arguments = get_args(penalty_fcn)
    return arguments


def add_somersault_info(n: int = 1) -> None:
    if n < 1:
        raise ValueError("n must be positive")

    data = read_acrobatics_data()
    somersaults_info = data["somersaults_info"]
    before = len(somersaults_info)
    n_somersaults = before + n
    final_time = data["final_time"]
    for i in range(0, before):
        somersaults_info[i]["duration"] = final_time / n_somersaults

    for i in range(before, before + n):
        somersaults_info.append(default_somersaults_info)
        somersaults_info[i]["duration"] = final_time / n_somersaults

    data["somersaults_info"] = somersaults_info
    with open(datafile, "w") as f:
        json.dump(data, f)


def remove_somersault_info(n: int = 0) -> None:
    if n < 0:
        raise ValueError("n must be positive")
    data = read_acrobatics_data()
    somersaults_info = data["somersaults_info"]
    before = len(somersaults_info)
    n_somersaults = before - n
    final_time = data["final_time"]
    for i in range(0, n_somersaults):
        somersaults_info[i]["duration"] = final_time / n_somersaults

    for _ in range(n):
        somersaults_info.pop()
    data["somersaults_info"] = somersaults_info
    with open(datafile, "w") as f:
        json.dump(data, f)


def update_acrobatics_data(key: str, value) -> None:
    with open(datafile, "r") as f:
        data = json.load(f)
    data[key] = value
    with open(datafile, "w") as f:
        json.dump(data, f)


def read_acrobatics_data(key: str = None):
    with open(datafile, "r") as f:
        data = json.load(f)
    return data if key is None else data[key]


@router.get("/", response_model=dict)
def get_acrobatics_data():
    data = read_acrobatics_data()
    return data


@router.put("/nb_somersaults", response_model=dict)
def update_nb_somersaults(nb_somersaults: NbSomersaultsRequest):
    old_value = read_acrobatics_data("nb_somersaults")
    new_value = nb_somersaults.nb_somersaults
    if new_value < 0:
        raise HTTPException(status_code=400, detail="nb_somersaults must be positive")

    if new_value > old_value:
        add_somersault_info(new_value - old_value)
    elif new_value < old_value:
        remove_somersault_info(old_value - new_value)

    update_acrobatics_data("nb_somersaults", new_value)

    data = read_acrobatics_data()
    return data


@router.put("/model_path", response_model=ModelPathResponse)
def put_model_path(model_path: ModelPathRequest):
    update_acrobatics_data("model_path", model_path.model_path)
    return ModelPathResponse(model_path=model_path.model_path)


@router.put("/final_time", response_model=FinalTimeResponse)
def put_final_time(final_time: FinalTimeRequest):
    new_value = final_time.final_time
    if new_value < 0:
        raise HTTPException(status_code=400, detail="final_time must be positive")
    update_acrobatics_data("final_time", new_value)
    return FinalTimeResponse(final_time=new_value)


@router.put("/final_time_margin", response_model=FinalTimeMarginResponse)
def put_final_time_margin(final_time_margin: FinalTimeMarginRequest):
    new_value = final_time_margin.final_time_margin
    if new_value < 0:
        raise HTTPException(
            status_code=400, detail="final_time_margin must be positive"
        )
    update_acrobatics_data("final_time_margin", new_value)
    return FinalTimeMarginResponse(final_time_margin=new_value)


@router.get("/position", response_model=list)
def get_position():
    return [side.capitalize() for side in Position]


@router.put("/position", response_model=PositionResponse)
def put_position(position: PositionRequest):
    new_value = position.position.value
    old_value = read_acrobatics_data("position")

    if old_value == new_value:
        raise HTTPException(
            status_code=304,
            detail=f"position is already {position}",
        )

    update_acrobatics_data("position", new_value)
    return PositionResponse(position=new_value)


@router.get("/sport_type", response_model=list)
def put_sport_type():
    return [side.capitalize() for side in SportType]


@router.put("/sport_type", response_model=SportTypeResponse)
def put_sport_type(sport_type: SportTypeRequest):
    new_value = sport_type.sport_type.value
    old_value = read_acrobatics_data("sport_type")

    if old_value == new_value:
        raise HTTPException(
            status_code=304,
            detail=f"sport_type is already {sport_type}",
        )

    update_acrobatics_data("sport_type", new_value)
    return SportTypeResponse(sport_type=new_value)


@router.get("/preferred_twist_side", response_model=list)
def get_preferred_twist_side():
    return [side.capitalize() for side in PreferredTwistSide]


@router.put("/preferred_twist_side", response_model=PreferredTwistSideResponse)
def put_preferred_twist_side(preferred_twist_side: PreferredTwistSideRequest):
    new_value = preferred_twist_side.preferred_twist_side.value
    old_value = read_acrobatics_data("preferred_twist_side")
    if old_value == new_value:
        raise HTTPException(
            status_code=304,
            detail=f"preferred_twist_side is already {preferred_twist_side}",
        )

    update_acrobatics_data("preferred_twist_side", new_value)
    return PreferredTwistSideResponse(preferred_twist_side=new_value)
