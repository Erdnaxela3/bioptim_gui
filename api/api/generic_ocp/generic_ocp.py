import json

import numpy as np
from bioptim import ObjectiveFcn
from fastapi import APIRouter, HTTPException

import generic_ocp.generic_ocp_code_generation as code_generation
import generic_ocp.generic_ocp_config as config
import penalty.penalty_config as penalty_config
import variables.variables_config as variables_config
from generic_ocp.generic_ocp_responses import *
from generic_ocp.generic_ocp_utils import (
    read_generic_ocp_data,
    update_generic_ocp_data,
)
from penalty.penalty_utils import obj_arguments, constraint_arguments

router = APIRouter(
    responses={404: {"description": "Not found"}},
)
router.include_router(code_generation.router)


def add_phase_info(n: int = 1) -> None:
    if n < 1:
        raise ValueError("n must be positive")

    data = read_generic_ocp_data()
    phases_info = data["phases_info"]
    before = len(phases_info)

    for i in range(before, before + n):
        phases_info.append(config.DefaultGenericOCPConfig.default_phases_info)

    data["phases_info"] = phases_info
    with open(config.DefaultGenericOCPConfig.datafile, "w") as f:
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
    with open(config.DefaultGenericOCPConfig.datafile, "w") as f:
        json.dump(data, f)


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
    objectives.append(penalty_config.DefaultPenaltyConfig.default_objective)
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
    constraints.append(penalty_config.DefaultPenaltyConfig.default_constraint)
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


@router.get("/phases_info/{phase_index}/dynamics", response_model=list)
def get_dynamics_list():
    return ["TORQUE_DRIVEN", "DUMMY"]


@router.put("/phases_info/{phase_index}/dynamics", response_model=list)
def put_dynamics_list(phase_index: int, dynamic_req: DynamicsRequest):
    phases_info = read_generic_ocp_data("phases_info")

    new_dynamic = dynamic_req.dynamics

    phases_info[phase_index]["dynamics"] = new_dynamic

    if new_dynamic == "TORQUE_DRIVEN":
        phases_info[phase_index][
            "state_variables"
        ] = variables_config.DefaultVariablesConfig.default_torque_driven_variables[
            "state_variables"
        ]
        phases_info[phase_index][
            "control_variables"
        ] = variables_config.DefaultVariablesConfig.default_torque_driven_variables[
            "control_variables"
        ]
    else:
        phases_info[phase_index][
            "state_variables"
        ] = variables_config.DefaultVariablesConfig.default_dummy_variables[
            "state_variables"
        ]
        phases_info[phase_index][
            "control_variables"
        ] = variables_config.DefaultVariablesConfig.default_dummy_variables[
            "control_variables"
        ]
    update_generic_ocp_data("phases_info", phases_info)

    return phases_info


@router.put("/phases_info/{phase_index}/state_variables/{variable_index}/dimension")
def put_state_variable_dimensions(
    phase_index: int, variable_index: int, dimension: DimensionRequest
):
    phases_info = read_generic_ocp_data("phases_info")

    new_dimension = dimension.dimension

    variable = phases_info[phase_index]["state_variables"][variable_index]

    variable["dimension"] = new_dimension

    for bound in variable["bounds"].keys():
        shape = np.array(variable["bounds"][bound]).shape
        new_value = np.zeros((new_dimension, shape[1])).tolist()
        variable["bounds"][bound] = new_value

    shape = np.array(variable["initial_guess"]).shape
    new_value = np.zeros((new_dimension, shape[1])).tolist()
    variable["initial_guess"] = new_value

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


@router.put("/phases_info/{phase_index}/control_variables/{variable_index}/dimension")
def put_control_variables_dimensions(
    phase_index: int, variable_index: int, dimension: DimensionRequest
):
    phases_info = read_generic_ocp_data("phases_info")

    new_dimension = dimension.dimension

    variable = phases_info[phase_index]["control_variables"][variable_index]

    variable["dimension"] = new_dimension

    for bound in variable["bounds"].keys():
        shape = np.array(variable["bounds"][bound]).shape
        new_value = np.zeros((new_dimension, shape[1])).tolist()
        variable["bounds"][bound] = new_value

    shape = np.array(variable["initial_guess"]).shape
    new_value = np.zeros((new_dimension, shape[1])).tolist()
    variable["initial_guess"] = new_value

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


def variables_zeros(dimension: int, interpolation_type: str) -> list:
    if interpolation_type == "LINEAR":
        return np.zeros((dimension, 2)).tolist()
    elif interpolation_type == "CONSTANT":
        return np.zeros((dimension, 1)).tolist()
    else:
        return np.zeros((dimension, 3)).tolist()


