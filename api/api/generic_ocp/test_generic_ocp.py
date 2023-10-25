import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from generic_ocp.generic_ocp import router

test_app = FastAPI()
test_app.include_router(router)
client = TestClient(test_app)


@pytest.fixture(autouse=True)
def run_for_all():
    # before test: create file
    datafile = "generic_ocp_data.json"

    base_data = {
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

    with open(datafile, "w") as f:
        json.dump(base_data, f)

    yield

    # after test : delete file
    import os

    os.remove(datafile)


# basic setter/getter tests


def test_put_nb_phase_negative():
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": -10})
    assert response.status_code == 400, response

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == 1

    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": -1})
    assert response.status_code == 400, response


def test_put_nb_phase_zero():
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 0})
    assert response.status_code == 200, response


def test_put_nb_phase():
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 2})
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == 2

    data = json.load(open("generic_ocp_data.json"))
    assert data["nb_phases"] == 2

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == 2


def test_put_model_path():
    response = client.put("/generic_ocp/model_path/", json={"model_path": "test/path"})
    assert response.status_code == 200, response
    assert response.json() == {"model_path": "test/path"}

    response = client.get("/generic_ocp/")
    assert response.status_code == 200
    assert response.json()["model_path"] == "test/path"


# effect of changing nb_phases tests


def test_base_info():
    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_phases"] == 1
    assert data["model_path"] == ""
    assert len(data["phases_info"]) == 1
    assert data["phases_info"][0]["duration"] == 1
    assert len(data["phases_info"][0]["objectives"]) == 0
    assert len(data["phases_info"][0]["constraints"]) == 0


def test_add_phase():
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 2})
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == 2

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_phases"] == 2
    assert data["model_path"] == ""
    assert len(data["phases_info"]) == 2
    assert data["phases_info"][0]["duration"] == 1
    assert data["phases_info"][1]["duration"] == 1
    assert len(data["phases_info"][0]["objectives"]) == 0
    assert len(data["phases_info"][0]["constraints"]) == 0
    assert len(data["phases_info"][1]["objectives"]) == 0
    assert len(data["phases_info"][1]["constraints"]) == 0


def test_add_multiple_phase():
    many = 10
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": many})
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == many

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_phases"] == many
    assert data["model_path"] == ""
    assert len(data["phases_info"]) == many
    for i in range(many):
        assert data["phases_info"][i]["duration"] == 1
        assert len(data["phases_info"][i]["objectives"]) == 0
        assert len(data["phases_info"][i]["constraints"]) == 0


def test_remove_one_phase_2to1():
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 2})
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == 2

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_phases"] == 2
    assert data["model_path"] == ""
    assert len(data["phases_info"]) == 2
    for i in range(2):
        assert data["phases_info"][i]["duration"] == 1
        assert len(data["phases_info"][i]["objectives"]) == 0
        assert len(data["phases_info"][i]["constraints"]) == 0

    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 1})
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == 1

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_phases"] == 1
    assert data["model_path"] == ""
    assert len(data["phases_info"]) == 1
    assert data["phases_info"][0]["duration"] == 1
    assert len(data["phases_info"][0]["objectives"]) == 0
    assert len(data["phases_info"][0]["constraints"]) == 0


def test_remove_single_phase():
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 0})
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == 0

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_phases"] == 0
    assert data["model_path"] == ""
    assert len(data["phases_info"]) == 0


def test_add_and_remove_multiple_phase():
    many = 10
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": many})
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == many

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_phases"] == many
    assert data["model_path"] == ""
    assert len(data["phases_info"]) == many
    for i in range(many):
        assert data["phases_info"][i]["duration"] == 1
        assert len(data["phases_info"][i]["objectives"]) == 0
        assert len(data["phases_info"][i]["constraints"]) == 0

    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 1})
    assert response.status_code == 200, response
    assert response.json()["nb_phases"] == 1

    response = client.get("/generic_ocp/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_phases"] == 1
    assert data["model_path"] == ""
    assert data["phases_info"][0]["duration"] == 1
    assert len(data["phases_info"][0]["objectives"]) == 0
    assert len(data["phases_info"][0]["constraints"]) == 0


