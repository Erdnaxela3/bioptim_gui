import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:bioptim_gui/models/variables.dart';
import 'package:flutter/foundation.dart';

class GenericOcpData extends ChangeNotifier implements OCPData {
  int _nbPhases;
  String modelPath;
  List<Phase> phaseInfo = [];

  GenericOcpData.fromJson(Map<String, dynamic> data)
      : _nbPhases = data["nb_phases"],
        modelPath = data["model_path"],
        phaseInfo = (data["phases_info"] as List<dynamic>).map((phase) {
          return Phase.fromJson(phase);
        }).toList();

  int get nbPhases => _nbPhases;
  set nbPhases(int value) {
    _nbPhases = value;
    notifyListeners();
  }

  void updateData(GenericOcpData newData) {
    nbPhases = newData.nbPhases;
    modelPath = newData.modelPath;
    phaseInfo = List.from(newData.phaseInfo);

    notifyListeners();
  }

  void updatePhaseInfo(List<Phase> newData) {
    phaseInfo = newData;

    notifyListeners();
  }

  void updateBioModelPath(String newModelPath) {
    modelPath = newModelPath;
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
}

class Phase {
  int nbShootingPoints;
  double duration;
  String dynamics;
  List<Variable> stateVariables;
  List<Variable> controlVariables;
  List<Objective> objectives;
  List<Constraint> constraints;

  Phase.fromJson(Map<String, dynamic> phaseData)
      : nbShootingPoints = phaseData["nb_shooting_points"],
        duration = phaseData["duration"],
        dynamics = phaseData["dynamics"],
        stateVariables =
            (phaseData["state_variables"] as List<dynamic>).map((variable) {
          return Variable.fromJson(variable);
        }).toList(),
        controlVariables =
            (phaseData["control_variables"] as List<dynamic>).map((variable) {
          return Variable.fromJson(variable);
        }).toList(),
        objectives =
            (phaseData["objectives"] as List<dynamic>).map((objective) {
          return Objective.fromJson(objective);
        }).toList(),
        constraints =
            (phaseData["constraints"] as List<dynamic>).map((constraint) {
          return Constraint.fromJson(constraint);
        }).toList();
}
