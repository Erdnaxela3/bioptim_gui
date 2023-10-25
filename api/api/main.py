import json

from fastapi import FastAPI

import acrobatics_ocp.acrobatics as acrobatics
import penalty.penalty as penalty
import generic_ocp.generic_ocp as generic_ocp
import variables.variables as variables


app = FastAPI()

app.include_router(acrobatics.router)
app.include_router(penalty.router)
app.include_router(variables.router)
app.include_router(generic_ocp.router)


@app.on_event("startup")
def startup_event():
    acrobatics_datafile = "acrobatics_data.json"

    base_acrobatics_data = {
        "nb_somersaults": 1,
        "model_path": "",
        "final_time": 1.0,
        "final_time_margin": 0.1,
        "position": "straight",
        "sport_type": "trampoline",
        "preferred_twist_side": "left",
        "somersaults_info": [
            {
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
        ],
    }

    with open(acrobatics_datafile, "w") as f:
        json.dump(base_acrobatics_data, f)

    generic_datafile = "generic_ocp_data.json"

    base_generic_data = {
        "nb_phases": 1,
        "model_path": "",
        "phases_info": [
            {
                "nb_shooting_points": 24,
                "duration": 1.0,
                "dynamics": "TORQUE_DRIVEN",
                "state_variables": [
                    {
                        "name": "q",
                        "dimension": 1,
                        "bounds_interpolation_type": "CONSTANT_WITH_FIRST_AND_LAST_DIFFERENT",
                        "bounds": {
                            "min_bounds": [[-1.0, -2.0, -3.0]],
                            "max_bounds": [[1.0, 2.0, 3.0]],
                        },
                        "initial_guess_interpolation_type": "CONSTANT",
                        "initial_guess": [[4.0]],
                    },
                    {
                        "name": "qdot",
                        "dimension": 1,
                        "bounds_interpolation_type": "CONSTANT_WITH_FIRST_AND_LAST_DIFFERENT",
                        "bounds": {
                            "min_bounds": [[-10.0, -20.0, -30.0]],
                            "max_bounds": [[10.0, 20.0, 30.0]],
                        },
                        "initial_guess_interpolation_type": "CONSTANT",
                        "initial_guess": [[40.0]],
                    },
                ],
                "control_variables": [
                    {
                        "name": "tau",
                        "dimension": 1,
                        "bounds_interpolation_type": "CONSTANT_WITH_FIRST_AND_LAST_DIFFERENT",
                        "bounds": {
                            "min_bounds": [[-100.0, -200.0, -300.0]],
                            "max_bounds": [[100.0, 200.0, 300.0]],
                        },
                        "initial_guess_interpolation_type": "CONSTANT",
                        "initial_guess": [[400.0]],
                    },
                ],
                "objectives": [],
                "constraints": [],
            }
        ],
    }

    with open(generic_datafile, "w") as f:
        json.dump(base_generic_data, f)


@app.on_event("shutdown")
def startup_event():
    datafiles = ["acrobatics_data.json", "generic_data.json"]

    import os

    for datafile in datafiles:
        os.remove(datafile)
