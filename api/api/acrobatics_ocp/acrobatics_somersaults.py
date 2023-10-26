import inspect
import json

import bioptim
from bioptim import ObjectiveFcn
from fastapi import APIRouter, HTTPException

from acrobatics_ocp.acrobatics_responses import *

router = APIRouter()

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

min_to_original_dict = {
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

max_to_original_dict = {
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


# somersaults info endpoints


@router.get("/", response_model=list)
def get_somersaults_info():
    somersaults_info = read_acrobatics_data("somersaults_info")
    return somersaults_info


@router.get("/{somersault_index}", response_model=dict)
def get_somersaults_info(somersault_index: int):
    n_somersaults = read_acrobatics_data("nb_somersaults")
    if somersault_index < 0 or somersault_index >= n_somersaults:
        raise HTTPException(
            status_code=404,
            detail=f"somersault_index must be between 0 and {n_somersaults - 1}",
        )
    somersaults_info = read_acrobatics_data("somersaults_info")
    return somersaults_info[somersault_index]


@router.put(
    "/{somersault_index}/nb_shooting_points",
    response_model=NbShootingPointsResponse,
)
def put_nb_shooting_points(
    somersault_index: int, nb_shooting_points: NbShootingPointsRequest
):
    if nb_shooting_points.nb_shooting_points <= 0:
        raise HTTPException(
            status_code=400, detail="nb_shooting_points must be positive"
        )
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index][
        "nb_shooting_points"
    ] = nb_shooting_points.nb_shooting_points
    update_acrobatics_data("somersaults_info", somersaults_info)
    return NbShootingPointsResponse(
        nb_shooting_points=nb_shooting_points.nb_shooting_points
    )


@router.put(
    "/{somersault_index}/duration",
    response_model=SomersaultDurationResponse,
)
def put_duration(somersault_index: int, duration: SomersaultDurationRequest):
    if duration.duration <= 0:
        raise HTTPException(status_code=400, detail="duration must be positive")
    infos = read_acrobatics_data()
    somersaults_info = infos["somersaults_info"]
    somersaults_info[somersault_index]["duration"] = duration.duration
    infos["final_time"] = sum(somersault["duration"] for somersault in somersaults_info)
    update_acrobatics_data("somersaults_info", somersaults_info)
    update_acrobatics_data("final_time", infos["final_time"])
    return SomersaultDurationResponse(duration=duration.duration)


@router.put(
    "/{somersault_index}/nb_half_twists",
    response_model=NbHalfTwistsResponse,
)
def put_nb_half_twist(somersault_index: int, nb_half_twists: NbHalfTwistsRequest):
    if nb_half_twists.nb_half_twists < 0:
        raise HTTPException(
            status_code=400, detail="nb_half_twists must be positive or zero"
        )
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["nb_half_twists"] = nb_half_twists.nb_half_twists
    update_acrobatics_data("somersaults_info", somersaults_info)
    return NbHalfTwistsResponse(nb_half_twists=nb_half_twists.nb_half_twists)


# objectives endpoints


@router.get("/{somersault_index}/objectives", response_model=list)
def get_objectives(somersault_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    objectives = somersaults_info[somersault_index]["objectives"]
    return objectives


@router.post("/{somersault_index}/objectives", response_model=list)
def add_objective(somersault_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    objectives = somersaults_info[somersault_index]["objectives"]
    objectives.append(default_objective)
    somersaults_info[somersault_index]["objectives"] = objectives
    update_acrobatics_data("somersaults_info", somersaults_info)
    return objectives


@router.get(
    "/{somersault_index}/objectives/{objective_index}",
    response_model=list,
)
def get_objective_dropdown_list(somersault_index: int, objective_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    objective = somersaults_info[somersault_index]["objectives"][objective_index]
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
    # return list(min_to_original_dict.keys()) if weight > 0 else list(max_to_original_dict.keys())
    # return [e.name for e in enum]


@router.delete(
    "/{somersault_index}/objectives/{objective_index}",
    response_model=list,
)
def delete_objective(somersault_index: int, objective_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    objectives = somersaults_info[somersault_index]["objectives"]
    objectives.pop(objective_index)
    somersaults_info[somersault_index]["objectives"] = objectives
    update_acrobatics_data("somersaults_info", somersaults_info)
    return objectives


@router.put(
    "/{somersault_index}/objectives/{objective_index}/objective_type",
    response_model=dict,
)
def put_objective_type(
    somersault_index: int, objective_index: int, objective_type: ObjectiveTypeRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "objective_type"
    ] = objective_type.objective_type.value

    objective_type_value = objective_type.objective_type.value
    penalty_type = somersaults_info[somersault_index]["objectives"][objective_index][
        "penalty_type"
    ]
    arguments = obj_arguments(objective_type_value, penalty_type)

    somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ] = arguments

    update_acrobatics_data("somersaults_info", somersaults_info)
    data = read_acrobatics_data()
    return data["somersaults_info"][somersault_index]["objectives"][objective_index]


# common arguments


@router.put(
    "/{somersault_index}/objectives/{objective_index}/penalty_type",
    response_model=dict,
)
def put_objective_penalty_type(
    somersault_index: int, objective_index: int, penalty_type: ObjectiveFcnRequest
):
    penalty_type_value = penalty_type.penalty_type
    somersaults_info = read_acrobatics_data("somersaults_info")

    somersaults_info[somersault_index]["objectives"][objective_index][
        "penalty_type"
    ] = penalty_type_value

    objective_type = somersaults_info[somersault_index]["objectives"][objective_index][
        "objective_type"
    ]
    arguments = obj_arguments(
        objective_type=objective_type, penalty_type=penalty_type_value
    )

    somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ] = arguments

    update_acrobatics_data("somersaults_info", somersaults_info)

    data = read_acrobatics_data()
    return data["somersaults_info"][somersault_index]["objectives"][objective_index]


@router.put(
    "/{somersault_index}/objectives/{objective_index}/nodes",
    response_model=NodesResponse,
)
def put_objective_nodes(
    somersault_index: int, objective_index: int, nodes: NodesRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "nodes"
    ] = nodes.nodes.value
    update_acrobatics_data("somersaults_info", somersaults_info)
    return NodesResponse(nodes=nodes.nodes)


@router.put(
    "/{somersault_index}/objectives/{objective_index}/quadratic",
    response_model=QuadraticResponse,
)
def put_objective_quadratic(
    somersault_index: int, objective_index: int, quadratic: QuadraticRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "quadratic"
    ] = quadratic.quadratic
    update_acrobatics_data("somersaults_info", somersaults_info)
    return QuadraticResponse(quadratic=quadratic.quadratic)


@router.put(
    "/{somersault_index}/objectives/{objective_index}/expand",
    response_model=ExpandResponse,
)
def put_objective_expand(
    somersault_index: int, objective_index: int, expand: ExpandRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "expand"
    ] = expand.expand
    update_acrobatics_data("somersaults_info", somersaults_info)
    return ExpandResponse(expand=expand.expand)


@router.put(
    "/{somersault_index}/objectives/{objective_index}/target",
    response_model=TargetResponse,
)
def put_objective_target(
    somersault_index: int, objective_index: int, target: TargetRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "target"
    ] = target.target
    update_acrobatics_data("somersaults_info", somersaults_info)
    return TargetResponse(target=target.target)


@router.put(
    "/{somersault_index}/objectives/{objective_index}/derivative",
    response_model=DerivativeResponse,
)
def put_objective_derivative(
    somersault_index: int, objective_index: int, derivative: DerivativeRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "derivative"
    ] = derivative.derivative
    update_acrobatics_data("somersaults_info", somersaults_info)
    return DerivativeResponse(derivative=derivative.derivative)


@router.put(
    "/{somersault_index}/objectives/{objective_index}/integration_rule",
    response_model=IntegrationRuleResponse,
)
def put_objective_integration_rule(
    somersault_index: int,
    objective_index: int,
    integration_rule: IntegrationRuleRequest,
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "integration_rule"
    ] = integration_rule.integration_rule.value
    update_acrobatics_data("somersaults_info", somersaults_info)
    return IntegrationRuleResponse(integration_rule=integration_rule.integration_rule)


@router.put(
    "/{somersault_index}/objectives/{objective_index}/multi_thread",
    response_model=MultiThreadResponse,
)
def put_objective_multi_thread(
    somersault_index: int, objective_index: int, multi_thread: MultiThreadRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "multi_thread"
    ] = multi_thread.multi_thread
    update_acrobatics_data("somersaults_info", somersaults_info)
    return MultiThreadResponse(multi_thread=multi_thread.multi_thread)


@router.put(
    "/{somersault_index}/objectives/{objective_index}/weight",
    response_model=WeightResponse,
)
def put_objective_weight(
    somersault_index: int, objective_index: int, weight: WeightRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "weight"
    ] = weight.weight
    update_acrobatics_data("somersaults_info", somersaults_info)
    return WeightResponse(weight=weight.weight)


@router.put(
    "/{somersault_index}/objectives/{objective_index}/weight/maximize",
    response_model=dict,
)
def put_objective_weight_maximize(somersault_index: int, objective_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    old_weight = somersaults_info[somersault_index]["objectives"][objective_index][
        "weight"
    ]
    new_weight = -abs(old_weight)

    somersaults_info[somersault_index]["objectives"][objective_index][
        "weight"
    ] = new_weight
    update_acrobatics_data("somersaults_info", somersaults_info)
    return somersaults_info[somersault_index]["objectives"][objective_index]


@router.put(
    "/{somersault_index}/objectives/{objective_index}/weight/minimize",
    response_model=dict,
)
def put_objective_weight_minimize(somersault_index: int, objective_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    old_weight = somersaults_info[somersault_index]["objectives"][objective_index][
        "weight"
    ]
    new_weight = abs(old_weight)

    somersaults_info[somersault_index]["objectives"][objective_index][
        "weight"
    ] = new_weight
    update_acrobatics_data("somersaults_info", somersaults_info)
    return somersaults_info[somersault_index]["objectives"][objective_index]


@router.get(
    "/{somersault_index}/objectives/{objective_index}/arguments/{key}",
    response_model=ArgumentResponse,
)
def get_objective_arguments(somersault_index: int, objective_index: int, key: str):
    somersaults_info = read_acrobatics_data("somersaults_info")
    arguments = somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ]

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
    "/{somersault_index}/objectives/{objective_index}/arguments/{key}",
    response_model=ArgumentResponse,
)
def put_objective_arguments(
    somersault_index: int, objective_index: int, key: str, argument_req: ArgumentRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")

    arguments = somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ]

    for argument in arguments:
        if argument["name"] == key:
            argument["type"] = argument_req.type
            argument["value"] = argument_req.value

            somersaults_info[somersault_index]["objectives"][objective_index][
                "arguments"
            ] = arguments
            update_acrobatics_data("somersaults_info", somersaults_info)

            return ArgumentResponse(
                key=key, type=argument["type"], value=argument["value"]
            )
    raise HTTPException(
        status_code=404,
        detail=f"{key} not found in arguments of objective {objective_index}",
    )


# constraints endpoints


@router.get("/{somersault_index}/constraints", response_model=list)
def get_constraints(somersault_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    constraints = somersaults_info[somersault_index]["constraints"]
    return constraints


@router.post("/{somersault_index}/constraints", response_model=list)
def add_constraint(somersault_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    constraints = somersaults_info[somersault_index]["constraints"]
    constraints.append(default_constraint)
    somersaults_info[somersault_index]["constraints"] = constraints
    update_acrobatics_data("somersaults_info", somersaults_info)
    return constraints


@router.get(
    "/{somersault_index}/constraints/{constraint_index}",
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
    "/{somersault_index}/constraints/{constraint_index}",
    response_model=list,
)
def delete_constraint(somersault_index: int, constraint_index: int):
    somersaults_info = read_acrobatics_data("somersaults_info")
    constraints = somersaults_info[somersault_index]["constraints"]
    constraints.pop(constraint_index)
    somersaults_info[somersault_index]["constraints"] = constraints
    update_acrobatics_data("somersaults_info", somersaults_info)
    return constraints


# common arguments


@router.put(
    "/{somersault_index}/constraints/{constraint_index}/penalty_type",
    response_model=dict,
)
def put_constraint_penalty_type(
    somersault_index: int, constraint_index: int, penalty_type: ConstraintFcnRequest
):
    penalty_type_value = penalty_type.penalty_type
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "penalty_type"
    ] = penalty_type_value

    arguments = constraint_arguments(penalty_type.penalty_type)
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "arguments"
    ] = arguments

    update_acrobatics_data("somersaults_info", somersaults_info)
    data = read_acrobatics_data()
    return data["somersaults_info"][somersault_index]["constraints"][constraint_index]


@router.put(
    "/{somersault_index}/constraints/{constraint_index}/nodes",
    response_model=NodesResponse,
)
def put_constraint_nodes(
    somersault_index: int, constraint_index: int, nodes: NodesRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "nodes"
    ] = nodes.nodes.value
    update_acrobatics_data("somersaults_info", somersaults_info)
    return NodesResponse(nodes=nodes.nodes)


@router.put(
    "/{somersault_index}/constraints/{constraint_index}/quadratic",
    response_model=QuadraticResponse,
)
def put_constraint_quadratic(
    somersault_index: int, constraint_index: int, quadratic: QuadraticRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "quadratic"
    ] = quadratic.quadratic
    update_acrobatics_data("somersaults_info", somersaults_info)
    return QuadraticResponse(quadratic=quadratic.quadratic)


@router.put(
    "/{somersault_index}/constraints/{constraint_index}/expand",
    response_model=ExpandResponse,
)
def put_constraint_expand(
    somersault_index: int, constraint_index: int, expand: ExpandRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "expand"
    ] = expand.expand
    update_acrobatics_data("somersaults_info", somersaults_info)
    return ExpandResponse(expand=expand.expand)


@router.put(
    "/{somersault_index}/constraints/{constraint_index}/target",
    response_model=TargetResponse,
)
def put_constraint_target(
    somersault_index: int, constraint_index: int, target: TargetRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "target"
    ] = target.target
    update_acrobatics_data("somersaults_info", somersaults_info)
    return TargetResponse(target=target.target)


@router.put(
    "/{somersault_index}/constraints/{constraint_index}/derivative",
    response_model=DerivativeResponse,
)
def put_constraint_derivative(
    somersault_index: int, constraint_index: int, derivative: DerivativeRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "derivative"
    ] = derivative.derivative
    update_acrobatics_data("somersaults_info", somersaults_info)
    return DerivativeResponse(derivative=derivative.derivative)


@router.put(
    "/{somersault_index}/constraints/{constraint_index}/integration_rule",
    response_model=IntegrationRuleResponse,
)
def put_constraint_integration_rule(
    somersault_index: int,
    constraint_index: int,
    integration_rule: IntegrationRuleRequest,
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "integration_rule"
    ] = integration_rule.integration_rule.value
    update_acrobatics_data("somersaults_info", somersaults_info)
    return IntegrationRuleResponse(integration_rule=integration_rule.integration_rule)


@router.put(
    "/{somersault_index}/constraints/{constraint_index}/multi_thread",
    response_model=MultiThreadResponse,
)
def put_constraint_multi_thread(
    somersault_index: int, constraint_index: int, multi_thread: MultiThreadRequest
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "multi_thread"
    ] = multi_thread.multi_thread
    update_acrobatics_data("somersaults_info", somersaults_info)
    return MultiThreadResponse(multi_thread=multi_thread.multi_thread)


@router.get(
    "/{somersault_index}/constraints/{constraint_index}/arguments/{key}",
    response_model=ArgumentResponse,
)
def get_constraint_arguments(somersault_index: int, constraint_index: int, key: str):
    somersaults_info = read_acrobatics_data("somersaults_info")
    arguments = somersaults_info[somersault_index]["constraints"][constraint_index][
        "arguments"
    ]

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
    "/{somersault_index}/constraints/{constraint_index}/arguments/{key}",
    response_model=ArgumentResponse,
)
def put_constraint_arguments(
    somersault_index: int,
    constraint_index: int,
    key: str,
    argument_req: ArgumentRequest,
):
    somersaults_info = read_acrobatics_data("somersaults_info")
    arguments = somersaults_info[somersault_index]["constraints"][constraint_index][
        "arguments"
    ]

    for argument in arguments:
        if argument["name"] == key:
            argument["type"] = argument_req.type
            argument["value"] = argument_req.value

            somersaults_info[somersault_index]["constraints"][constraint_index][
                "arguments"
            ] = arguments
            update_acrobatics_data("somersaults_info", somersaults_info)

            return ArgumentResponse(
                key=key, type=argument["type"], value=argument["value"]
            )
    raise HTTPException(
        status_code=404,
        detail=f"{key} not found in arguments of constraint {constraint_index}",
    )
