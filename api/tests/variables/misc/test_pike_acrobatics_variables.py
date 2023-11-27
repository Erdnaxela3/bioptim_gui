import numpy as np
import pytest

from bioptim_gui_api.variables.misc.pike_acrobatics_variables import (
    PikeAcrobaticsVariables,
)


# P pike
# S somersault
# K kick out
# T twist
# W waiting
# L landing
@pytest.mark.parametrize(
    ("half_twists", "phases_str"),
    [
        ([0, 0], "PSKWL"),
        ([1, 0], "TPSKWL"),
        ([0, 1], "PSKTL"),
        ([1, 1], "TPSKTL"),
        ([0, 0, 0], "PSKWL"),
        ([0, 0, 1], "PSKTL"),
        ([0, 1, 0], "PSKTPSKWL"),
        ([0, 1, 1], "PSKTPSKTL"),
        ([1, 0, 0], "TPSKWL"),
        ([1, 0, 1], "TPSKTL"),
        ([1, 1, 0], "TPSKTPSKWL"),
        ([0, 0, 0, 0], "PSKWL"),
        ([0, 0, 0, 1], "PSKTL"),
        ([0, 0, 1, 0], "PSKTPSKWL"),
        ([0, 0, 1, 1], "PSKTPSKTL"),
        ([0, 1, 0, 0], "PSKTPSKWL"),
        ([0, 1, 0, 1], "PSKTPSKTL"),
        ([0, 1, 1, 0], "PSKTPSKTPSKWL"),
        ([0, 1, 1, 1], "PSKTPSKTPSKTL"),
        ([1, 0, 0, 0], "TPSKWL"),
        ([1, 0, 0, 1], "TPSKTL"),
        ([1, 0, 1, 0], "TPSKTPSKWL"),
        ([1, 0, 1, 1], "TPSKTPSKTL"),
        ([1, 1, 0, 0], "TPSKTPSKWL"),
        ([1, 1, 0, 1], "TPSKTPSKTL"),
        ([1, 1, 1, 0], "TPSKTPSKTPSKWL"),
        ([1, 1, 1, 1], "TPSKTPSKTPSKTL"),
    ],
)
def test_q_bounds_number(half_twists, phases_str):
    phases = PikeAcrobaticsVariables.get_q_bounds(
        half_twists=half_twists,
        prefer_left=False,
    )
    assert len(phases) == len(phases_str)
    # assert expected_number_of_phase == len(phases_str) # to check if the test is correctly written
    # assert "".join(phases) == phases_str


def test_q_bounds_quadruple_left_forward():
    actual = PikeAcrobaticsVariables.get_q_bounds(
        half_twists=[1, 0, 2, 4],
        prefer_left=True,
    )

    assert actual is not None


def test_q_init_quadruple_left_forward():
    actual = PikeAcrobaticsVariables.get_q_init(
        nb_phases=10,
        half_twists=[1, 0, 2, 4],
        prefer_left=True,
    )
    assert actual is not None


def test_qdot_bounds_quadruple_left_forward():
    expected = [
        {
            "min": [
                [-0.5, -10.0, -10.0],
                [-0.5, -10.0, -10.0],
                [17.62, -100.0, -100.0],
                [0.5, 0.5, 0.5],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
                [0.0, -100.0, -100.0],
            ],
            "max": [
                [0.5, 10.0, 10.0],
                [0.5, 10.0, 10.0],
                [21.62, 100.0, 100.0],
                [20.0, 20.0, 20.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
                [-0.0, 100.0, 100.0],
            ],
        },
        {
            "min": [
                [-10.0, -10.0, -10.0],
                [-10.0, -10.0, -10.0],
                [-100.0, -100.0, -100.0],
                [0.5, 0.5, 0.5],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
            ],
            "max": [
                [10.0, 10.0, 10.0],
                [10.0, 10.0, 10.0],
                [100.0, 100.0, 100.0],
                [20.0, 20.0, 20.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
            ],
        },
        {
            "min": [
                [-10.0, -10.0, -10.0],
                [-10.0, -10.0, -10.0],
                [-100.0, -100.0, -100.0],
                [0.5, 0.5, 0.5],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
            ],
            "max": [
                [10.0, 10.0, 10.0],
                [10.0, 10.0, 10.0],
                [100.0, 100.0, 100.0],
                [20.0, 20.0, 20.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
            ],
        },
        {
            "min": [
                [-10.0, -10.0, -10.0],
                [-10.0, -10.0, -10.0],
                [-100.0, -100.0, -100.0],
                [0.5, 0.5, 0.5],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
                [-100.0, -100.0, -100.0],
            ],
            "max": [
                [10.0, 10.0, 10.0],
                [10.0, 10.0, 10.0],
                [100.0, 100.0, 100.0],
                [20.0, 20.0, 20.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
                [100.0, 100.0, 100.0],
            ],
        },
    ]

    actual = PikeAcrobaticsVariables.get_qdot_bounds(4, 4.0, True)

    for i in range(4):
        for m in "min", "max":
            assert np.allclose(actual[i][m], expected[i][m])


def test_qdot_init():
    expected = [0.0] * 16
    actual = PikeAcrobaticsVariables.get_qdot_init()
    assert actual == expected


def test_tau_bounds():
    expected_min = [-500.0] * 10
    expected_max = [500.0] * 10
    actual = PikeAcrobaticsVariables.get_tau_bounds()
    actual_min, actual_max = actual["min"], actual["max"]
    assert actual_min == expected_min
    assert actual_max == expected_max


def test_tau_init():
    expected = [0.0] * 10
    actual = PikeAcrobaticsVariables.get_tau_init()
    assert actual == expected