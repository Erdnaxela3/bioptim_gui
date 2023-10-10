import inspect
import json

import bioptim
from bioptim import ObjectiveFcn
from fastapi import APIRouter, HTTPException

from acrobatics_ocp.acrobatics_responses import *

router = APIRouter(
    prefix="/acrobatics",
    tags=["acrobatics"],
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
    "arguments": {},
}

default_somersaults_info = {
    "nb_shooting_points": 24,
    "nb_half_twists": 0,
    "duration": 1,
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
            "arguments": {
                "key": {"value": "tau", "type": "string"},
            },
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
            "arguments": {
                "min_bound": {"value": 0.9, "type": "float"},
                "max_bound": {"value": 1.1, "type": "float"},
            },
        },
    ],
    "constraints": [],
}


def get_objective_arguments(objective_type: str, penalty_type: str) -> dict:
    if objective_type == "mayer":
        penalty_fcn = getattr(ObjectiveFcn.Mayer, penalty_type)
    elif objective_type == "lagrange":
        penalty_fcn = getattr(ObjectiveFcn.Lagrange, penalty_type)
    else:
        raise HTTPException(404, f"{objective_type} not found")

    penalty_fcn = penalty_fcn.value[0]

    # arguments
    arg_specs = inspect.getfullargspec(penalty_fcn)
    defaults = arg_specs.defaults
    arguments = arg_specs.annotations

    formatted_arguments = {
        k: {"value": None, "type": str(v)} for k, v in arguments.items()
    }

    if defaults:
        l_defaults = len(defaults)
        for i in range(l_defaults):
            formatted_arguments[arg_specs.args[-l_defaults + i]]["value"] = defaults[i]

    for key_to_delete in ["_", "penalty", "controller"]:
        if key_to_delete in formatted_arguments:
            del formatted_arguments[key_to_delete]

    return formatted_arguments


def get_constraint_arguments(penalty_type: str) -> dict:
    try:
        penalty_fcn = getattr(bioptim.ConstraintFcn, penalty_type)
    except AttributeError:
        raise HTTPException(404, f"{penalty_type} not found")

    penalty_fcn = penalty_fcn.value[0]

    # arguments
    arg_specs = inspect.getfullargspec(penalty_fcn)
    defaults = arg_specs.defaults
    arguments = arg_specs.annotations

    formatted_arguments = {
        k: {"value": None, "type": str(v)} for k, v in arguments.items()
    }

    if defaults:
        l_defaults = len(defaults)
        for i in range(l_defaults):
            formatted_arguments[arg_specs.args[-l_defaults + i]]["value"] = defaults[i]

    for key_to_delete in ["_", "penalty", "controller"]:
        if key_to_delete in formatted_arguments:
            del formatted_arguments[key_to_delete]

    return formatted_arguments


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


@router.get("/")
def get_acrobatics_data() -> dict:
    data = read_acrobatics_data()
    return data


@router.put("/nb_somersaults")
def update_nb_somersaults(
    nb_somersaults: NbSomersaultsRequest,
) -> NbSomersaultsResponse:
    old_value = read_acrobatics_data("nb_somersaults")
    new_value = nb_somersaults.nb_somersaults
    if new_value < 0:
        raise HTTPException(status_code=400, detail="nb_somersaults must be positive")

    if new_value > old_value:
        add_somersault_info(new_value - old_value)
    elif new_value < old_value:
        remove_somersault_info(old_value - new_value)

    update_acrobatics_data("nb_somersaults", new_value)
    return NbSomersaultsResponse(nb_somersaults=new_value)


@router.put("/model_path")
def put_model_path(model_path: ModelPathRequest) -> ModelPathResponse:
    update_acrobatics_data("model_path", model_path.model_path)
    return ModelPathResponse(model_path=model_path.model_path)


@router.put("/final_time")
def put_final_time(final_time: FinalTimeRequest) -> FinalTimeResponse:
    new_value = final_time.final_time
    if new_value < 0:
        raise HTTPException(status_code=400, detail="final_time must be positive")
    update_acrobatics_data("final_time", new_value)
    return FinalTimeResponse(final_time=new_value)


