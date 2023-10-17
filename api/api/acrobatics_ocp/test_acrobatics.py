from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest
import json

from acrobatics_ocp.acrobatics import router

test_app = FastAPI()
test_app.include_router(router)
client = TestClient(test_app)


@pytest.fixture(autouse=True)
def run_for_all():
    # before test: create file
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
        ],
    }

    with open(datafile, "w") as f:
        json.dump(base_data, f)

    yield

    # after test : delete file
    import os

    os.remove(datafile)


# basic setter/getter tests


def test_put_nb_somersault_negative():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": -10})
    assert response.status_code == 400, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    assert response.json()["nb_somersaults"] == 1

    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": -1})
    assert response.status_code == 400, response


def test_put_nb_somersault_zero():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 0})
    assert response.status_code == 200, response


def test_put_nb_somersault():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    assert response.status_code == 200, response
    assert response.json() == {"nb_somersaults": 2}

    data = json.load(open("acrobatics_data.json"))
    assert data["nb_somersaults"] == 2

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    assert response.json()["nb_somersaults"] == 2


def test_put_model_path():
    response = client.put("/acrobatics/model_path/", json={"model_path": "test/path"})
    assert response.status_code == 200, response
    assert response.json() == {"model_path": "test/path"}

    response = client.get("/acrobatics/")
    assert response.status_code == 200
    assert response.json()["model_path"] == "test/path"


def test_put_final_time_negative():
    response = client.put("/acrobatics/final_time/", json={"final_time": -10})
    assert response.status_code == 400, response

    response = client.put("/acrobatics/final_time/", json={"final_time": -1})
    assert response.status_code == 400, response


def test_put_final_time_zero():
    response = client.put("/acrobatics/final_time/", json={"final_time": 0})
    assert response.status_code == 200, response


def test_put_final_time():
    response = client.put("/acrobatics/final_time/", json={"final_time": 2})
    assert response.status_code == 200, response
    assert response.json() == {"final_time": 2}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    assert response.json()["final_time"] == 2


def test_put_final_time_margin_negative():
    response = client.put(
        "/acrobatics/final_time_margin/", json={"final_time_margin": -10}
    )
    assert response.status_code == 400, response

    response = client.put(
        "/acrobatics/final_time_margin/", json={"final_time_margin": -1}
    )
    assert response.status_code == 400, response


def test_put_final_time_margin_zero():
    response = client.put(
        "/acrobatics/final_time_margin/", json={"final_time_margin": 0}
    )
    assert response.status_code == 200, response


def test_put_final_time_margin():
    response = client.put(
        "/acrobatics/final_time_margin/", json={"final_time_margin": 0.2}
    )
    assert response.status_code == 200, response
    assert response.json() == {"final_time_margin": 0.2}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    assert response.json()["final_time_margin"] == 0.2


def test_get_position():
    response = client.get("/acrobatics/position/")
    assert response.status_code == 200, response
    assert set(response.json()) == {"Straight", "Tuck", "Pike"}


def test_put_position():
    response = client.put("/acrobatics/position/", json={"position": "tuck"})
    assert response.status_code == 200, response
    assert response.json() == {"position": "tuck"}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    assert response.json()["position"] == "tuck"


def test_put_position_wrong():
    response = client.put("/acrobatics/position/", json={"position": "wrong"})
    assert response.status_code == 422, response


def test_put_position_same():
    response = client.put("/acrobatics/position/", json={"position": "straight"})
    assert response.status_code == 304, response


def test_get_sport_type():
    response = client.get("/acrobatics/sport_type/")
    assert response.status_code == 200, response
    assert set(response.json()) == {"Trampoline", "Diving"}


def test_put_sport_type():
    response = client.put("/acrobatics/sport_type/", json={"sport_type": "diving"})
    assert response.status_code == 200, response
    assert response.json() == {"sport_type": "diving"}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    assert response.json()["sport_type"] == "diving"


def test_put_sport_type_wrong():
    response = client.put("/acrobatics/sport_type/", json={"sport_type": "wrong"})
    assert response.status_code == 422, response


def test_put_sport_type_same():
    response = client.put("/acrobatics/sport_type/", json={"sport_type": "trampoline"})
    assert response.status_code == 304, response


def test_get_preferred_twist_side():
    response = client.get("/acrobatics/preferred_twist_side/")
    assert response.status_code == 200, response
    assert set(response.json()) == {"Left", "Right"}


def test_put_preferred_twist_side_same():
    response = client.put(
        "/acrobatics/preferred_twist_side/", json={"preferred_twist_side": "left"}
    )
    assert response.status_code == 304, response


