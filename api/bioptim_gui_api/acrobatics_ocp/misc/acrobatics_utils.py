import copy
import json

import numpy as np

from bioptim_gui_api.acrobatics_ocp.misc.acrobatics_data import AcrobaticsOCPData
from bioptim_gui_api.acrobatics_ocp.misc.models import AdditionalCriteria
from bioptim_gui_api.acrobatics_ocp.penalties.collision_constraint import collision_constraint_constraints
from bioptim_gui_api.acrobatics_ocp.penalties.common import common_objectives
from bioptim_gui_api.acrobatics_ocp.penalties.kickout import kickout_objectives
from bioptim_gui_api.acrobatics_ocp.penalties.landing import landing_objectives
from bioptim_gui_api.acrobatics_ocp.penalties.pike_tuck import pike_tuck_objectives
from bioptim_gui_api.acrobatics_ocp.penalties.somersault import somersault_objectives, somersault_constraints
from bioptim_gui_api.acrobatics_ocp.penalties.twist import twist_objectives
from bioptim_gui_api.acrobatics_ocp.penalties.waiting import waiting_objectives
from bioptim_gui_api.acrobatics_ocp.penalties.with_spine import with_spine_objectives
from bioptim_gui_api.acrobatics_ocp.penalties.with_visual_criteria import with_visual_criteria_objectives
from bioptim_gui_api.acrobatics_ocp.variables.variable_compute import get_variable_computer


def update_state_control_variables(phases: list[dict], data: dict) -> None:
    """
    Updates the state and control variables of the phases according to given data.
    Updates the dimension of the state and control variables.
    Updates the bounds and initial guess of the state and control variables.
    Updates the bounds interpolation type and initial guess interpolation type of the state and control variables.

    Parameters
    ----------
    phases: list[dict]
        The list of phases to update
    data: dict
        The data of the acrobatics
    """
    dynamics_control = {
        "torque_driven": "tau",
        "joints_acceleration_driven": "qddot_joints",
    }

    nb_somersaults = data["nb_somersaults"]
    half_twists = data["nb_half_twists"]
    prefer_left = data["preferred_twist_side"] == "left"
    position = data["position"]
    additional_criteria = AdditionalCriteria(
        with_visual_criteria=data["with_visual_criteria"],
        collision_constraint=data["collision_constraint"],
        with_spine=data["with_spine"],
    )
    final_time = data["final_time"]
    is_forward = sum(half_twists) % 2 != 0

    model = get_variable_computer(position, additional_criteria)

    nb_q = model.nb_q
    nb_qdot = model.nb_qdot
    nb_tau = model.nb_tau

    q_bounds = model.get_q_bounds(half_twists, prefer_left)
    nb_phases = len(q_bounds)
    qdot_bounds = model.get_qdot_bounds(nb_phases, final_time, is_forward)
    tau_bounds = model.get_tau_bounds()

    q_init = model.get_q_init(half_twists, prefer_left)
    qdot_init = model.get_qdot_init(nb_somersaults, final_time)
    tau_init = model.get_tau_init()

    for i, phase in enumerate(phases):
        phases[i]["state_variables"] = [
            {
                "name": "q",
                "dimension": nb_q,
                "bounds_interpolation_type": "CONSTANT_WITH_FIRST_AND_LAST_DIFFERENT",
                "bounds": {
                    "min_bounds": q_bounds[i]["min"].tolist(),
                    "max_bounds": q_bounds[i]["max"].tolist(),
                },
                "initial_guess_interpolation_type": "LINEAR",
                "initial_guess": q_init[i].T.tolist(),
            },
            {
                "name": "qdot",
                "dimension": nb_qdot,
                "bounds_interpolation_type": "CONSTANT_WITH_FIRST_AND_LAST_DIFFERENT",
                "bounds": {
                    "min_bounds": qdot_bounds[i]["min"].tolist(),
                    "max_bounds": qdot_bounds[i]["max"].tolist(),
                },
                "initial_guess_interpolation_type": "CONSTANT",
                "initial_guess": qdot_init,
            },
        ]
        phases[i]["control_variables"] = [
            {
                "name": dynamics_control[data["dynamics"]],
                "dimension": nb_tau,
                "bounds_interpolation_type": "CONSTANT",
                "bounds": {
                    "min_bounds": tau_bounds["min"],
                    "max_bounds": tau_bounds["max"],
                },
                "initial_guess_interpolation_type": "CONSTANT",
                "initial_guess": tau_init,
            },
        ]


