import json

from fastapi import FastAPI

import acrobatics_ocp.acrobatics as acrobatics

app = FastAPI()
app.include_router(acrobatics.router)


@app.on_event("startup")
def startup_event():
    datafile = "acrobatics_data.json"

    base_data = {
        "nb_somersaults": 1,
        "model_path": "",
        "final_time": 1,
        "final_time_margin": 0.1,
        "position": "straight",
        "sport_type": "trampoline",
        "preferred_twist_side": "left",
        "somersaults_info": [
            {
                "nb_shooting_points": 24,
                "nb_half_twists": 0,
                "duration": 1,
                "objectives": [
                    {
                        "objective_type": "lagrange",
                        "penalty_type": "MINIMIZE_CONTROL",
                        "nodes": "ALL_SHOOTING",
                        "quadratic": True,
                        "expand": True,
                        "target": None,
                        "derivative": False,
                        "integration_rule": "RECTANGLE_LEFT",
                        "multi_thread": False,
                        "weight": 100.0,
                        "arguments": {
                            "key": {"value": "tau", "type": "string"},
                        },
                    },
                    {
                        "objective_type": "mayer",
                        "penalty_type": "MINIMIZE_TIME",
                        "nodes": "END",
                        "quadratic": True,
                        "expand": True,
                        "target": None,
                        "derivative": False,
                        "integration_rule": "RECTANGLE_LEFT",
                        "multi_thread": False,
                        "weight": 1.0,
                        "arguments": {
                            "min_bound": {"value": 0.0, "type": "float"},
                            "max_bound": {"value": 0.0, "type": "float"},
                        },
                    },
                ],
                "constraints": [],
            }
        ],
    }

    with open(datafile, "w") as f:
        json.dump(base_data, f)


@app.on_event("shutdown")
def startup_event():
    datafile = "acrobatics_data.json"

    import os

    os.remove(datafile)