@router.put("/final_time_margin")
def put_final_time_margin(
    final_time_margin: FinalTimeMarginRequest,
) -> FinalTimeMarginResponse:
    new_value = final_time_margin.final_time_margin
    if new_value < 0:
        raise HTTPException(
            status_code=400, detail="final_time_margin must be positive"
        )
    update_acrobatics_data("final_time_margin", new_value)
    return FinalTimeMarginResponse(final_time_margin=new_value)


@router.put("/position")
def put_position(position: PositionRequest) -> PositionResponse:
    new_value = position.position.value
    update_acrobatics_data("position", new_value)
    return PositionResponse(position=new_value)


@router.put("/sport_type")
def put_sport_type(sport_type: SportTypeRequest) -> SportTypeResponse:
    new_value = sport_type.sport_type.value
    update_acrobatics_data("sport_type", new_value)
    return SportTypeResponse(sport_type=new_value)


@router.put("/preferred_twist_side")
def put_preferred_twist_side(
    preferred_twist_side: PreferredTwistSideRequest,
) -> PreferredTwistSideResponse:
    new_value = preferred_twist_side.preferred_twist_side.value

    update_acrobatics_data("preferred_twist_side", new_value)
    return PreferredTwistSideResponse(preferred_twist_side=new_value)


# somersaults info endpoints


@router.get("/somersaults_info/")
def get_somersaults_info() -> list:
    somersaults_info = read_acrobatics_data("somersaults_info")
    return somersaults_info


@router.get("/somersaults_info/{somersault_index}")
def get_somersaults_info(somersault_index: int) -> dict:
    n_somersaults = read_acrobatics_data("nb_somersaults")
    if somersault_index < 0 or somersault_index >= n_somersaults:
        raise HTTPException(
            status_code=404,
            detail=f"somersault_index must be between 0 and {n_somersaults - 1}",
        )
    somersaults_info = read_acrobatics_data("somersaults_info")
    return somersaults_info[somersault_index]


@router.put("/somersaults_info/{somersault_index}/shooting_points")
def put_nb_shooting_points(
    somersault_index: int, nb_shooting_points: NbShootingPointsRequest
) -> NbShootingPointsResponse:
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


@router.put("/somersaults_info/{somersault_index}/duration")
def put_duration(
    somersault_index: int, duration: SomersaultDurationRequest
) -> SomersaultDurationResponse:
    if duration.duration <= 0:
        raise HTTPException(status_code=400, detail="duration must be positive")
    infos = read_acrobatics_data()
    somersaults_info = infos["somersaults_info"]
    somersaults_info[somersault_index]["duration"] = duration.duration
    infos["final_time"] = sum(somersault["duration"] for somersault in somersaults_info)
    update_acrobatics_data("somersaults_info", somersaults_info)
    update_acrobatics_data("final_time", infos["final_time"])
    return SomersaultDurationResponse(duration=duration.duration)


@router.put("/somersaults_info/{somersault_index}/nb_half_twists")
def put_nb_half_twist(
    somersault_index: int, nb_half_twists: NbHalfTwistsRequest
) -> NbHalfTwistsResponse:
    if nb_half_twists.nb_half_twists < 0:
        raise HTTPException(
            status_code=400, detail="nb_half_twists must be positive or zero"
        )
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["nb_half_twists"] = nb_half_twists.nb_half_twists
    update_acrobatics_data("somersaults_info", somersaults_info)
    return NbHalfTwistsResponse(nb_half_twists=nb_half_twists.nb_half_twists)


# objectives endpoints


@router.get("/somersaults_info/{somersault_index}/objectives")
def get_objectives(somersault_index: int) -> list:
    somersaults_info = read_acrobatics_data("somersaults_info")
    objectives = somersaults_info[somersault_index]["objectives"]
    return objectives


