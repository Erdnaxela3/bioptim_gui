from bioptim import ObjectiveFcn
from fastapi import APIRouter, HTTPException

from acrobatics_ocp.acrobatics_responses import *
from acrobatics_ocp.acrobatics_utils import (
    read_acrobatics_data,
    update_acrobatics_data,
)
import penalty.penalty_config as penalty_config

from penalty.penalty_utils import obj_arguments, constraint_arguments

router = APIRouter()

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
    objectives.append(penalty_config.DefaultPenaltyConfig.default_objective)
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
    constraints.append(penalty_config.DefaultPenaltyConfig.default_constraint)
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
