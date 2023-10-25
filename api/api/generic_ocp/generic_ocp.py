import inspect
import json

import bioptim
from bioptim import ObjectiveFcn
from fastapi import APIRouter, HTTPException

from generic_ocp.generic_ocp_responses import *

from generic_ocp.generic_ocp_requests import MultiThreadRequest

router = APIRouter(
    prefix="/generic_ocp",
    tags=["generic_ocp"],
    responses={404: {"description": "Not found"}},
)

datafile = "generic_ocp_data.json"

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

default_phases_info = {
    "nb_shooting_points": 24,
    "duration": 1.0,
    "objectives": [],
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


def add_phase_info(n: int = 1) -> None:
    if n < 1:
        raise ValueError("n must be positive")

    data = read_generic_ocp_data()
    phases_info = data["phases_info"]
    before = len(phases_info)
    n_phases = before + n

    for i in range(before, before + n):
        phases_info.append(default_phases_info)

    data["phases_info"] = phases_info
    with open(datafile, "w") as f:
        json.dump(data, f)


def remove_phase_info(n: int = 0) -> None:
    if n < 0:
        raise ValueError("n must be positive")
    data = read_generic_ocp_data()
    phases_info = data["phases_info"]
    before = len(phases_info)
    n_phases = before - n

    for _ in range(n):
        phases_info.pop()
    data["phases_info"] = phases_info
    with open(datafile, "w") as f:
        json.dump(data, f)


def update_generic_ocp_data(key: str, value) -> None:
    with open(datafile, "r") as f:
        data = json.load(f)
    data[key] = value
    with open(datafile, "w") as f:
        json.dump(data, f)


def read_generic_ocp_data(key: str = None):
    with open(datafile, "r") as f:
        data = json.load(f)
    return data if key is None else data[key]


@router.get("/", response_model=dict)
def get_generic_ocp_data():
    data = read_generic_ocp_data()
    return data


@router.put("/nb_phases", response_model=dict)
def update_nb_phases(nb_phases: NbPhasesRequest):
    old_value = read_generic_ocp_data("nb_phases")
    new_value = nb_phases.nb_phases
    if new_value < 0:
        raise HTTPException(status_code=400, detail="nb_phases must be positive")

    if new_value > old_value:
        add_phase_info(new_value - old_value)
    elif new_value < old_value:
        remove_phase_info(old_value - new_value)

    update_generic_ocp_data("nb_phases", new_value)

    data = read_generic_ocp_data()
    return data


@router.put("/model_path", response_model=ModelPathResponse)
def put_model_path(model_path: ModelPathRequest):
    update_generic_ocp_data("model_path", model_path.model_path)
    return ModelPathResponse(model_path=model_path.model_path)


# phases info endpoints


@router.get("/phases_info/", response_model=list)
def get_phases_info():
    phases_info = read_generic_ocp_data("phases_info")
    return phases_info


@router.get("/phases_info/{phase_index}", response_model=dict)
def get_phases_info(phase_index: int):
    n_phases = read_generic_ocp_data("nb_phases")
    if phase_index < 0 or phase_index >= n_phases:
        raise HTTPException(
            status_code=404,
            detail=f"phase_index must be between 0 and {n_phases - 1}",
        )
    phases_info = read_generic_ocp_data("phases_info")
    return phases_info[phase_index]


@router.put(
    "/phases_info/{phase_index}/nb_shooting_points",
    response_model=NbShootingPointsResponse,
)
def put_nb_shooting_points(
    phase_index: int, nb_shooting_points: NbShootingPointsRequest
):
    if nb_shooting_points.nb_shooting_points <= 0:
        raise HTTPException(
            status_code=400, detail="nb_shooting_points must be positive"
        )
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index][
        "nb_shooting_points"
    ] = nb_shooting_points.nb_shooting_points
    update_generic_ocp_data("phases_info", phases_info)
    return NbShootingPointsResponse(
        nb_shooting_points=nb_shooting_points.nb_shooting_points
    )