def test_put_preferred_twist_side_wrong():
    response = client.put(
        "/acrobatics/preferred_twist_side/", json={"preferred_twist_side": "wrong"}
    )
    assert response.status_code == 422, response


# effect of changing nb_somersaults tests


def test_base_info():
    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_somersaults"] == 1
    assert data["model_path"] == ""
    assert data["final_time"] == 1
    assert data["final_time_margin"] == 0.1
    assert data["position"] == "straight"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "left"
    assert len(data["somersaults_info"]) == 1
    assert data["somersaults_info"][0]["duration"] == 1
    assert len(data["somersaults_info"][0]["objectives"]) == 2
    assert len(data["somersaults_info"][0]["constraints"]) == 0


def test_add_somersault():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    assert response.status_code == 200, response
    assert response.json() == {"nb_somersaults": 2}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_somersaults"] == 2
    assert data["model_path"] == ""
    assert data["final_time"] == 1
    assert data["final_time_margin"] == 0.1
    assert data["position"] == "straight"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "left"
    assert len(data["somersaults_info"]) == 2
    assert data["somersaults_info"][0]["duration"] == 0.5
    assert data["somersaults_info"][1]["duration"] == 0.5
    assert len(data["somersaults_info"][0]["objectives"]) == 2
    assert len(data["somersaults_info"][0]["constraints"]) == 0
    assert len(data["somersaults_info"][1]["objectives"]) == 2
    assert len(data["somersaults_info"][1]["constraints"]) == 0


def test_add_multiple_somersault():
    many = 10
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": many})
    assert response.status_code == 200, response
    assert response.json() == {"nb_somersaults": many}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_somersaults"] == many
    assert data["model_path"] == ""
    assert data["final_time"] == 1
    assert data["final_time_margin"] == 0.1
    assert data["position"] == "straight"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "left"
    assert len(data["somersaults_info"]) == many
    for i in range(many):
        assert data["somersaults_info"][i]["duration"] == 1 / many
        assert len(data["somersaults_info"][i]["objectives"]) == 2
        assert len(data["somersaults_info"][i]["constraints"]) == 0


def test_remove_one_somersault_2to1():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    assert response.status_code == 200, response
    assert response.json() == {"nb_somersaults": 2}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_somersaults"] == 2
    assert data["model_path"] == ""
    assert data["final_time"] == 1
    assert data["final_time_margin"] == 0.1
    assert data["position"] == "straight"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "left"
    assert len(data["somersaults_info"]) == 2
    for i in range(2):
        assert data["somersaults_info"][i]["duration"] == 1 / 2
        assert len(data["somersaults_info"][i]["objectives"]) == 2
        assert len(data["somersaults_info"][i]["constraints"]) == 0

    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 1})
    assert response.status_code == 200, response
    assert response.json() == {"nb_somersaults": 1}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_somersaults"] == 1
    assert data["model_path"] == ""
    assert data["final_time"] == 1
    assert data["final_time_margin"] == 0.1
    assert data["position"] == "straight"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "left"
    assert len(data["somersaults_info"]) == 1
    assert data["somersaults_info"][0]["duration"] == 1
    assert len(data["somersaults_info"][0]["objectives"]) == 2
    assert len(data["somersaults_info"][0]["constraints"]) == 0


def test_remove_single_somersault():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 0})
    assert response.status_code == 200, response
    assert response.json() == {"nb_somersaults": 0}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_somersaults"] == 0
    assert data["model_path"] == ""
    assert data["final_time"] == 1
    assert data["final_time_margin"] == 0.1
    assert data["position"] == "straight"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "left"
    assert len(data["somersaults_info"]) == 0


def test_add_and_remove_multiple_somersault():
    many = 10
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": many})
    assert response.status_code == 200, response
    assert response.json() == {"nb_somersaults": many}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_somersaults"] == many
    assert data["model_path"] == ""
    assert data["final_time"] == 1
    assert data["final_time_margin"] == 0.1
    assert data["position"] == "straight"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "left"
    assert len(data["somersaults_info"]) == many
    for i in range(many):
        assert data["somersaults_info"][i]["duration"] == 1 / many
        assert len(data["somersaults_info"][i]["objectives"]) == 2
        assert len(data["somersaults_info"][i]["constraints"]) == 0

    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 1})
    assert response.status_code == 200, response
    assert response.json() == {"nb_somersaults": 1}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_somersaults"] == 1
    assert data["model_path"] == ""
    assert data["final_time"] == 1
    assert data["final_time_margin"] == 0.1
    assert data["position"] == "straight"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "left"
    assert len(data["somersaults_info"]) == 1
    assert data["somersaults_info"][0]["duration"] == 1
    assert len(data["somersaults_info"][0]["objectives"]) == 2
    assert len(data["somersaults_info"][0]["constraints"]) == 0


