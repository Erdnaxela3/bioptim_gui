import inspect

import bioptim
from bioptim import ObjectiveFcn
from fastapi import HTTPException


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
