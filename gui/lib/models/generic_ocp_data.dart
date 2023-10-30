import 'package:bioptim_gui/models/generic_ocp_request_maker.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/models/optimal_control_program_controllers.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:bioptim_gui/models/variables.dart';
import 'package:flutter/material.dart';

class GenericOcpData extends ChangeNotifier implements OCPData {
  int _nbPhases;
  String _modelPath;

  @override
  List<GenericPhase> phaseInfo = [];

  GenericOcpData.fromJson(Map<String, dynamic> data)
      : _nbPhases = data["nb_phases"],
        _modelPath = data["model_path"],
        phaseInfo = (data["phases_info"] as List<dynamic>).map((phase) {
          return GenericPhase.fromJson(phase);
        }).toList();

  // getters/setters

  @override
  GenericOCPRequestMaker get requestMaker {
    notifyListeners();
    return GenericOCPRequestMaker();
  }

  @override
  int get nbPhases => _nbPhases;

  @override
  String get modelPath => _modelPath;

  set nbPhases(int value) {
    _nbPhases = value;
    notifyListeners();
  }

  ///
  /// update methods

  @override
  void updateField(String name, String value) {
    requestMaker.updateField(name, value);

    switch (name) {
      case "nb_phases":
        nbPhases = int.parse(value);
        break;
      case "model_path":
        _modelPath = value;
        break;
    }
    notifyListeners();
  }

  @override
  void updatePhaseField(int phaseIndex, String fieldName, String newValue) {
    requestMaker.updatePhaseField(phaseIndex, fieldName, newValue);

    // TODO fix double calls to notifyListeners for nb_shooting_points and duration
    switch (fieldName) {
      case "dynamics":
        phaseInfo[phaseIndex].dynamics = newValue;
        break;
      case "nb_shooting_points":
        phaseInfo[phaseIndex].nbShootingPoints = int.parse(newValue);
        break;
      case "duration":
        phaseInfo[phaseIndex].duration = double.parse(newValue);
        break;
    }
    notifyListeners();
  }

  void updateData(GenericOcpData newData) {
    nbPhases = newData.nbPhases;
    _modelPath = newData._modelPath;
    phaseInfo = List.from(newData.phaseInfo);

    notifyListeners();
  }

  @override
  void updatePhaseInfo(List<dynamic> newData) {
    final newPhases = (newData).map((p) => GenericPhase.fromJson(p)).toList();
    phaseInfo = newPhases;

    notifyListeners();
  }

  void updateBioModelPath(String newModelPath) {
    _modelPath = newModelPath;
    notifyListeners();
  }

  @override
  void updatePenalties(
      int phaseIndex, String penaltyType, List<Penalty> penalties) {
    if (penaltyType == "objective") {
      phaseInfo[phaseIndex].objectives = penalties as List<Objective>;
    } else {
      phaseInfo[phaseIndex].constraints = penalties as List<Constraint>;
    }
    notifyListeners();
  }

  @override
  void updatePenalty(
      int phaseIndex, String penaltyType, int penaltyIndex, Penalty penalty) {
    if (penaltyType == "objective") {
      phaseInfo[phaseIndex].objectives[penaltyIndex] = penalty as Objective;
    } else {
      phaseInfo[phaseIndex].constraints[penaltyIndex] = penalty as Constraint;
    }

    notifyListeners();
  }

  @override
  void notifyListeners() {
    OptimalControlProgramControllers.instance.notifyListeners();
    super.notifyListeners();
  }

  @override
  void updateObjectiveArgument(int phaseIndex, int objectiveIndex,
      String argumentName, String newValue) {}
}

class GenericPhase extends Phase {
  String dynamics;
  List<Variable> stateVariables;
  List<Variable> controlVariables;

  GenericPhase.fromJson(Map<String, dynamic> phaseData)
      : dynamics = phaseData["dynamics"],
        stateVariables =
            (phaseData["state_variables"] as List<dynamic>).map((variable) {
          return Variable.fromJson(variable);
        }).toList(),
        controlVariables =
            (phaseData["control_variables"] as List<dynamic>).map((variable) {
          return Variable.fromJson(variable);
        }).toList(),
        super.fromJson(phaseData);
}