def update_phase_info() -> list[dict]:
    """
    Update the phases_info of the acrobatics
    It will update the phase_name, duration and objectives and constraints according to the new phase names, the
    existing position, with_visual_criteria and collision_constraint.

    - Compute the phase names
    - The phase names are updated in the order they are given.
    - The new durations for each phase is calculated by dividing the final_time by the number of phases.
    - The phase's objectives and constraints are updated according to the new phase name, existing position, and
    additional criteria (with_visual_criteria and collision_constraint)


    Returns
    -------
    list[dict]
        The updated phases_info
    """
    data = AcrobaticsOCPData.read_data()

    nb_somersaults = data["nb_somersaults"]
    position = data["position"]
    half_twists = data["nb_half_twists"]
    final_time = data["final_time"]
    additional_criteria = AdditionalCriteria(
        with_visual_criteria=data["with_visual_criteria"],
        collision_constraint=data["collision_constraint"],
        with_spine=data["with_spine"],
    )
    dynamics = data["dynamics"]

    phase_names = acrobatics_phase_names(nb_somersaults, position, half_twists)
    n_phases = len(phase_names)
    new_phases = [phase_name_to_info(position, phase_names, i, additional_criteria) for i, _ in enumerate(phase_names)]

    for i in range(n_phases):
        new_phases[i]["phase_name"] = phase_names[i]
        # rounding is necessary to avoid buffer overflow in the frontend
        new_phases[i]["duration"] = round(final_time / n_phases, 2)

    update_state_control_variables(new_phases, data)

    for phase in new_phases:
        adapt_dynamics(phase, dynamics)

    AcrobaticsOCPData.update_data("nb_phases", n_phases)
    AcrobaticsOCPData.update_data("phases_info", new_phases)

    return new_phases


def calculate_n_tuck(half_twists: list[int]) -> int:
    """
    Calculate the number of tuck/pike phases given the number of half twists in each somersault of the acrobatics

    The number of tuck/pike is at least 1 (acrobatics with no half twists whatsoever).
    A beginning or an ending half twist does impact the number of tuck/pike phases.
    But every somersault with a half twist in the middle will add a tuck/pike phase.

    Parameters
    ----------
    half_twists: list[int]
        The number of half twists for each phase

    Returns
    -------
    The number of tuck/pike phases in the acrobatics
    """
    return sum(np.array(half_twists[1:-1]) > 0) + 1


def acrobatics_phase_names(nb_somersaults: int, position: str, half_twists: list[int]) -> list[str]:
    """
    Calculate the phase names of the acrobatics

    Straight acrobatics: Somersault 1, Somersault 2, ..., Landing (The twists are done within the somersaults)
    Tuck/Pike acrobatics: Twist, Tuck/Pike, Somersault, Kick out, Twists, ..., Landing,
    (The phases names are computed with the same logic as in calculate_n_tuck)


    Parameters
    ----------
    nb_somersaults: int
        The number of somersaults in the acrobatics
    position: str
        The position of the acrobatics
    half_twists: list[int]
        The number of half twists for each phase

    Returns
    -------
    list[str]:
        The phase names of the acrobatics
    """
    if position == "straight":
        return [f"Somersault {i + 1}" for i in range(nb_somersaults)] + ["Landing"]

    n_tucks = calculate_n_tuck(half_twists)

    names = ["Twist"] if half_twists[0] > 0 else []
    names += [position.capitalize(), "Somersault", "Kick out", "Twist"] * n_tucks

    if half_twists[-1] == 0:
        names[-1] = "Waiting"

    names.append("Landing")
    return names