@router.post("/somersaults_info/{somersault_index}/objectives")
def add_objective(somersault_index: int) -> list:
    somersaults_info = read_acrobatics_data("somersaults_info")
    objectives = somersaults_info[somersault_index]["objectives"]
    objectives.append(default_objective)
    somersaults_info[somersault_index]["objectives"] = objectives
    update_acrobatics_data("somersaults_info", somersaults_info)
    return objectives


@router.delete("/somersaults_info/{somersault_index}/objectives/{objective_index}")
def delete_objective(somersault_index: int, objective_index: int) -> list:
    somersaults_info = read_acrobatics_data("somersaults_info")
    objectives = somersaults_info[somersault_index]["objectives"]
    objectives.pop(objective_index)
    somersaults_info[somersault_index]["objectives"] = objectives
    update_acrobatics_data("somersaults_info", somersaults_info)
    return objectives


@router.put(
    "/somersaults_info/{somersault_index}/objectives/{objective_index}/objective_type"
)
def put_objective_type(
    somersault_index: int, objective_index: int, objective_type: ObjectiveTypeRequest
) -> ObjectiveTypeResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "objective_type"
    ] = objective_type.objective_type.value

    objective_type_value = objective_type.objective_type.value
    penalty_type = somersaults_info[somersault_index]["objectives"][objective_index][
        "penalty_type"
    ]
    arguments = get_objective_arguments(objective_type_value, penalty_type)

    somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ] = arguments

    update_acrobatics_data("somersaults_info", somersaults_info)
    return ObjectiveTypeResponse(objective_type=objective_type.objective_type)


# common arguments


@router.put(
    "/somersaults_info/{somersault_index}/objectives/{objective_index}/penalty_type"
)
def put_penalty_type(
    somersault_index: int, objective_index: int, penalty_type: ObjectiveFcnRequest
) -> PenaltyTypeResponse:
    penalty_type_value = penalty_type.penalty_type.value
    somersaults_info = read_acrobatics_data("somersaults_info")

    somersaults_info[somersault_index]["objectives"][objective_index][
        "penalty_type"
    ] = penalty_type_value

    arguments = get_objective_arguments(
        objective_type="lagrange", penalty_type=penalty_type_value
    )

    somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ] = arguments

    update_acrobatics_data("somersaults_info", somersaults_info)
    return PenaltyTypeResponse(penalty_type=penalty_type.penalty_type)


@router.put("/somersaults_info/{somersault_index}/objectives/{objective_index}/nodes")
def put_nodes(
    somersault_index: int, objective_index: int, nodes: NodesRequest
) -> NodesResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "nodes"
    ] = nodes.nodes.value
    update_acrobatics_data("somersaults_info", somersaults_info)
    return NodesResponse(nodes=nodes.nodes)


@router.put(
    "/somersaults_info/{somersault_index}/objectives/{objective_index}/quadratic"
)
def put_quadratic(
    somersault_index: int, objective_index: int, quadratic: QuadraticRequest
) -> QuadraticResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "quadratic"
    ] = quadratic.quadratic
    update_acrobatics_data("somersaults_info", somersaults_info)
    return QuadraticResponse(quadratic=quadratic.quadratic)


@router.put("/somersaults_info/{somersault_index}/objectives/{objective_index}/expand")
def put_expand(
    somersault_index: int, objective_index: int, expand: ExpandRequest
) -> ExpandResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "expand"
    ] = expand.expand
    update_acrobatics_data("somersaults_info", somersaults_info)
    return ExpandResponse(expand=expand.expand)


@router.put("/somersaults_info/{somersault_index}/objectives/{objective_index}/target")
def put_target(
    somersault_index: int, objective_index: int, target: TargetRequest
) -> TargetResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "target"
    ] = target.target
    update_acrobatics_data("somersaults_info", somersaults_info)
    return TargetResponse(target=target.target)