def test_get_phases_info():
    response = client.get("/generic_ocp/phases_info/")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["duration"] == 1
    assert len(data[0]["objectives"]) == 0
    assert len(data[0]["constraints"]) == 0

    client.put("/generic_ocp/nb_phases/", json={"nb_phases": 2})
    response = client.get("/generic_ocp/phases_info/")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2
    assert data[0]["duration"] == 1
    assert len(data[0]["objectives"]) == 0
    assert len(data[0]["constraints"]) == 0


def test_get_phase_with_index():
    response = client.get("/generic_ocp/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 1
    assert len(data["objectives"]) == 0
    assert len(data["constraints"]) == 0


def test_get_phase_with_index_wrong():
    response = client.get("/generic_ocp/phases_info/1")
    assert response.status_code == 404, response


def test_put_shooting_points():
    response = client.get("/generic_ocp/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_shooting_points"] == 24

    response = client.put(
        "/generic_ocp/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": 10},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_shooting_points"] == 10


def test_put_shooting_points_wrong():
    response = client.put(
        "/generic_ocp/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": -10},
    )
    assert response.status_code == 400, response

    response = client.put(
        "/generic_ocp/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": 0},
    )
    assert response.status_code == 400, response


def test_put_shooting_points_wrong_type():
    response = client.put(
        "/generic_ocp/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": "wrong"},
    )
    assert response.status_code == 422, response


def test_put_shooting_points_unchanged_other_phases():
    """
    add a phase, change its shooting points, check that the other phases are unchanged
    """
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 2})
    assert response.status_code == 200, response

    response = client.put(
        "/generic_ocp/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": 10},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["nb_shooting_points"] == 10
    assert data[1]["nb_shooting_points"] == 24