@router.put(
    "/phases_info/{phase_index}/duration",
    response_model=PhaseDurationResponse,
)
def put_duration(phase_index: int, duration: PhaseDurationRequest):
    if duration.duration <= 0:
        raise HTTPException(status_code=400, detail="duration must be positive")
    infos = read_generic_ocp_data()
    phases_info = infos["phases_info"]
    phases_info[phase_index]["duration"] = duration.duration
    update_generic_ocp_data("phases_info", phases_info)
    return PhaseDurationResponse(duration=duration.duration)


# objectives endpoints


@router.get("/phases_info/{phase_index}/objectives", response_model=list)
def get_objectives(phase_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    objectives = phases_info[phase_index]["objectives"]
    return objectives


@router.post("/phases_info/{phase_index}/objectives", response_model=list)
def add_objective(phase_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    objectives = phases_info[phase_index]["objectives"]
    objectives.append(default_objective)
    phases_info[phase_index]["objectives"] = objectives
    update_generic_ocp_data("phases_info", phases_info)
    return objectives


@router.get(
    "/phases_info/{phase_index}/objectives/{objective_index}",
    response_model=list,
)
def get_objective_dropdown_list(phase_index: int, objective_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    objective = phases_info[phase_index]["objectives"][objective_index]
    objective_type = objective["objective_type"]
    if objective_type == "mayer":
        enum = ObjectiveFcn.Mayer
    elif objective_type == "lagrange":
        enum = ObjectiveFcn.Lagrange
    else:
        raise HTTPException(
            status_code=400, detail="objective_type has to be mayer or lagrange"
        )

    # weight = objective["weight"]

    # we don't implement all the objective functions for now
    return [
        "MINIMIZE_ANGULAR_MOMENTUM",
        "MINIMIZE_COM_POSITION",
        "MINIMIZE_COM_VELOCITY",
        "MINIMIZE_CONTROL",
        "MINIMIZE_LINEAR_MOMENTUM",
        "MINIMIZE_MARKERS",
        "MINIMIZE_MARKERS_ACCELERATION",
        "MINIMIZE_MARKERS_VELOCITY",
        "MINIMIZE_POWER",
        "MINIMIZE_QDDOT",
        "MINIMIZE_SEGMENT_ROTATION",
        "MINIMIZE_SEGMENT_VELOCITY",
        "MINIMIZE_STATE",
        "MINIMIZE_TIME",
        "PROPORTIONAL_CONTROL",
        "PROPORTIONAL_STATE",
        "SUPERIMPOSE_MARKERS",
        "TRACK_MARKER_WITH_SEGMENT_AXIS",
        "TRACK_SEGMENT_WITH_CUSTOM_RT",
        "TRACK_VECTOR_ORIENTATIONS_FROM_MARKERS",
    ]
    # return list(min_to_originial_dict.keys()) if weight > 0 else list(max_to_originial_dict.keys())
    # return [e.name for e in enum]


@router.delete(
    "/phases_info/{phase_index}/objectives/{objective_index}",
    response_model=list,
)
def delete_objective(phase_index: int, objective_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    objectives = phases_info[phase_index]["objectives"]
    objectives.pop(objective_index)
    phases_info[phase_index]["objectives"] = objectives
    update_generic_ocp_data("phases_info", phases_info)
    return objectives


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/objective_type",
    response_model=dict,
)
def put_objective_type(
    phase_index: int, objective_index: int, objective_type: ObjectiveTypeRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index][
        "objective_type"
    ] = objective_type.objective_type.value

    objective_type_value = objective_type.objective_type.value
    penalty_type = phases_info[phase_index]["objectives"][objective_index][
        "penalty_type"
    ]
    arguments = obj_arguments(objective_type_value, penalty_type)

    phases_info[phase_index]["objectives"][objective_index]["arguments"] = arguments

    update_generic_ocp_data("phases_info", phases_info)
    data = read_generic_ocp_data()
    return data["phases_info"][phase_index]["objectives"][objective_index]


# common arguments


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/penalty_type",
    response_model=dict,
)
def put_objective_penalty_type(
    phase_index: int, objective_index: int, penalty_type: ObjectiveFcnRequest
):
    penalty_type_value = penalty_type.penalty_type
    phases_info = read_generic_ocp_data("phases_info")

    phases_info[phase_index]["objectives"][objective_index][
        "penalty_type"
    ] = penalty_type_value

    objective_type = phases_info[phase_index]["objectives"][objective_index][
        "objective_type"
    ]
    arguments = obj_arguments(
        objective_type=objective_type, penalty_type=penalty_type_value
    )

    phases_info[phase_index]["objectives"][objective_index]["arguments"] = arguments

    update_generic_ocp_data("phases_info", phases_info)

    data = read_generic_ocp_data()
    return data["phases_info"][phase_index]["objectives"][objective_index]


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/nodes",
    response_model=NodesResponse,
)
def put_objective_nodes(phase_index: int, objective_index: int, nodes: NodesRequest):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index]["nodes"] = nodes.nodes.value
    update_generic_ocp_data("phases_info", phases_info)
    return NodesResponse(nodes=nodes.nodes)


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/quadratic",
    response_model=QuadraticResponse,
)
def put_objective_quadratic(
    phase_index: int, objective_index: int, quadratic: QuadraticRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index][
        "quadratic"
    ] = quadratic.quadratic
    update_generic_ocp_data("phases_info", phases_info)
    return QuadraticResponse(quadratic=quadratic.quadratic)


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/expand",
    response_model=ExpandResponse,
)
def put_objective_expand(phase_index: int, objective_index: int, expand: ExpandRequest):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index]["expand"] = expand.expand
    update_generic_ocp_data("phases_info", phases_info)
    return ExpandResponse(expand=expand.expand)


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/target",
    response_model=TargetResponse,
)
def put_objective_target(phase_index: int, objective_index: int, target: TargetRequest):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index]["target"] = target.target
    update_generic_ocp_data("phases_info", phases_info)
    return TargetResponse(target=target.target)


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/derivative",
    response_model=DerivativeResponse,
)
def put_objective_derivative(
    phase_index: int, objective_index: int, derivative: DerivativeRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index][
        "derivative"
    ] = derivative.derivative
    update_generic_ocp_data("phases_info", phases_info)
    return DerivativeResponse(derivative=derivative.derivative)


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/integration_rule",
    response_model=IntegrationRuleResponse,
)
def put_objective_integration_rule(
    phase_index: int,
    objective_index: int,
    integration_rule: IntegrationRuleRequest,
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index][
        "integration_rule"
    ] = integration_rule.integration_rule.value
    update_generic_ocp_data("phases_info", phases_info)
    return IntegrationRuleResponse(integration_rule=integration_rule.integration_rule)


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/multi_thread",
    response_model=MultiThreadResponse,
)
def put_objective_multi_thread(
    phase_index: int, objective_index: int, multi_thread: MultiThreadRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index][
        "multi_thread"
    ] = multi_thread.multi_thread
    update_generic_ocp_data("phases_info", phases_info)
    return MultiThreadResponse(multi_thread=multi_thread.multi_thread)


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/weight",
    response_model=WeightResponse,
)
def put_objective_weight(phase_index: int, objective_index: int, weight: WeightRequest):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["objectives"][objective_index]["weight"] = weight.weight
    update_generic_ocp_data("phases_info", phases_info)
    return WeightResponse(weight=weight.weight)


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/weight/maximize",
    response_model=dict,
)
def put_objective_weight_maximize(phase_index: int, objective_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    old_weight = phases_info[phase_index]["objectives"][objective_index]["weight"]
    new_weight = -abs(old_weight)

    phases_info[phase_index]["objectives"][objective_index]["weight"] = new_weight
    update_generic_ocp_data("phases_info", phases_info)
    return phases_info[phase_index]["objectives"][objective_index]


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/weight/minimize",
    response_model=dict,
)
def put_objective_weight_minimize(phase_index: int, objective_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    old_weight = phases_info[phase_index]["objectives"][objective_index]["weight"]
    new_weight = abs(old_weight)

    phases_info[phase_index]["objectives"][objective_index]["weight"] = new_weight
    update_generic_ocp_data("phases_info", phases_info)
    return phases_info[phase_index]["objectives"][objective_index]


@router.get(
    "/phases_info/{phase_index}/objectives/{objective_index}/arguments/{key}",
    response_model=ArgumentResponse,
)
def get_objective_arguments(phase_index: int, objective_index: int, key: str):
    phases_info = read_generic_ocp_data("phases_info")
    arguments = phases_info[phase_index]["objectives"][objective_index]["arguments"]

    for argument in arguments:
        if argument["name"] == key:
            return ArgumentResponse(
                key=key, type=argument["type"], value=argument["value"]
            )

    raise HTTPException(
        status_code=404,
        detail=f"{key} not found in arguments of objective {objective_index}",
    )


@router.put(
    "/phases_info/{phase_index}/objectives/{objective_index}/arguments/{key}",
    response_model=ArgumentResponse,
)
def put_objective_arguments(
    phase_index: int, objective_index: int, key: str, argument_req: ArgumentRequest
):
    phases_info = read_generic_ocp_data("phases_info")

    arguments = phases_info[phase_index]["objectives"][objective_index]["arguments"]

    for argument in arguments:
        if argument["name"] == key:
            argument["type"] = argument_req.type
            argument["value"] = argument_req.value

            phases_info[phase_index]["objectives"][objective_index][
                "arguments"
            ] = arguments
            update_generic_ocp_data("phases_info", phases_info)

            return ArgumentResponse(
                key=key, type=argument["type"], value=argument["value"]
            )
    raise HTTPException(
        status_code=404,
        detail=f"{key} not found in arguments of objective {objective_index}",
    )


# constraints endpoints


@router.get("/phases_info/{phase_index}/constraints", response_model=list)
def get_constraints(phase_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    constraints = phases_info[phase_index]["constraints"]
    return constraints


@router.post("/phases_info/{phase_index}/constraints", response_model=list)
def add_constraint(phase_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    constraints = phases_info[phase_index]["constraints"]
    constraints.append(default_constraint)
    phases_info[phase_index]["constraints"] = constraints
    update_generic_ocp_data("phases_info", phases_info)
    return constraints


@router.get(
    "/phases_info/{phase_index}/constraints/{constraint_index}",
    response_model=list,
)
def get_constraints_dropdown_list():
    # we don't use all the available constraints for now
    return [
        "CONTINUITY",
        "TIME_CONSTRAINT",
    ]
    # if all constraints have to be implemented
    # return [e.name for e in ConstraintFcn]


@router.delete(
    "/phases_info/{phase_index}/constraints/{constraint_index}",
    response_model=list,
)
def delete_constraint(phase_index: int, constraint_index: int):
    phases_info = read_generic_ocp_data("phases_info")
    constraints = phases_info[phase_index]["constraints"]
    constraints.pop(constraint_index)
    phases_info[phase_index]["constraints"] = constraints
    update_generic_ocp_data("phases_info", phases_info)
    return constraints


# common arguments


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/penalty_type",
    response_model=dict,
)
def put_constraint_penalty_type(
    phase_index: int, constraint_index: int, penalty_type: ConstraintFcnRequest
):
    penalty_type_value = penalty_type.penalty_type
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["constraints"][constraint_index][
        "penalty_type"
    ] = penalty_type_value

    arguments = constraint_arguments(penalty_type.penalty_type)
    phases_info[phase_index]["constraints"][constraint_index]["arguments"] = arguments

    update_generic_ocp_data("phases_info", phases_info)
    data = read_generic_ocp_data()
    return data["phases_info"][phase_index]["constraints"][constraint_index]


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/nodes",
    response_model=NodesResponse,
)
def put_constraint_nodes(phase_index: int, constraint_index: int, nodes: NodesRequest):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["constraints"][constraint_index][
        "nodes"
    ] = nodes.nodes.value
    update_generic_ocp_data("phases_info", phases_info)
    return NodesResponse(nodes=nodes.nodes)


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/quadratic",
    response_model=QuadraticResponse,
)
def put_constraint_quadratic(
    phase_index: int, constraint_index: int, quadratic: QuadraticRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["constraints"][constraint_index][
        "quadratic"
    ] = quadratic.quadratic
    update_generic_ocp_data("phases_info", phases_info)
    return QuadraticResponse(quadratic=quadratic.quadratic)


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/expand",
    response_model=ExpandResponse,
)
def put_constraint_expand(
    phase_index: int, constraint_index: int, expand: ExpandRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["constraints"][constraint_index]["expand"] = expand.expand
    update_generic_ocp_data("phases_info", phases_info)
    return ExpandResponse(expand=expand.expand)


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/target",
    response_model=TargetResponse,
)
def put_constraint_target(
    phase_index: int, constraint_index: int, target: TargetRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["constraints"][constraint_index]["target"] = target.target
    update_generic_ocp_data("phases_info", phases_info)
    return TargetResponse(target=target.target)


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/derivative",
    response_model=DerivativeResponse,
)
def put_constraint_derivative(
    phase_index: int, constraint_index: int, derivative: DerivativeRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["constraints"][constraint_index][
        "derivative"
    ] = derivative.derivative
    update_generic_ocp_data("phases_info", phases_info)
    return DerivativeResponse(derivative=derivative.derivative)


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/integration_rule",
    response_model=IntegrationRuleResponse,
)
def put_constraint_integration_rule(
    phase_index: int,
    constraint_index: int,
    integration_rule: IntegrationRuleRequest,
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["constraints"][constraint_index][
        "integration_rule"
    ] = integration_rule.integration_rule.value
    update_generic_ocp_data("phases_info", phases_info)
    return IntegrationRuleResponse(integration_rule=integration_rule.integration_rule)


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/multi_thread",
    response_model=MultiThreadResponse,
)
def put_constraint_multi_thread(
    phase_index: int, constraint_index: int, multi_thread: MultiThreadRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    phases_info[phase_index]["constraints"][constraint_index][
        "multi_thread"
    ] = multi_thread.multi_thread
    update_generic_ocp_data("phases_info", phases_info)
    return MultiThreadResponse(multi_thread=multi_thread.multi_thread)


@router.get(
    "/phases_info/{phase_index}/constraints/{constraint_index}/arguments/{key}",
    response_model=ArgumentResponse,
)
def get_constraint_arguments(phase_index: int, constraint_index: int, key: str):
    phases_info = read_generic_ocp_data("phases_info")
    arguments = phases_info[phase_index]["constraints"][constraint_index]["arguments"]

    for argument in arguments:
        if argument["name"] == key:
            return ArgumentResponse(
                key=key, type=argument["type"], value=argument["value"]
            )

    raise HTTPException(
        status_code=404,
        detail=f"{key} not found in arguments of constraint {constraint_index}",
    )


@router.put(
    "/phases_info/{phase_index}/constraints/{constraint_index}/arguments/{key}",
    response_model=ArgumentResponse,
)
def put_constraint_arguments(
    phase_index: int,
    constraint_index: int,
    key: str,
    argument_req: ArgumentRequest,
):
    phases_info = read_generic_ocp_data("phases_info")
    arguments = phases_info[phase_index]["constraints"][constraint_index]["arguments"]

    for argument in arguments:
        if argument["name"] == key:
            argument["type"] = argument_req.type
            argument["value"] = argument_req.value

            phases_info[phase_index]["constraints"][constraint_index][
                "arguments"
            ] = arguments
            update_generic_ocp_data("phases_info", phases_info)

            return ArgumentResponse(
                key=key, type=argument["type"], value=argument["value"]
            )
    raise HTTPException(
        status_code=404,
        detail=f"{key} not found in arguments of constraint {constraint_index}",
    )