@router.put(
    "/somersaults_info/{somersault_index}/objectives/{objective_index}/derivative"
)
def put_derivative(
    somersault_index: int, objective_index: int, derivative: DerivativeRequest
) -> DerivativeResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "derivative"
    ] = derivative.derivative
    update_acrobatics_data("somersaults_info", somersaults_info)
    return DerivativeResponse(derivative=derivative.derivative)


@router.put(
    "/somersaults_info/{somersault_index}/objectives/{objective_index}/integration_rule"
)
def put_integration_rule(
    somersault_index: int,
    objective_index: int,
    integration_rule: IntegrationRuleRequest,
) -> IntegrationRuleResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "integration_rule"
    ] = integration_rule.integration_rule.value
    update_acrobatics_data("somersaults_info", somersaults_info)
    return IntegrationRuleResponse(integration_rule=integration_rule.integration_rule)


@router.put(
    "/somersaults_info/{somersault_index}/objectives/{objective_index}/multi_thread"
)
def put_multi_thread(
    somersault_index: int, objective_index: int, multi_thread: MultiThreadRequest
) -> MultiThreadResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "multi_thread"
    ] = multi_thread.multi_thread
    update_acrobatics_data("somersaults_info", somersaults_info)
    return MultiThreadResponse(multi_thread=multi_thread.multi_thread)


@router.put("/somersaults_info/{somersault_index}/objectives/{objective_index}/weight")
def put_weight(
    somersault_index: int, objective_index: int, weight: WeightRequest
) -> WeightResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["objectives"][objective_index][
        "weight"
    ] = weight.weight
    update_acrobatics_data("somersaults_info", somersaults_info)
    return WeightResponse(weight=weight.weight)


@router.get(
    "/somersaults_info/{somersault_index}/objectives/{objective_index}/arguments"
)
def get_arguments(
    somersault_index: int, objective_index: int, argument_req: ArgumentRequest
) -> ArgumentResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    arguments = somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ]
    key = argument_req.key
    return ArgumentResponse(
        key=key, type=arguments[key]["type"], value=arguments[key]["value"]
    )


@router.put(
    "/somersaults_info/{somersault_index}/objectives/{objective_index}/arguments"
)
def put_arguments(
    somersault_index: int, objective_index: int, argument_req: ArgumentRequest
) -> ArgumentResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    arguments = somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ]
    key = argument_req.key
    arguments[key]["type"] = argument_req.type
    arguments[key]["value"] = argument_req.value
    somersaults_info[somersault_index]["objectives"][objective_index][
        "arguments"
    ] = arguments
    update_acrobatics_data("somersaults_info", somersaults_info)
    return ArgumentResponse(
        key=key, type=arguments[key]["type"], value=arguments[key]["value"]
    )


# constraints endpoints


@router.get("/somersaults_info/{somersault_index}/constraints")
def get_constraints(somersault_index: int) -> list:
    somersaults_info = read_acrobatics_data("somersaults_info")
    constraints = somersaults_info[somersault_index]["constraints"]
    return constraints


@router.post("/somersaults_info/{somersault_index}/constraints")
def add_constraint(somersault_index: int) -> list:
    somersaults_info = read_acrobatics_data("somersaults_info")
    constraints = somersaults_info[somersault_index]["constraints"]
    constraints.append(default_constraint)
    somersaults_info[somersault_index]["constraints"] = constraints
    update_acrobatics_data("somersaults_info", somersaults_info)
    return constraints


@router.delete("/somersaults_info/{somersault_index}/constraints/{constraint_index}")
def delete_constraint(somersault_index: int, constraint_index: int) -> list:
    somersaults_info = read_acrobatics_data("somersaults_info")
    constraints = somersaults_info[somersault_index]["constraints"]
    constraints.pop(constraint_index)
    somersaults_info[somersault_index]["constraints"] = constraints
    update_acrobatics_data("somersaults_info", somersaults_info)
    return constraints


# common arguments


