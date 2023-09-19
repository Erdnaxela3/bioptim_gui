import 'dart:io';

import 'package:bioptim_gui/models/acrobatics_ocp_config.dart';
import 'package:bioptim_gui/models/dynamics.dart';
import 'package:bioptim_gui/models/decision_variables.dart';
import 'package:bioptim_gui/models/global.dart';
import 'package:bioptim_gui/models/penalty.dart';

class _Somersault {
  int somersaultIndex;
  int nbShootingPoints;
  int nbHalfTwists;
  double duration;
  Dynamics dynamics;

  final List<Objective> objectives = [];
  final List<Constraint> constraints = [];

  DecisionVariables stateVariables =
      DecisionVariables(DecisionVariableType.state);
  DecisionVariables controlVariables =
      DecisionVariables(DecisionVariableType.control);

  _Somersault({
    required this.somersaultIndex,
    required this.nbShootingPoints,
    required this.nbHalfTwists,
    required this.duration,
    required this.dynamics,
  });
}

///
/// This is the main class holder for the model. Nevertheless, this class should
/// not be instantiated manually but only by the [AcrobaticsOCPController].
/// Similarly, it should not be directly access (except from the said calss).
class AcrobaticsOCPProgram {
  ///
  /// Constructor

  AcrobaticsOCPProgram() {
    updateSomersaults();
  }

  ///
  /// Setters and Getters

  bool _hasPendingChangesToBeExported = true;
  void notifyThatModelHasChanged() => _hasPendingChangesToBeExported = true;
  bool get mustExport => _hasPendingChangesToBeExported;

  AcrobaticsOptimalControlProgram generic = AcrobaticsOptimalControlProgram();

  final somersaults = <_Somersault>[];
  void updateSomersaults() {
    if (somersaults.length < generic.nbSomersaults) {
      for (int i = somersaults.length; i < generic.nbSomersaults; i++) {
        somersaults.add(_Somersault(
            somersaultIndex: i,
            duration: 1.0,
            nbShootingPoints: 50,
            nbHalfTwists: 0,
            dynamics: const Dynamics(
                type: DynamicsType.torqueDriven, isExpanded: true)));
        resetVariables(somersaultIndex: i);
      }
    } else {
      // Do not change anything if we already have the right number of somersaults

      // Do not remove the somersaults if they are removed from the GUI, so it can
      // be reinstated prefilled with previous data
    }
    _hasPendingChangesToBeExported = true;
  }

  void resetVariables({required int somersaultIndex}) {
    somersaults[somersaultIndex].stateVariables.clearVariables();
    for (final name in somersaults[somersaultIndex].dynamics.type.states) {
      variables(
              from: DecisionVariableType.state,
              somersaultIndex: somersaultIndex)
          .addVariable(DecisionVariable(
        name: name,
        bounds: Bounds(
          nbElements: 1,
          interpolation: Interpolation.constantWithFirstAndLastDifferent,
        ),
        initialGuess:
            InitialGuess(nbElements: 1, interpolation: Interpolation.constant),
      ));
    }

    somersaults[somersaultIndex].controlVariables.clearVariables();
    for (final name in somersaults[somersaultIndex].dynamics.type.controls) {
      variables(
              from: DecisionVariableType.control,
              somersaultIndex: somersaultIndex)
          .addVariable(DecisionVariable(
        name: name,
        bounds: Bounds(
          nbElements: 1,
          interpolation: Interpolation.constantWithFirstAndLastDifferent,
        ),
        initialGuess:
            InitialGuess(nbElements: 1, interpolation: Interpolation.constant),
      ));
    }

    _hasPendingChangesToBeExported = true;
  }

  DecisionVariables variables(
      {required DecisionVariableType from, required int somersaultIndex}) {
    switch (from) {
      case DecisionVariableType.state:
        return somersaults[somersaultIndex].stateVariables;
      case DecisionVariableType.control:
        return somersaults[somersaultIndex].controlVariables;
    }
  }

  DecisionVariable variable(String name,
          {required DecisionVariableType from, required int somersaultIndex}) =>
      variables(from: from, somersaultIndex: somersaultIndex)[name];

  ///
  /// Main interface