def test_get_somersaults_info():
    response = client.get("/acrobatics/somersaults_info/")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["duration"] == 1
    assert len(data[0]["objectives"]) == 2
    assert len(data[0]["constraints"]) == 0

    client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    response = client.get("/acrobatics/somersaults_info/")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2
    assert data[0]["duration"] == 0.5
    assert len(data[0]["objectives"]) == 2
    assert len(data[0]["constraints"]) == 0


def test_get_somersault_with_index():
    response = client.get("/acrobatics/somersaults_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 1
    assert len(data["objectives"]) == 2
    assert len(data["constraints"]) == 0


def test_get_somersault_with_index_wrong():
    response = client.get("/acrobatics/somersaults_info/1")
    assert response.status_code == 404, response


def test_put_shooting_points():
    response = client.get("/acrobatics/somersaults_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_shooting_points"] == 24

    response = client.put(
        "/acrobatics/somersaults_info/0/nb_shooting_points",
        json={"nb_shooting_points": 10},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_shooting_points"] == 10


def test_put_shooting_points_wrong():
    response = client.put(
        "/acrobatics/somersaults_info/0/nb_shooting_points",
        json={"nb_shooting_points": -10},
    )
    assert response.status_code == 400, response

    response = client.put(
        "/acrobatics/somersaults_info/0/nb_shooting_points",
        json={"nb_shooting_points": 0},
    )
    assert response.status_code == 400, response


def test_put_shooting_points_wrong_type():
    response = client.put(
        "/acrobatics/somersaults_info/0/nb_shooting_points",
        json={"nb_shooting_points": "wrong"},
    )
    assert response.status_code == 422, response


def test_put_shooting_points_unchanged_other_somersaults():
    """
    add a somersault, change its shooting points, check that the other somersaults are unchanged
    """
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    assert response.status_code == 200, response

    response = client.put(
        "/acrobatics/somersaults_info/0/nb_shooting_points",
        json={"nb_shooting_points": 10},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["nb_shooting_points"] == 10
    assert data[1]["nb_shooting_points"] == 24


def test_put_somersault_duration():
    response = client.get("/acrobatics/somersaults_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 1

    response = client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": 0.5},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 0.5


def test_put_somersault_duration_wrong():
    response = client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": -0.5},
    )
    assert response.status_code == 400, response

    response = client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": 0},
    )
    assert response.status_code == 400, response


def test_put_somersault_duration_wrong_type():
    response = client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": "wrong"},
    )
    assert response.status_code == 422, response


def test_put_somersault_duration_unchanged_other_somersaults():
    """
    add a somersault, change its duration, check that the other somersaults are unchanged
    """
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    assert response.status_code == 200, response

    response = client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": 0.2},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["duration"] == 0.2
    assert data[1]["duration"] == 0.5


def test_put_somersault_duration_changes_final_time_simple_more():
    response = client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": 1.2},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["final_time"] == 1.2


def test_put_somersault_duration_changes_final_time_simple_less():
    response = client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": 0.2},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["final_time"] == 0.2


def test_put_somersault_duration_changes_final_time_simple_more_multiple():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 5})
    assert response.status_code == 200, response

    client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": 1.2},
    )

    response = client.put(
        "/acrobatics/somersaults_info/1/duration",
        json={"duration": 0.6},
    )
    # durations : 1.2, 0.6, 0.2, 0.2, 0.2, final_time = 2.4

    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["final_time"] == 2.4


def test_put_somersault_duration_changes_final_time_simple_less_multiple():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 5})
    assert response.status_code == 200, response

    client.put(
        "/acrobatics/somersaults_info/0/duration",
        json={"duration": 0.1},
    )

    response = client.put(
        "/acrobatics/somersaults_info/1/duration",
        json={"duration": 0.1},
    )
    # durations : 0.1, 0.1, 0.2, 0.2, 0.2 final_time = 0.8

    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["final_time"] == 0.8


