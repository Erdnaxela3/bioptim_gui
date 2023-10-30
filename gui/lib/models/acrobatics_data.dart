import 'package:bioptim_gui/models/acrobatics_controllers.dart';
import 'package:bioptim_gui/models/acrobatics_request_maker.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:flutter/foundation.dart';

class AcrobaticsData extends ChangeNotifier implements OCPData {
  int _nbSomersaults;
  String _modelPath;
  double finalTime;
  double finalTimeMargin;
  String position;
  String sportType;
  String preferredTwistSide;

  List<Somersault> somersaultInfo = [];

  AcrobaticsData.fromJson(Map<String, dynamic> data)
      : _nbSomersaults = data["nb_somersaults"],
        _modelPath = data["model_path"],
        finalTime = data["final_time"],
        finalTimeMargin = data["final_time_margin"],
        position = data["position"],
        sportType = data["sport_type"],
        preferredTwistSide = data["preferred_twist_side"],
        somersaultInfo =
            (data["somersaults_info"] as List<dynamic>).map((somersault) {
          return Somersault.fromJson(somersault);
        }).toList();

  ///
  /// Getters Setters

  @override
  AcrobaticsRequestMaker get requestMaker {
    return AcrobaticsRequestMaker();
  }

  @override
  List<Phase> get phaseInfo => somersaultInfo;

  @override
  String get modelPath => _modelPath;

  @override
  set modelPath(String value) {
    _modelPath = value;
    notifyListeners();
  }

  @override
  int get nbPhases => _nbSomersaults;

  int get nbSomersaults => _nbSomersaults;
  set nbSomersaults(int value) {
    _nbSomersaults = value;
    notifyListeners();
  }

  ///
  /// Update methods

  void updateData(AcrobaticsData newData) {
    nbSomersaults = newData.nbSomersaults;
    _modelPath = newData._modelPath;
    finalTime = newData.finalTime;
    finalTimeMargin = newData.finalTimeMargin;
    position = newData.position;
    sportType = newData.sportType;
    preferredTwistSide = newData.preferredTwistSide;
    somersaultInfo = List.from(newData.somersaultInfo);

    notifyListeners();
  }

  @override
  void updatePenalties(
      int somersaultIndex, String penaltyType, List<Penalty> penalties) {
    if (penaltyType == "objective") {
      somersaultInfo[somersaultIndex].objectives = penalties as List<Objective>;
    } else {
      somersaultInfo[somersaultIndex].constraints =
          penalties as List<Constraint>;
    }
    notifyListeners();
  }

  @override
  void updatePenalty(int somersaultIndex, String penaltyType, int penaltyIndex,
      Penalty penalty) {
    if (penaltyType == "objective") {
      somersaultInfo[somersaultIndex].objectives[penaltyIndex] =
          penalty as Objective;
    } else {
      somersaultInfo[somersaultIndex].constraints[penaltyIndex] =
          penalty as Constraint;
    }

    notifyListeners();
  }

  @override
  void updatePhaseInfo(List newData) {
    final newPhases = (newData).map((p) => Somersault.fromJson(p)).toList();
    somersaultInfo = newPhases;

    notifyListeners();
  }

  @override
  void notifyListeners() {
    super.notifyListeners();
    AcrobaticsControllers.instance.notifyListeners();
  }
}

class Somersault extends Phase {
  int nbHalfTwists;

  Somersault.fromJson(Map<String, dynamic> somersaultData)
      : nbHalfTwists = somersaultData["nb_half_twists"],
        super.fromJson(somersaultData);
}
