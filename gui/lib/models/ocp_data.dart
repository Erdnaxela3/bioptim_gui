import 'package:bioptim_gui/models/ocp_request_maker.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:flutter/material.dart';

abstract class OCPData<T extends Phase> with ChangeNotifier {
  OCPRequestMaker get requestMaker;
  List<T> get phaseInfo;
  int get nbPhases;
  String get modelPath;
  set modelPath(String value);

  void updatePhaseInfo(List<dynamic> newData);

  void updatePenalties(
      int somersaultIndex, String penaltyType, List<Penalty> penalties);

  void updatePenalty(int somersaultIndex, String penaltyType, int penaltyIndex,
      Penalty penalty);
}

abstract class Phase {
  late int nbShootingPoints;
  late double duration;
  late List<Objective> objectives;
  late List<Constraint> constraints;

  Phase.fromJson(Map<String, dynamic> phaseData)
      : nbShootingPoints = phaseData["nb_shooting_points"],
        duration = phaseData["duration"],
        objectives =
            (phaseData["objectives"] as List<dynamic>).map((objective) {
          return Objective.fromJson(objective);
        }).toList(),
        constraints =
            (phaseData["constraints"] as List<dynamic>).map((constraint) {
          return Constraint.fromJson(constraint);
        }).toList();
}