@router.put(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/penalty_type"
)
def put_penalty_type(
    somersault_index: int, constraint_index: int, penalty_type: ConstraintFcnRequest
) -> PenaltyTypeResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "penalty_type"
    ] = penalty_type.penalty_type

    arguments = get_constraint_arguments(penalty_type.penalty_type)
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "arguments"
    ] = arguments

    update_acrobatics_data("somersaults_info", somersaults_info)
    return PenaltyTypeResponse(penalty_type=penalty_type.penalty_type)


@router.put("/somersaults_info/{somersault_index}/constraints/{constraint_index}/nodes")
def put_nodes(
    somersault_index: int, constraint_index: int, nodes: NodesRequest
) -> NodesResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "nodes"
    ] = nodes.nodes.value
    update_acrobatics_data("somersaults_info", somersaults_info)
    return NodesResponse(nodes=nodes.nodes)


@router.put(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/quadratic"
)
def put_quadratic(
    somersault_index: int, constraint_index: int, quadratic: QuadraticRequest
) -> QuadraticResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "quadratic"
    ] = quadratic.quadratic
    update_acrobatics_data("somersaults_info", somersaults_info)
    return QuadraticResponse(quadratic=quadratic.quadratic)


@router.put(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/expand"
)
def put_expand(
    somersault_index: int, constraint_index: int, expand: ExpandRequest
) -> ExpandResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "expand"
    ] = expand.expand
    update_acrobatics_data("somersaults_info", somersaults_info)
    return ExpandResponse(expand=expand.expand)


@router.put(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/target"
)
def put_target(
    somersault_index: int, constraint_index: int, target: TargetRequest
) -> TargetResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "target"
    ] = target.target
    update_acrobatics_data("somersaults_info", somersaults_info)
    return TargetResponse(target=target.target)


@router.put(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/derivative"
)
def put_derivative(
    somersault_index: int, constraint_index: int, derivative: DerivativeRequest
) -> DerivativeResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "derivative"
    ] = derivative.derivative
    update_acrobatics_data("somersaults_info", somersaults_info)
    return DerivativeResponse(derivative=derivative.derivative)


@router.put(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/integration_rule"
)
def put_integration_rule(
    somersault_index: int,
    constraint_index: int,
    integration_rule: IntegrationRuleRequest,
) -> IntegrationRuleResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "integration_rule"
    ] = integration_rule.integration_rule.value
    update_acrobatics_data("somersaults_info", somersaults_info)
    return IntegrationRuleResponse(integration_rule=integration_rule.integration_rule)


@router.put(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/multi_thread"
)
def put_multi_thread(
    somersault_index: int, constraint_index: int, multi_thread: MultiThreadRequest
) -> MultiThreadResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "multi_thread"
    ] = multi_thread.multi_thread
    update_acrobatics_data("somersaults_info", somersaults_info)
    return MultiThreadResponse(multi_thread=multi_thread.multi_thread)


@router.get(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/arguments"
)
def get_arguments(
    somersault_index: int, constraint_index: int, argument_req: ArgumentRequest
) -> ArgumentResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    arguments = somersaults_info[somersault_index]["constraints"][constraint_index][
        "arguments"
    ]
    key = argument_req.key
    return ArgumentResponse(
        key=key, type=arguments[key]["type"], value=arguments[key]["value"]
    )


@router.put(
    "/somersaults_info/{somersault_index}/constraints/{constraint_index}/arguments"
)
def put_arguments(
    somersault_index: int, constraint_index: int, argument_req: ArgumentRequest
) -> ArgumentResponse:
    somersaults_info = read_acrobatics_data("somersaults_info")
    arguments = somersaults_info[somersault_index]["constraints"][constraint_index][
        "arguments"
    ]
    key = argument_req.key
    arguments[key]["type"] = argument_req.type
    arguments[key]["value"] = argument_req.value
    somersaults_info[somersault_index]["constraints"][constraint_index][
        "arguments"
    ] = arguments
    update_acrobatics_data("somersaults_info", somersaults_info)
    return ArgumentResponse(
        key=key, type=arguments[key]["type"], value=arguments[key]["value"]
    )
