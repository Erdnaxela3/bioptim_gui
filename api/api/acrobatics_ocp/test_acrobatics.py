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


def test_put_sport_type():
    response = client.put("/acrobatics/sport_type/", json={"sport_type": "trampoline"})
    assert response.status_code == 200, response
    assert response.json() == {"sport_type": "trampoline"}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    assert response.json()["sport_type"] == "trampoline"


def test_put_sport_type_wrong():
    response = client.put("/acrobatics/sport_type/", json={"sport_type": "wrong"})
    assert response.status_code == 422, response


def test_put_preferred_twist_side():
    response = client.put(
        "/acrobatics/preferred_twist_side/", json={"preferred_twist_side": "right"}
    )
    assert response.status_code == 200, response
    assert response.json() == {"preferred_twist_side": "right"}

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    assert response.json()["preferred_twist_side"] == "right"


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
    response = client.put("/acrobatics/somersaults_info/0/shooting_points")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_shooting_points"] == 24

    response = client.put(
        "/acrobatics/somersaults_info/0/nb_shooting_points/",
        json={"nb_shooting_points": 10},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/somersaults_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_shooting_points"] == 10


def test_actually_deleted_fields():
    # TODO change a somersault duration then delete
    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()

    assert data["nb_somersaults"] == 1
    assert data["model_path"] == "test/path"
    assert data["final_time"] == 2
    assert data["final_time_margin"] == 0.2
    assert data["position"] == "tuck"
    assert data["sport_type"] == "trampoline"
    assert data["preferred_twist_side"] == "right"

    client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 0})

    client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 1})
    response = client.get("/acrobatics/")
    data = response.json()
    assert data["model_path"] != "test/path"
    assert data["final_time"] != 2
    assert data["final_time_margin"] != 0.2
    assert data["position"] != "tuck"
    assert data["preferred_twist_side"] != "right"