def test_put_phase_duration():
    response = client.get("/generic_ocp/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 1

    response = client.put(
        "/generic_ocp/phases_info/0/duration",
        json={"duration": 0.5},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 0.5


def test_put_phase_duration_wrong():
    response = client.put(
        "/generic_ocp/phases_info/0/duration",
        json={"duration": -0.5},
    )
    assert response.status_code == 400, response

    response = client.put(
        "/generic_ocp/phases_info/0/duration",
        json={"duration": 0},
    )
    assert response.status_code == 400, response


def test_put_phase_duration_wrong_type():
    response = client.put(
        "/generic_ocp/phases_info/0/duration",
        json={"duration": "wrong"},
    )
    assert response.status_code == 422, response


def test_put_phase_duration_unchanged_other_phases():
    """
    add a phase, change its duration, check that the other phases are unchanged
    """
    response = client.put("/generic_ocp/nb_phases/", json={"nb_phases": 2})
    assert response.status_code == 200, response

    response = client.put(
        "/generic_ocp/phases_info/0/duration",
        json={"duration": 0.2},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["duration"] == 0.2
    assert data[1]["duration"] == 1


def test_add_objective_simple():
    response = client.post("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1


def test_add_objective_multiple():
    for _ in range(8):
        response = client.post("/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response
        data = response.json()
        assert len(data) == _ + 1


def test_get_objectives():
    for _ in range(2):
        response = client.post("/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2
    assert data[0]["weight"] == 1.0
    assert data[1]["weight"] == 1.0


def test_delete_objective_0():
    for _ in range(2):
        response = client.post("/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.delete("/generic_ocp/phases_info/0/objectives/0")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"


def test_delete_objective_1():
    for _ in range(2):
        response = client.post("/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.delete("/generic_ocp/phases_info/0/objectives/1")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"


def test_add_and_remove_objective():
    for _ in range(2):
        response = client.post("/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    data = response.json()
    assert len(data) == 2

    client.delete("/generic_ocp/phases_info/0/objectives/0")
    client.delete("/generic_ocp/phases_info/0/objectives/0")
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    data = response.json()
    assert len(data) == 0


def test_multiple_phases_add_remove_objective():
    client.put("/generic_ocp/nb_phases/", json={"nb_phases": 5})

    for i in range(5):
        for _ in range(2):
            response = client.post(f"/generic_ocp/phases_info/{i}/objectives")
            assert response.status_code == 200, response

    response = client.post("/generic_ocp/phases_info/3/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3

    client.delete("/generic_ocp/phases_info/3/objectives/0")
    client.delete("/generic_ocp/phases_info/3/objectives/0")
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/3/objectives")
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"

    for i in [0, 1, 2, 4]:
        response = client.get(f"/generic_ocp/phases_info/{i}/objectives")
        data = response.json()
        assert len(data) == 2
        assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"
        assert data[1]["penalty_type"] == "MINIMIZE_CONTROL"


@pytest.mark.parametrize(
    (
        "key",
        "default_value",
        "new_value",
    ),
    [
        ("objective_type", "lagrange", "mayer"),
        ("penalty_type", "MINIMIZE_CONTROL", "MINIMIZE_TIME"),
        ("nodes", "all_shooting", "end"),
        ("quadratic", True, False),
        ("expand", True, False),
        ("target", None, [0.2, 0.5]),
        ("derivative", False, True),
        ("integration_rule", "rectangle_left", "rectangle_right"),
        ("multi_thread", False, True),
        ("weight", 1.0, 10.0),
    ],
)
def test_put_objective_common_argument(key, default_value, new_value):
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0][key] == default_value

    response = client.put(
        f"/generic_ocp/phases_info/0/objectives/0/{key}",
        json={key: new_value},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0][key] == new_value


def test_put_weight_minmax():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["weight"] == 1

    response = client.put(
        f"/generic_ocp/phases_info/0/objectives/0/weight/maximize",
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["weight"] == -1

    response = client.put(
        f"/generic_ocp/phases_info/0/objectives/0/weight/minimize",
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["weight"] == 1


def test_put_weight_minmax_no_change():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["weight"] == 1

    response = client.put(
        f"/generic_ocp/phases_info/0/objectives/0/weight/minimize",
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["weight"] == 1

    response = client.put(
        f"/generic_ocp/phases_info/0/objectives/0/weight/maximize",
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["weight"] == -1

    response = client.put(
        f"/generic_ocp/phases_info/0/objectives/0/weight/maximize",
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["weight"] == -1


@pytest.mark.parametrize(
    (
        "key",
        "new_value",
    ),
    [
        ("objective_type", "mayer"),
        ("penalty_type", "MINIMIZE_TIME"),
        ("nodes", "end"),
        ("quadratic", False),
        ("expand", False),
        ("target", [0.2, 0.5]),
        ("derivative", True),
        ("integration_rule", "rectangle_right"),
        ("multi_thread", True),
        ("weight", 10.0),
    ],
)
def test_actually_deleted_fields_objective(key, new_value):
    """
    add one objective, change its values,
    remove it,
    add another objective,
    check that the values are reset
    """
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.post("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3

    response = client.put(
        f"/generic_ocp/phases_info/0/objectives/2/{key}", json={key: new_value}
    )
    assert response.status_code == 200, response

    response = client.delete("/generic_ocp/phases_info/0/objectives/2")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    response = client.post("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3
    assert data[2][key] != new_value


def test_get_constraints():
    response = client.get("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 0


def test_post_constraint():
    response = client.post("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] == "TIME_CONSTRAINT"
    assert data[0]["nodes"] == "end"
    assert data[0]["quadratic"]
    assert data[0]["expand"]
    assert data[0]["target"] is None
    assert not data[0]["derivative"]
    assert data[0]["integration_rule"] == "rectangle_left"
    assert not data[0]["multi_thread"]


def test_post_constraint_multiple():
    for i in range(8):
        response = client.post("/generic_ocp/phases_info/0/constraints")
        assert response.status_code == 200, response
        data = response.json()
        assert len(data) == i + 1
        assert data[i]["penalty_type"] == "TIME_CONSTRAINT"
        assert data[i]["nodes"] == "end"
        assert data[i]["quadratic"]
        assert data[i]["expand"]
        assert data[i]["target"] is None
        assert not data[i]["derivative"]
        assert data[i]["integration_rule"] == "rectangle_left"
        assert not data[i]["multi_thread"]


def test_delete_constraint_0():
    response = client.post("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1

    response = client.delete("/generic_ocp/phases_info/0/constraints/0")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 0

    response = client.get("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 0


@pytest.mark.parametrize(
    (
        "key",
        "default_value",
        "new_value",
    ),
    [
        ("penalty_type", "TIME_CONSTRAINT", "CONTINUITY"),
        ("nodes", "end", "all_shooting"),
        ("quadratic", True, False),
        ("expand", True, False),
        ("target", None, [0.2, 0.5]),
        ("derivative", False, True),
        ("integration_rule", "rectangle_left", "rectangle_right"),
        ("multi_thread", False, True),
    ],
)
def test_put_constraints_common_argument(key, default_value, new_value):
    response = client.post("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1

    response = client.get("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0][key] == default_value

    response = client.put(
        f"/generic_ocp/phases_info/0/constraints/0/{key}",
        json={key: new_value},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0][key] == new_value


def test_add_objective_check_arguments_changing_penalty_type():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    response = client.put(
        "/generic_ocp/phases_info/0/objectives/1/penalty_type",
        json={"penalty_type": "MINIMIZE_TIME"},
    )
    assert response.status_code == 200, response

    response = client.put(
        "/generic_ocp/phases_info/0/objectives/1/objective_type",
        json={"objective_type": "mayer"},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    assert data[0]["objective_type"] == "lagrange"
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"
    assert data[0]["nodes"] == "all_shooting"
    assert len(data[0]["arguments"]) == 1

    assert data[1]["objective_type"] == "mayer"
    assert data[1]["penalty_type"] == "MINIMIZE_TIME"
    assert data[1]["nodes"] == "all_shooting"
    assert len(data[1]["arguments"]) == 2

    # change the penalty_type of MINIMIZE_CONTROL to PROPORTIONAL_STATE
    response = client.put(
        "/generic_ocp/phases_info/0/objectives/0/penalty_type",
        json={"penalty_type": "PROPORTIONAL_STATE"},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["objective_type"] == "lagrange"
    assert data[0]["penalty_type"] == "PROPORTIONAL_STATE"
    assert data[0]["nodes"] == "all_shooting"
    assert len(data[0]["arguments"]) == 6

    arg_names = [arg["name"] for arg in data[0]["arguments"]]
    for arg in (
        "key",
        "first_dof",
        "second_dof",
        "coef",
        "first_dof_intercept",
        "second_dof_intercept",
    ):
        assert arg in arg_names


def test_add_objective_check_arguments_changing_objective_type():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    response = client.put(
        "/generic_ocp/phases_info/0/objectives/1/penalty_type",
        json={"penalty_type": "MINIMIZE_TIME"},
    )
    assert response.status_code == 200, response

    response = client.put(
        "/generic_ocp/phases_info/0/objectives/1/objective_type",
        json={"objective_type": "mayer"},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    assert data[0]["objective_type"] == "lagrange"
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"
    assert data[0]["nodes"] == "all_shooting"
    assert len(data[0]["arguments"]) == 1

    assert data[1]["objective_type"] == "mayer"
    assert data[1]["penalty_type"] == "MINIMIZE_TIME"
    assert data[1]["nodes"] == "all_shooting"
    assert len(data[1]["arguments"]) == 2

    # change the objective_type from mayer to lagrange for time
    response = client.put(
        "/generic_ocp/phases_info/0/objectives/1/objective_type",
        json={"objective_type": "lagrange"},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[1]["objective_type"] == "lagrange"
    assert data[1]["penalty_type"] == "MINIMIZE_TIME"
    assert data[1]["nodes"] == "all_shooting"
    assert len(data[1]["arguments"]) == 0


def test_remove_constraints_fields_delete():
    response = client.post("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response

    client.put(
        "/generic_ocp/phases_info/0/constraints/0/penalty_type",
        json={"penalty_type": "CONTINUITY"},
    )

    response = client.delete("/generic_ocp/phases_info/0/constraints/0")
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 0

    response = client.post("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] != "CONTINUITY"


def test_add_constraints_check_arguments_changing_penalty_type():
    response = client.post("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["arguments"]) == 0

    response = client.put(
        "/generic_ocp/phases_info/0/constraints/0/penalty_type",
        json={"penalty_type": "TRACK_POWER"},
    )
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["arguments"]) == 1
    assert "key_control" in [arg["name"] for arg in data[0]["arguments"]]


def test_get_arguments():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/penalty_type",
        json={"penalty_type": "MINIMIZE_TIME"},
    )
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/objective_type",
        json={"objective_type": "mayer"},
    )

    response = client.get(
        "/generic_ocp/phases_info/0/objectives/1/arguments/min_bound",
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["value"] is None


def test_get_arguments_bad():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/penalty_type",
        json={"penalty_type": "MINIMIZE_TIME"},
    )
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/objective_type",
        json={"objective_type": "mayer"},
    )

    response = client.get(
        "/generic_ocp/phases_info/0/objectives/1/arguments/impossible",
    )
    assert response.status_code == 404, response


def test_put_argument_objective():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/penalty_type",
        json={"penalty_type": "MINIMIZE_TIME"},
    )
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/objective_type",
        json={"objective_type": "mayer"},
    )

    response = client.put(
        "/generic_ocp/phases_info/0/objectives/1/arguments/min_bound",
        json={"type": "list", "value": [1, 2, 3]},
    )
    assert response.status_code == 200, response

    response = client.get(
        "/generic_ocp/phases_info/0/objectives/1/arguments/min_bound",
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["value"] == [1, 2, 3]
    assert data["type"] == "list"


def test_put_argument_objective_bad():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/penalty_type",
        json={"penalty_type": "MINIMIZE_TIME"},
    )
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/objective_type",
        json={"objective_type": "mayer"},
    )

    response = client.put(
        "/generic_ocp/phases_info/0/objectives/1/arguments/minor_bound",
        json={"type": "list", "value": [1, 2, 3]},
    )
    assert response.status_code == 404, response


def test_get_arguments_constraint():
    response = client.post("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response

    response = client.put(
        "/generic_ocp/phases_info/0/constraints/0/penalty_type",
        json={"penalty_type": "TRACK_POWER"},
    )
    assert response.status_code == 200, response

    response = client.get(
        "/generic_ocp/phases_info/0/constraints/0/arguments/key_control",
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["value"] is None


def test_get_arguments_constraint_bad():
    client.post("/generic_ocp/phases_info/0/constraints")
    client.put(
        "/generic_ocp/phases_info/0/constraints/0/penalty_type",
        json={"penalty_type": "TRACK_POWER"},
    )

    response = client.get(
        "/generic_ocp/phases_info/0/constraints/0/arguments/impossible",
    )
    assert response.status_code == 404, response


def test_put_arguments_constraint():
    client.post("/generic_ocp/phases_info/0/constraints")
    client.put(
        "/generic_ocp/phases_info/0/constraints/0/penalty_type",
        json={"penalty_type": "TRACK_POWER"},
    )

    response = client.put(
        "/generic_ocp/phases_info/0/constraints/0/arguments/key_control",
        json={"type": "list", "value": [1, 2, 3]},
    )
    assert response.status_code == 200, response

    response = client.get(
        "/generic_ocp/phases_info/0/constraints/0/arguments/key_control",
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["value"] == [1, 2, 3]
    assert data["type"] == "list"


def test_put_arguments_constraint_bad():
    client.post("/generic_ocp/phases_info/0/constraints")

    response = client.put(
        "/generic_ocp/phases_info/0/constraints/0/arguments/impossible",
        json={"type": "list", "value": [1, 2, 3]},
    )
    assert response.status_code == 404, response


def test_get_objective_fcn():
    for _ in range(2):
        response = client.post(f"/generic_ocp/phases_info/0/objectives")
        assert response.status_code == 200, response
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/penalty_type",
        json={"penalty_type": "MINIMIZE_TIME"},
    )
    client.put(
        "/generic_ocp/phases_info/0/objectives/1/objective_type",
        json={"objective_type": "mayer"},
    )

    response = client.get("/generic_ocp/phases_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["objective_type"] == "lagrange"
    assert data[1]["objective_type"] == "mayer"

    response = client.get("/generic_ocp/phases_info/0/objectives/0")
    assert response.status_code == 200, response
    data = response.json()
    assert type(data) is list
    assert len(data) != 0


def test_get_constraints_fcn():
    response = client.post("/generic_ocp/phases_info/0/constraints")
    assert response.status_code == 200, response

    response = client.get("/generic_ocp/phases_info/0/constraints/0")
    assert response.status_code == 200, response
    data = response.json()
    assert type(data) is list
    assert len(data) != 0


def test_get_dynamic():
    response = client.get("/generic_ocp/phases_info/1/dynamics")
    assert response.status_code == 200, response
    data = response.json()
    assert data == ["TORQUE_DRIVEN", "DUMMY"]


def test_put_dynamic():
    response = client.put(
        "/generic_ocp/phases_info/0/dynamics", json={"dynamics": "DUMMY"}
    )
    assert response.status_code == 200, response


def test_put_state_variable_interpolation_type():
    response = client.put(
        "/generic_ocp/phases_info/0/control_variables/0/initial_guess",
        json={
            "x": 0,
            "y": 0,
            "value": 69,
        },
    )
    assert response.status_code == 200, response
