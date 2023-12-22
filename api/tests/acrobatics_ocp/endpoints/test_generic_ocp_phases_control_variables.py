import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics import router
from bioptim_gui_api.acrobatics_ocp.misc.acrobatics_data import AcrobaticsOCPData

test_app = FastAPI()
test_app.include_router(router)
client = TestClient(test_app)


@pytest.fixture(autouse=True)
def run_for_all():
    # before test: create file
    datafile = AcrobaticsOCPData.datafile

    with open(datafile, "w") as f:
        json.dump(AcrobaticsOCPData.base_data, f)

    yield

    # after test : delete file
    import os

    os.remove(datafile)


def test_put_control_variable_dimension():
    response = client.put(
        "/acrobatics/phases_info/0/control_variables/0/dimension",
        json={"dimension": 2},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/phases_info/")
    phase_info = response.json()[0]
    assert phase_info["control_variables"][0]["dimension"] == 2
    assert phase_info["control_variables"][0]["bounds"]["min_bounds"] == [
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
    ]
    assert phase_info["control_variables"][0]["bounds"]["max_bounds"] == [
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
    ]
    assert phase_info["control_variables"][0]["initial_guess"] == [
        [0.0],
        [0.0],
    ]


def test_put_control_variable_bounds_interpolation_type():
    response = client.put(
        "/acrobatics/phases_info/0/control_variables/0/bounds_interpolation_type",
        json={"interpolation_type": "LINEAR"},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/phases_info/")
    phase_info = response.json()[0]
    assert phase_info["control_variables"][0]["bounds"]["min_bounds"] == [
        [0.0, 0.0],
    ]
    assert phase_info["control_variables"][0]["bounds"]["max_bounds"] == [
        [0.0, 0.0],
    ]


@pytest.mark.parametrize("bounds", ["min_bounds", "max_bounds"])
def test_put_control_variable_bounds(bounds):
    response = client.put(
        f"/acrobatics/phases_info/0/control_variables/0/{bounds}",
        json={
            "x": 0,
            "y": 0,
            "value": 42,
        },
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/phases_info/")
    phase_info = response.json()[0]
    assert phase_info["control_variables"][0]["bounds"][f"{bounds}"] == [[42.0, 0.0, 0.0]]


def test_put_control_variable_initial_guess():
    response = client.put(
        "/acrobatics/phases_info/0/control_variables/0/initial_guess",
        json={
            "x": 0,
            "y": 0,
            "value": 69,
        },
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/phases_info/")
    phase_info = response.json()[0]
    assert phase_info["control_variables"][0]["initial_guess"] == [[69.0]]


def test_put_control_variable_initial_guess_interpolation_type():
    response = client.put(
        "/acrobatics/phases_info/0/control_variables/0/initial_guess_interpolation_type",
        json={"interpolation_type": "LINEAR"},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/phases_info/")
    phase_info = response.json()[0]
    assert phase_info["control_variables"][0]["initial_guess"] == [[0.0, 0.0]]