@router.put(
    "/phases_info/{phase_index}/state_variables/{variable_index}/bounds_interpolation_type"
)
def put_state_variables_bounds_interpolation_type(
    phase_index: int, variable_index: int, interpolation: InterpolationTypeRequest
):
    phases_info = read_generic_ocp_data("phases_info")

    new_interpolation = interpolation.interpolation_type

    variable = phases_info[phase_index]["state_variables"][variable_index]

    variable["bounds_interpolation_type"] = new_interpolation
    dimension = variable["dimension"]

    variable["bounds"]["min_bounds"] = variables_zeros(dimension, new_interpolation)
    variable["bounds"]["max_bounds"] = variables_zeros(dimension, new_interpolation)

    phases_info[phase_index]["state_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)

    return phases_info


@router.put(
    "/phases_info/{phase_index}/state_variables/{variable_index}/initial_guess_interpolation_type"
)
def put_state_variables_initial_guess_interpolation_type(
    phase_index: int, variable_index: int, interpolation: InterpolationTypeRequest
):
    phases_info = read_generic_ocp_data("phases_info")

    new_interpolation = interpolation.interpolation_type

    variable = phases_info[phase_index]["state_variables"][variable_index]

    variable["initial_guess_interpolation_type"] = new_interpolation
    dimension = variable["dimension"]
    variable["initial_guess"] = variables_zeros(dimension, new_interpolation)

    phases_info[phase_index]["state_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


@router.put(
    "/phases_info/{phase_index}/control_variables/{variable_index}/bounds_interpolation_type"
)
def put_control_variables_bounds_interpolation_type(
    phase_index: int, variable_index: int, interpolation: InterpolationTypeRequest
):
    phases_info = read_generic_ocp_data("phases_info")

    new_interpolation = interpolation.interpolation_type

    variable = phases_info[phase_index]["control_variables"][variable_index]

    variable["bounds_interpolation_type"] = new_interpolation
    dimension = variable["dimension"]

    variable["bounds"]["min_bounds"] = variables_zeros(dimension, new_interpolation)
    variable["bounds"]["max_bounds"] = variables_zeros(dimension, new_interpolation)

    phases_info[phase_index]["control_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)

    return phases_info


@router.put(
    "/phases_info/{phase_index}/control_variables/{variable_index}/initial_guess_interpolation_type"
)
def put_control_variables_initial_guess_interpolation_type(
    phase_index: int, variable_index: int, interpolation: InterpolationTypeRequest
):
    phases_info = read_generic_ocp_data("phases_info")

    new_interpolation = interpolation.interpolation_type

    variable = phases_info[phase_index]["control_variables"][variable_index]

    variable["initial_guess_interpolation_type"] = new_interpolation
    dimension = variable["dimension"]
    variable["initial_guess"] = variables_zeros(dimension, new_interpolation)

    phases_info[phase_index]["control_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


@router.put("/phases_info/{phase_index}/state_variables/{variable_index}/max_bounds")
def put_state_variables_max_bounds_value(
    phase_index: int, variable_index: int, value: VariableUpdateRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    x, y, new_value = value.x, value.y, value.value

    variable = phases_info[phase_index]["state_variables"][variable_index]

    variable["bounds"]["max_bounds"][x][y] = new_value

    phases_info[phase_index]["state_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


@router.put("/phases_info/{phase_index}/state_variables/{variable_index}/min_bounds")
def put_state_variables_min_bounds_value(
    phase_index: int, variable_index: int, value: VariableUpdateRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    x, y, new_value = value.x, value.y, value.value

    variable = phases_info[phase_index]["state_variables"][variable_index]

    variable["bounds"]["min_bounds"][x][y] = new_value

    phases_info[phase_index]["state_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


@router.put("/phases_info/{phase_index}/state_variables/{variable_index}/initial_guess")
def put_state_variables_initial_guess_value(
    phase_index: int, variable_index: int, value: VariableUpdateRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    x, y, new_value = value.x, value.y, value.value

    variable = phases_info[phase_index]["state_variables"][variable_index]

    variable["initial_guess"][x][y] = new_value

    phases_info[phase_index]["state_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


@router.put("/phases_info/{phase_index}/control_variables/{variable_index}/max_bounds")
def put_control_variables_max_bounds_value(
    phase_index: int, variable_index: int, value: VariableUpdateRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    x, y, new_value = value.x, value.y, value.value

    variable = phases_info[phase_index]["control_variables"][variable_index]

    variable["bounds"]["max_bounds"][x][y] = new_value

    phases_info[phase_index]["control_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


@router.put("/phases_info/{phase_index}/control_variables/{variable_index}/min_bounds")
def put_control_variables_min_bounds_value(
    phase_index: int, variable_index: int, value: VariableUpdateRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    x, y, new_value = value.x, value.y, value.value

    variable = phases_info[phase_index]["control_variables"][variable_index]

    variable["bounds"]["min_bounds"][x][y] = new_value
    phases_info[phase_index]["control_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info


@router.put(
    "/phases_info/{phase_index}/control_variables/{variable_index}/initial_guess"
)
def put_control_variables_initial_guess_value(
    phase_index: int, variable_index: int, value: VariableUpdateRequest
):
    phases_info = read_generic_ocp_data("phases_info")
    x, y, new_value = value.x, value.y, value.value

    variable = phases_info[phase_index]["control_variables"][variable_index]

    variable["initial_guess"][x][y] = new_value
    phases_info[phase_index]["control_variables"][variable_index] = variable

    update_generic_ocp_data("phases_info", phases_info)
    return phases_info