def get_phase_objectives(
    phase_names: list[str], phase_index: int, position: str, additional_criteria: AdditionalCriteria
) -> list[dict]:
    """
    Returns the list of objectives for the given phase name, position and additional criteria

    Parameters
    ----------
    phase_names: list[str]
        The list of phase names (e.g. ["Somersault", "Landing", "Twist", ...])
    phase_index: int
        The index of the phase in the list of phase names, is used to get the phase name
        Some objectives depends on the index of the phase (First, last, ...)
    position: str
        The position of the acrobatics (e.g. "straight", "pike", "tuck")
    additional_criteria: AdditionalCriteria
        The additional criteria (e.g. with_visual_criteria, collision_constraint, without_cone)

    Returns
    -------
    list[dict]
        The list of objectives (e.g. [{penalty_type, nodes, target, arguments, weight, ...} ...])
    """
    with_visual_criteria = additional_criteria.with_visual_criteria
    with_spine = additional_criteria.with_spine

    phase_name = phase_names[phase_index]
    model = get_variable_computer(position, additional_criteria)

    objectives = common_objectives(
        phase_name=phase_names[phase_index], position=position, phase_index=phase_index, model=model
    )

    objectives += pike_tuck_objectives(phase_name, model, position)
    objectives += kickout_objectives(phase_name, model)
    objectives += twist_objectives(phase_name, model)
    objectives += waiting_objectives(phase_name, model)
    objectives += landing_objectives(phase_name, model, position)
    objectives += somersault_objectives(phase_name, model)

    if with_visual_criteria:
        objectives += with_visual_criteria_objectives(phase_names, phase_index, model)

    if with_spine:
        objectives += with_spine_objectives(model)

    return objectives


def get_phase_constraints(phase_name: str, position: str, additional_criteria: AdditionalCriteria) -> list[dict]:
    """
    Returns the list of constraints for the given phase name, position and additional criteria

    Parameters
    ----------
    phase_name: str
        The name of the phase (e.g. "Somersault", "Landing", "Twist", ...)
    position: str
        The position of the acrobatics (e.g. "straight", "pike", "tuck")
    additional_criteria: AdditionalCriteria
        The additional criteria (e.g. with_visual_criteria, collision_constraint, without_cone)

    Returns
    -------
    list[dict]
        The list of constraints (e.g. [{penalty_type, nodes, target, arguments, ...} ...])
    """
    collision_constraint = additional_criteria.collision_constraint

    constraints = []
    constraints += somersault_constraints(phase_name, position)

    if collision_constraint:
        constraints += collision_constraint_constraints(phase_name, position)

    return constraints


def adapt_dynamics(phase: dict, dynamics: str) -> None:
    dynamics_control = {
        "torque_driven": "tau",
        "joints_acceleration_driven": "qddot_joints",
    }
    control_names = dynamics_control.values()
    control = dynamics_control[dynamics]

    for objective in phase["objectives"]:
        for arguments in objective["arguments"]:
            if arguments["name"] == "key" and arguments["value"] in control_names:
                arguments["value"] = control

    for control_variable in phase["control_variables"]:
        if control_variable["name"] in control_names:
            control_variable["name"] = control


def phase_name_to_info(
    position, phase_names: list[str], phase_index: int, additional_criteria: AdditionalCriteria
) -> dict:
    """
    Returns the phase info for the given phase name, position and additional criteria

    Parameters
    ----------
    position: str
        The position of the acrobatics (e.g. "straight", "pike", "tuck")
    phase_names: list[str]
        The list of phase names (e.g. ["Somersault", "Landing", "Twist", ...])
    phase_index: int
        The index of the phase in the list of phase names, is used to get the phase name
        Some objectives depends on the index of the phase (First, last, ...)
    additional_criteria: AdditionalCriteria
        The additional criteria (e.g. with_visual_criteria, collision_constraint, without_cone)

    Returns
    -------
    dict
        The phase info (e.g. {phase_name, nb_shooting_points, objectives, constraints, ...})

    """
    phase_name = phase_names[phase_index]

    # need to deepcopy or else there will be unwanted modification due to addresses
    res = copy.deepcopy(AcrobaticsOCPData.default_phases_info)
    res["phase_name"] = phase_name

    res["objectives"] = get_phase_objectives(phase_names, phase_index, position, additional_criteria)
    res["constraints"] = get_phase_constraints(phase_name, position, additional_criteria)

    with open(AcrobaticsOCPData.datafile, "r") as f:
        dynamics = json.load(f)["dynamics"]

    adapt_dynamics(res, dynamics)

    return res
