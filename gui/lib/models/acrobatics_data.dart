import 'package:bioptim_gui/models/penalty.dart';
import 'package:flutter/foundation.dart';

class AcrobaticsData extends ChangeNotifier {
  int _nbSomersaults;
  String modelPath;
  double finalTime;
  double finalTimeMargin;
  String position;
  String sportType;
  String preferredTwistSide;
  List<Somersault> somersaultInfo = [];

  AcrobaticsData.fromJson(Map<String, dynamic> data)
      : _nbSomersaults = data["nb_somersaults"],
        modelPath = data["model_path"],
        finalTime = data["final_time"],
        finalTimeMargin = data["final_time_margin"],
        position = data["position"],
        sportType = data["sport_type"],
        preferredTwistSide = data["preferred_twist_side"],
        somersaultInfo =
            (data["somersaults_info"] as List<dynamic>).map((somersault) {
          return Somersault.fromJson(somersault);
        }).toList();

  int get nbSomersaults => _nbSomersaults;
  set nbSomersaults(int value) {
    _nbSomersaults = value;
    notifyListeners();
  }

  void updateData(AcrobaticsData newData) {
    nbSomersaults = newData.nbSomersaults;
    modelPath = newData.modelPath;
    finalTime = newData.finalTime;
    finalTimeMargin = newData.finalTimeMargin;
    position = newData.position;
    sportType = newData.sportType;
    preferredTwistSide = newData.preferredTwistSide;
    somersaultInfo = List.from(newData.somersaultInfo);

    notifyListeners();
  }

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
}

class Somersault {
  int nbShootingPoints;
  int nbHalfTwists;
  double duration;
  List<Objective> objectives;
  List<Constraint> constraints;

  Somersault.fromJson(Map<String, dynamic> somersaultData)
      : nbShootingPoints = somersaultData["nb_shooting_points"],
        nbHalfTwists = somersaultData["nb_half_twists"],
        duration = somersaultData["duration"],
        objectives =
            (somersaultData["objectives"] as List<dynamic>).map((objective) {
          return Objective.fromJson(objective);
        }).toList(),
        constraints =
            (somersaultData["constraints"] as List<dynamic>).map((constraint) {
          return Constraint.fromJson(constraint);
        }).toList();
}