def test_put_nb_half_twists():
    response = client.get("/acrobatics/somersaults_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_half_twists"] == 0

    response = client.put(
        "/acrobatics/somersaults_info/0/nb_half_twists",
        json={"nb_half_twists": 1},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_half_twists"] == 1


def test_put_nb_half_twists_wrong():
    response = client.put(
        "/acrobatics/somersaults_info/0/nb_half_twists",
        json={"nb_half_twists": -1},
    )
    assert response.status_code == 400, response

    response = client.put(
        "/acrobatics/somersaults_info/0/nb_half_twists",
        json={"nb_half_twists": 0},
    )
    assert response.status_code == 200, response


def test_put_nb_half_twists_wrong_type():
    response = client.put(
        "/acrobatics/somersaults_info/0/nb_half_twists",
        json={"nb_half_twists": "wrong"},
    )
    assert response.status_code == 422, response


def test_get_objectives():
    response = client.get("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2
    assert data[0]["weight"] == 100.0
    assert data[1]["weight"] == 1.0


def test_add_objective_simple():
    response = client.post("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3


def test_add_objective_multiple():
    for _ in range(8):
        response = client.post("/acrobatics/somersaults_info/0/objectives")
        assert response.status_code == 200, response
        data = response.json()
        assert len(data) == _ + 3


def test_delete_objective_0():
    response = client.delete("/acrobatics/somersaults_info/0/objectives/0")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] == "MINIMIZE_TIME"


def test_delete_objective_1():
    response = client.delete("/acrobatics/somersaults_info/0/objectives/1")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"


def test_add_and_remove_objective():
    response = client.post("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3

    client.delete("/acrobatics/somersaults_info/0/objectives/0")
    client.delete("/acrobatics/somersaults_info/0/objectives/0")
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/objectives")
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"


def test_multiple_somersaults_add_remove_objective():
    client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 5})
    response = client.post("/acrobatics/somersaults_info/3/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3

    client.delete("/acrobatics/somersaults_info/3/objectives/0")
    client.delete("/acrobatics/somersaults_info/3/objectives/0")
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/3/objectives")
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"

    for i in [0, 1, 2, 4]:
        response = client.get(f"/acrobatics/somersaults_info/{i}/objectives")
        data = response.json()
        assert len(data) == 2
        assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"
        assert data[1]["penalty_type"] == "MINIMIZE_TIME"


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
        ("weight", 100.0, 10.0),
    ],
)
def test_put_objective_common_argument(key, default_value, new_value):
    response = client.get("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0][key] == default_value

    response = client.put(
        f"/acrobatics/somersaults_info/0/objectives/0/{key}",
        json={key: new_value},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0][key] == new_value


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
    response = client.post("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3

    response = client.put(
        f"/acrobatics/somersaults_info/0/objectives/2/{key}", json={key: new_value}
    )
    assert response.status_code == 200, response

    response = client.delete("/acrobatics/somersaults_info/0/objectives/2")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    response = client.post("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3
    assert data[2][key] != new_value


def test_get_constraints():
    response = client.get("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 0


def test_post_constraint():
    response = client.post("/acrobatics/somersaults_info/0/constraints")
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
        response = client.post("/acrobatics/somersaults_info/0/constraints")
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
    response = client.post("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1

    response = client.delete("/acrobatics/somersaults_info/0/constraints/0")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 0

    response = client.get("/acrobatics/somersaults_info/0/constraints")
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
    response = client.post("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1

    response = client.get("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0][key] == default_value

    response = client.put(
        f"/acrobatics/somersaults_info/0/constraints/0/{key}",
        json={key: new_value},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0][key] == new_value


def test_add_objective_check_arguments_changing_penalty_type():
    response = client.get("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    assert data[0]["objective_type"] == "lagrange"
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"
    assert data[0]["nodes"] == "all_shooting"
    assert len(data[0]["arguments"]) == 1

    assert data[1]["objective_type"] == "mayer"
    assert data[1]["penalty_type"] == "MINIMIZE_TIME"
    assert data[1]["nodes"] == "end"
    assert len(data[1]["arguments"]) == 2

    # change the penalty_type of MINIMIZE_CONTROL to PROPORTIONAL_STATE
    response = client.put(
        "/acrobatics/somersaults_info/0/objectives/0/penalty_type",
        json={"penalty_type": "PROPORTIONAL_STATE"},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["objective_type"] == "lagrange"
    assert data[0]["penalty_type"] == "PROPORTIONAL_STATE"
    assert data[0]["nodes"] == "all_shooting"
    assert len(data[0]["arguments"]) == 6
    for arg in (
        "key",
        "first_dof",
        "second_dof",
        "coef",
        "first_dof_intercept",
        "second_dof_intercept",
    ):
        assert arg in data[0]["arguments"].keys()

    assert data[0]["arguments"]["key"]["value"] is None
    assert data[0]["arguments"]["first_dof"]["value"] is None
    assert data[0]["arguments"]["second_dof"]["value"] is None
    assert data[0]["arguments"]["coef"]["value"] is None
    assert data[0]["arguments"]["first_dof_intercept"]["value"] == 0
    assert data[0]["arguments"]["second_dof_intercept"]["value"] == 0


def test_add_objective_check_arguments_changing_objective_type():
    response = client.get("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2

    assert data[0]["objective_type"] == "lagrange"
    assert data[0]["penalty_type"] == "MINIMIZE_CONTROL"
    assert data[0]["nodes"] == "all_shooting"
    assert len(data[0]["arguments"]) == 1

    assert data[1]["objective_type"] == "mayer"
    assert data[1]["penalty_type"] == "MINIMIZE_TIME"
    assert data[1]["nodes"] == "end"
    assert len(data[1]["arguments"]) == 2

    # change the objective_type from mayer to lagrange for time
    response = client.put(
        "/acrobatics/somersaults_info/0/objectives/1/objective_type",
        json={"objective_type": "lagrange"},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/objectives")
    assert response.status_code == 200, response
    data = response.json()
    assert data[1]["objective_type"] == "lagrange"
    assert data[1]["penalty_type"] == "MINIMIZE_TIME"
    assert data[1]["nodes"] == "end"
    assert len(data[1]["arguments"]) == 0


def test_remove_constraints_fields_delete():
    response = client.post("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response

    client.put(
        "/acrobatics/somersaults_info/0/constraints/0/penalty_type",
        json={"penalty_type": "CONTINUITY"},
    )

    response = client.delete("/acrobatics/somersaults_info/0/constraints/0")
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 0

    response = client.post("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert data[0]["penalty_type"] != "CONTINUITY"


def test_add_constraints_check_arguments_changing_penalty_type():
    response = client.post("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["arguments"]) == 0

    response = client.put(
        "/acrobatics/somersaults_info/0/constraints/0/penalty_type",
        json={"penalty_type": "TRACK_POWER"},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["arguments"]) == 1
    assert "key_control" in data[0]["arguments"].keys()


def test_get_arguments():
    response = client.get(
        "/acrobatics/somersaults_info/0/objectives/1/arguments/min_bound",
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["value"] == 0.9


def test_get_arguments_bad():
    response = client.get(
        "/acrobatics/somersaults_info/0/objectives/1/arguments/impossible",
    )
    assert response.status_code == 404, response


def test_put_argument_objective():
    response = client.put(
        "/acrobatics/somersaults_info/0/objectives/1/arguments/min_bound",
        json={"type": "list", "value": [1, 2, 3]},
    )
    assert response.status_code == 200, response

    response = client.get(
        "/acrobatics/somersaults_info/0/objectives/1/arguments/min_bound",
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["value"] == [1, 2, 3]
    assert data["type"] == "list"


def test_put_argument_objective_bad():
    response = client.put(
        "/acrobatics/somersaults_info/0/objectives/1/arguments/minor_bound",
        json={"type": "list", "value": [1, 2, 3]},
    )
    assert response.status_code == 404, response


def test_get_arguments_constraint():
    response = client.post("/acrobatics/somersaults_info/0/constraints")
    assert response.status_code == 200, response

    response = client.put(
        "/acrobatics/somersaults_info/0/constraints/0/penalty_type",
        json={"penalty_type": "TRACK_POWER"},
    )
    assert response.status_code == 200, response

    response = client.get(
        "/acrobatics/somersaults_info/0/constraints/0/arguments/key_control",
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["value"] is None


def test_get_arguments_constraint_bad():
    client.post("/acrobatics/somersaults_info/0/constraints")
    client.put(
        "/acrobatics/somersaults_info/0/constraints/0/penalty_type",
        json={"penalty_type": "TRACK_POWER"},
    )

    response = client.get(
        "/acrobatics/somersaults_info/0/constraints/0/arguments/impossible",
    )
    assert response.status_code == 404, response


def test_put_arguments_constraint():
    client.post("/acrobatics/somersaults_info/0/constraints")
    client.put(
        "/acrobatics/somersaults_info/0/constraints/0/penalty_type",
        json={"penalty_type": "TRACK_POWER"},
    )

    response = client.put(
        "/acrobatics/somersaults_info/0/constraints/0/arguments/key_control",
        json={"type": "list", "value": [1, 2, 3]},
    )
    assert response.status_code == 200, response

    response = client.get(
        "/acrobatics/somersaults_info/0/constraints/0/arguments/key_control",
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["value"] == [1, 2, 3]
    assert data["type"] == "list"


def test_put_arguments_constraint_bad():
    client.post("/acrobatics/somersaults_info/0/constraints")

    response = client.put(
        "/acrobatics/somersaults_info/0/constraints/0/arguments/impossible",
        json={"type": "list", "value": [1, 2, 3]},
    )
    assert response.status_code == 404, response
