import json

from fastapi import FastAPI

import acrobatics_ocp.acrobatics as acrobatics
import penalty.penalty as penalty
import generic_ocp.generic_ocp as generic_ocp


app = FastAPI()

app.include_router(acrobatics.router)
app.include_router(penalty.router)
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