  void exportScript(String path) {
    _hasPendingChangesToBeExported = false;
    final file = File(path);

    // Write the header
    file.writeAsStringSync('"""\n'
        'This file was automatically generated using BioptimGUI version $biotimGuiVersion\n'
        '"""\n'
        '\n'
        'import pickle as pkl\n'
        '\n'
        'import numpy as np\n'
        'from bioptim import (\n'
        '    BiorbdModel,\n'
        '    OptimalControlProgram,\n'
        '    DynamicsList,\n'
        '    DynamicsFcn,\n'
        '    BoundsList,\n'
        '    InitialGuessList,\n'
        '    ObjectiveList,\n'
        '    ObjectiveFcn,\n'
        '    ConstraintList,\n'
        '    InterpolationType,\n'
        '    BiMappingList,\n'
        '    Solver,\n'
        '    Node,\n'
        ')\n'
        'from casadi import MX, Function\n'
        '\n'
        '\n');

    // Write the docstring of the prepare_ocp section
    file.writeAsStringSync(
        'def prepare_ocp():\n'
        '    """\n'
        '    This function build an optimal control program and instantiate it.\n'
        '    It can be seen as a factory for the OptimalControlProgram class.\n'
        '\n'
        '    Parameters\n'
        '    ----------\n'
        '    # TODO fill this section\n'
        '\n'
        '    Returns\n'
        '    -------\n'
        '    The OptimalControlProgram ready to be solved\n'
        '    """\n'
        '\n',
        mode: FileMode.append);

    // Write the Generic section
    final nSomersaults = generic.nbSomersaults;
    final nSomersaultsAsString = nSomersaults.toString();
    final finalTimeMarginAsString = generic.finalTimeMargin.toString();

    final bioModelAsString =
        '${generic.bioModel.toPythonString()}(r"${generic.modelPath}")';

    final nShootingAsString = nSomersaults == 1
        ? somersaults[0].nbShootingPoints.toString()
        : '${[
            for (int i = 0; i < nSomersaults; i++)
              somersaults[i].nbShootingPoints.toString()
          ]}';

    final nHalfTwistsAsString = nSomersaults == 1
        ? somersaults[0].nbHalfTwists.toString()
        : '${[
            for (int i = 0; i < nSomersaults; i++)
              somersaults[i].nbHalfTwists.toString()
          ]}';

    final durationAsString = nSomersaults == 1
        ? somersaults[0].duration.toString()
        : '${[
            for (int i = 0; i < nSomersaults; i++)
              somersaults[i].duration.toString()
          ]}';

    file.writeAsStringSync(
        '    class SomersaultDirection:\n'
        '        FORWARD = "forward"\n'
        '        BACKWARD = "backward"\n'
        '\n'
        '    class PreferredTwistSide:\n'
        '        RIGHT = "right"\n'
        '        LEFT = "left"\n'
        '\n'
        '    # Declaration of generic elements\n'
        '    bio_model = $bioModelAsString\n'
        '\n'
        '    n_shooting = $nShootingAsString\n'
        '    phase_time = $durationAsString  # TODO user-input to add\n'
        '    final_time = $durationAsString  # TO CHECK\n'
        '    final_time_margin = $finalTimeMarginAsString\n'
        '    n_somersault = $nSomersaultsAsString\n'
        '    n_half_twist = $nHalfTwistsAsString\n'
        '    preferred_twist_side = PreferredTwistSide.LEFT\n'
        '    somersault_direction = (\n'
        '        SomersaultDirection.BACKWARD\n'
        '        if n_half_twist % 2 == 0\n'
        '        else SomersaultDirection.FORWARD\n'
        '    )\n'
        '\n'
        '    # Declaration of the constraints and objectives of the ocp\n'
        '    constraints = ConstraintList()\n'
        '    objective_functions = ObjectiveList()\n'
        '\n'
        '    objective_functions.add(\n'
        '        ObjectiveFcn.Lagrange.MINIMIZE_CONTROL,\n'
        '        key="tau",\n'
        '        node=Node.ALL_SHOOTING,\n'
        '        weight=100,\n'
        '    )\n'
        '\n'
        '    objective_functions.add(\n'
        '        ObjectiveFcn.Mayer.MINIMIZE_TIME, min_bound=final_time - final_time_margin, max_bound=final_time + final_time_margin, weight=1\n'
        '    )\n'
        '\n'
        '    # Declaration of the dynamics function used during integration\n'
        '    dynamics = DynamicsList()\n'
        '\n'
        '    dynamics.add(DynamicsFcn.TORQUE_DRIVEN, expand=True)\n'
        '\n'
        '    # Define control path constraint\n'
        '    tau_min, tau_max, tau_init = -100, 100, 0\n'
        '\n'
        '    n_q = bio_model.nb_q\n'
        '    n_qdot = bio_model.nb_qdot\n'
        '    n_tau = bio_model.nb_tau - bio_model.nb_root\n'
        '\n'
        '    # Declaration of optimization variables bounds and initial guesses\n'
        '    # Path constraint\n'
        '    x_bounds = BoundsList()\n'
        '    x_bounds["q"] = bio_model.bounds_from_ranges("q")\n'
        '    x_bounds["qdot"] = bio_model.bounds_from_ranges("qdot")\n'
        '\n'
        '    x_initial_guesses = InitialGuessList()\n'
        '\n'
        '    u_bounds = BoundsList()\n'
        '    u_initial_guesses = InitialGuessList()\n'
        '\n'
        '    # Initial bounds\n'
        '    x_bounds["q"].min[:, 0] = [\n'
        '        -0.001,  # pelvis translation X\n'
        '        -0.001,  # pelvis translation Y\n'
        '        -0.001,  # pelvis translation Z\n'
        '        0,  # pelvis rotation X, somersault\n'
        '        0,  # pelvis rotation Y, tilt\n'
        '        0,  # pelvis rotation Z, twist\n'
        '        0,  # right upper arm rotation Z\n'
        '        2.9,  # right upper arm rotation Y\n'
        '        0,  # left upper arm rotation Z\n'
        '        -2.9,  # left upper arm rotation Y\n'
        '    ]\n'
        '    x_bounds["q"].max[:, 0] = [\n'
        '        0.001,  # pelvis translation X\n'
        '        0.001,  # pelvis translation Y\n'
        '        0.001,  # pelvis translation Z\n'
        '        0,  # pelvis rotation X, somersault\n'
        '        0,  # pelvis rotation Y, tilt\n'
        '        0,  # pelvis rotation Z, twist\n'
        '        0,  # right upper arm rotation Z\n'
        '        2.9,  # right upper arm rotation Y\n'
        '        0,  # left upper arm rotation Z\n'
        '        -2.9,  # left upper arm rotation Y\n'
        '    ]\n'
        '\n'
        '    # Intermediate bounds\n'
        '    x_bounds["q"].min[:, 1] = [\n'
        '        -1,  # transX\n'
        '        -1,  # transY\n'
        '        -0.1,  # transZ\n'
        '        (\n'
        '            -0.2\n'
        '            if somersault_direction == SomersaultDirection.FORWARD\n'
        '            else -(2 * np.pi * n_somersault + 0.2)\n'
        '        ),  # somersault\n'
        '        -np.pi / 4,  # tilt\n'
        '        (\n'
        '            -0.2\n'
        '            if preferred_twist_side == PreferredTwistSide.LEFT\n'
        '            else -(np.pi * n_half_twist + 0.2)\n'
        '        ),  # twist\n'
        '        -0.65,  # right upper arm rotation Z\n'
        '        -0.05,  # right upper arm rotation Y\n'
        '        -2,  # left upper arm rotation Z\n'
        '        -3,  # left upper arm rotation Y\n'
        '    ]\n'
        '    x_bounds["q"].max[:, 1] = [\n'
        '        1,  # transX\n'
        '        1,  # transY\n'
        '        10,  # transZ\n'
        '        (\n'
        '            2 * np.pi * n_somersault + 0.2\n'
        '            if somersault_direction == SomersaultDirection.FORWARD\n'
        '            else 0.2\n'
        '        ),  # somersault\n'
        '        np.pi / 4,  # tilt\n'
        '        (\n'
        '            np.pi * n_half_twist + 0.2\n'
        '            if preferred_twist_side == PreferredTwistSide.LEFT\n'
        '            else 0.2\n'
        '        ),  # twist\n'
        '        2,  # right upper arm rotation Z\n'
        '        3,  # right upper arm rotation Y\n'
        '        0.65,  # left upper arm rotation Z\n'
        '        0.05,  # left upper arm rotation Y\n'
        '    ]\n'
        '\n'
        '    # Final bounds\n'
        '    x_bounds["q"].min[:, 2] = [\n'
        '        -1,  # transX\n'
        '        -1,  # transY\n'
        '        -0.1,  # transZ\n'
        '        (\n'
        '            2 * np.pi * n_somersault - 0.1\n'
        '            if somersault_direction == SomersaultDirection.FORWARD\n'
        '            else -2 * np.pi * n_somersault - 0.1\n'
        '        ),  # somersault\n'
        '        -0.1,  # tilt\n'
        '        (\n'
        '            np.pi * n_half_twist - 0.1\n'
        '            if preferred_twist_side == PreferredTwistSide.LEFT\n'
        '            else -np.pi * n_half_twist - 0.1\n'
        '        ),  # twist\n'
        '        -0.1,  # right upper arm rotation Z\n'
        '        2.9 - 0.1,  # right upper arm rotation Y\n'
        '        -0.1,  # left upper arm rotation Z\n'
        '        -2.9 - 0.1,  # left upper arm rotation Y\n'
        '    ]\n'
        '    x_bounds["q"].max[:, 2] = [\n'
        '        1,  # transX\n'
        '        1,  # transY\n'
        '        0.1,  # transZ\n'
        '        (\n'
        '            2 * np.pi * n_somersault + 0.1\n'
        '            if somersault_direction == SomersaultDirection.FORWARD\n'
        '            else -2 * np.pi * n_somersault + 0.1\n'
        '        ),  # somersault\n'
        '        0.1,  # tilt\n'
        '        (\n'
        '            np.pi * n_half_twist + 0.1\n'
        '            if preferred_twist_side == PreferredTwistSide.LEFT\n'
        '            else -np.pi * n_half_twist + 0.1\n'
        '        ),  # twist\n'
        '        0.1,  # right upper arm rotation Z\n'
        '        2.9 + 0.1,  # right upper arm rotation Y\n'
        '        0.1,  # left upper arm rotation Z\n'
        '        -2.9 + 0.1,  # left upper arm rotation Y\n'
        '    ]\n'
        '\n'
        '    x_init = np.array(\n'
        '        [\n'
        '            [0, 0, 0, 0, 0, 0, 0, 2.9, 0, -2.9],\n'
        '            [\n'
        '                0,\n'
        '                0,\n'
        '                0,\n'
        '                (\n'
        '                    2 * np.pi * n_somersault\n'
        '                    if somersault_direction == SomersaultDirection.FORWARD\n'
        '                    else -2 * np.pi * n_somersault\n'
        '                ),  # somersault\n'
        '                0,\n'
        '                (\n'
        '                    np.pi * n_half_twist\n'
        '                    if preferred_twist_side == PreferredTwistSide.LEFT\n'
        '                    else -np.pi * n_half_twist\n'
        '                ),  # twist\n'
        '                0,\n'
        '                2.9,\n'
        '                0,\n'
        '                -2.9,\n'
        '            ],\n'
        '        ]\n'
        '    ).T\n'
        '    x_initial_guesses.add(\n'
        '        "q",\n'
        '        initial_guess=x_init,\n'
        '        interpolation=InterpolationType.LINEAR,\n'
        '    )\n'
        '\n'
        '    # Taken from https://github.com/EveCharbie/AnthropoImpactOnTech/blob/main/TechOpt83.py\n'
        '    vzinit = (\n'
        '        9.81 / 2 * final_time\n'
        '    )  # vitesse initiale en z du CoM pour revenir a terre au temps final\n'
        '\n'
        '    x_bounds["qdot"].min[:, 0] = [\n'
        '        -0.5,  # pelvis translation X speed\n'
        '        -0.5,  # pelvis translation Y\n'
        '        vzinit - 2,  # pelvis translation Z\n'
        '        (\n'
        '            0.5 if somersault_direction == SomersaultDirection.FORWARD else -20\n'
        '        ),  # pelvis rotation X, somersault\n'
        '        0,  # pelvis rotation Y, tilt\n'
        '        0,  # pelvis rotation Z, twist\n'
        '        0,  # right upper arm rotation Z\n'
        '        0,  # right upper arm rotation Y\n'
        '        0,  # left upper arm rotation Z\n'
        '        0,  # left upper arm rotation Y\n'
        '    ]\n'
        '    x_bounds["qdot"].max[:, 0] = [\n'
        '        0.5,  # pelvis translation X\n'
        '        0.5,  # pelvis translation Y\n'
        '        vzinit + 2,  # pelvis translation Z\n'
        '        (\n'
        '            20 if somersault_direction == SomersaultDirection.FORWARD else -0.5\n'
        '        ),  # pelvis rotation X, somersault\n'
        '        0,  # pelvis rotation Y, tilt\n'
        '        0,  # pelvis rotation Z, twist\n'
        '        0,  # right upper arm rotation Z\n'
        '        0,  # right upper arm rotation Y\n'
        '        0,  # left upper arm rotation Z\n'
        '        0,  # left upper arm rotation Y\n'
        '    ]\n'
        '\n'
        '    # Intermediate bounds\n'
        '    x_bounds["qdot"].min[:, 1] = [\n'
        '        -10,\n'
        '        -10,\n'
        '        -100,\n'
        '        (0.5 if somersault_direction == SomersaultDirection.FORWARD else -20),\n'
        '        -100,\n'
        '        -100,\n'
        '        -100,\n'
        '        -100,\n'
        '        -100,\n'
        '        -100,\n'
        '    ]\n'
        '    x_bounds["qdot"].max[:, 1] = [\n'
        '        10,\n'
        '        10,\n'
        '        100,\n'
        '        (20 if somersault_direction == SomersaultDirection.FORWARD else -0.5),\n'
        '        100,\n'
        '        100,\n'
        '        100,\n'
        '        100,\n'
        '        100,\n'
        '        100,\n'
        '    ]\n'
        '\n'
        '    # Final bounds\n'
        '    x_bounds["qdot"].min[:, 2] = [\n'
        '        -10,\n'
        '        -10,\n'
        '        -100,\n'
        '        (0.5 if somersault_direction == SomersaultDirection.FORWARD else -20),\n'
        '        -100,\n'
        '        -100,\n'
        '        -100,\n'
        '        -100,\n'
        '        -100,\n'
        '        -100,\n'
        '    ]\n'
        '    x_bounds["qdot"].max[:, 2] = [\n'
        '        10,\n'
        '        10,\n'
        '        100,\n'
        '        (20 if somersault_direction == SomersaultDirection.FORWARD else -0.5),\n'
        '        100,\n'
        '        100,\n'
        '        100,\n'
        '        100,\n'
        '        100,\n'
        '        100,\n'
        '    ]\n'
        '\n'
        '    x_initial_guesses.add(\n'
        '        "qdot",\n'
        '        initial_guess=[0.0] * n_qdot,\n'
        '        interpolation=InterpolationType.CONSTANT,\n'
        '    )\n'
        '\n'
        '    u_bounds.add(\n'
        '        "tau",\n'
        '        min_bound=[tau_min] * n_tau,\n'
        '        max_bound=[tau_max] * n_tau,\n'
        '        interpolation=InterpolationType.CONSTANT,\n'
        '    )\n'
        '    u_initial_guesses.add(\n'
        '        "tau",\n'
        '        initial_guess=[tau_init] * n_tau,\n'
        '        interpolation=InterpolationType.CONSTANT,\n'
        '    )\n'
        '\n'
        '    mapping = BiMappingList()\n'
        '    mapping.add(\n'
        '        "tau",\n'
        '        to_second=[None, None, None, None, None, None, 0, 1, 2, 3],\n'
        '        to_first=[6, 7, 8, 9],\n'
        '    )\n'
        '\n'
        '    # Construct and return the optimal control program (OCP)\n'
        '    return OptimalControlProgram(\n'
        '        bio_model=bio_model,\n'
        '        n_shooting=n_shooting,\n'
        '        phase_time=phase_time,\n'
        '        dynamics=dynamics,\n'
        '        x_bounds=x_bounds,\n'
        '        u_bounds=u_bounds,\n'
        '        x_init=x_initial_guesses,\n'
        '        u_init=u_initial_guesses,\n'
        '        constraints=constraints,\n'
        '        objective_functions=objective_functions,\n'
        '        variable_mappings=mapping,\n'
        '        use_sx=False,\n'
        '        assume_phase_dynamics=True,\n'
        '    )\n'
        '\n'
        '\n'
        'def main():\n'
        '    """\n'
        '    If this file is run, then it will perform the optimization\n'
        '    """\n'
        '\n'
        '    # --- Prepare the ocp --- #\n'
        '    ocp = prepare_ocp()\n'
        '\n'
        '    solver = Solver.IPOPT()\n'
        '    # solver.set_maximum_iterations(0)\n'
        '    # --- Solve the ocp --- #\n'
        '    sol = ocp.solve(solver=solver)\n'
        '    # sol.graphs(show_bounds=True)\n'
        '    sol.animate()\n'
        '\n'
        '    out = sol.integrate(merge_phases=True)\n'
        '    state, time_vector = out._states["unscaled"], out._time_vector\n'
        '\n'
        '    save = {\n'
        '        "solution": sol,\n'
        '        "unscaled_state": state,\n'
        '        "time_vector": time_vector,\n'
        '    }\n'
        '\n'
        '    del sol.ocp\n'
        '    with open(f"somersault.pkl", "wb") as f:\n'
        '        pkl.dump(save, f)\n'
        '\n'
        '\n'
        'if __name__ == "__main__":\n'
        '    main()\n',
        mode: FileMode.append);
  }
}