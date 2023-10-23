import 'package:bioptim_gui/widgets/utils/extensions.dart';

class AcrobaticsData {
  int nbSomersaults;
  String modelPath;
  double finalTime;
  double finalTimeMargin;
  String position;
  String sportType;
  String preferredTwistSide;
  List<Somersault> somersaultInfo;

  AcrobaticsData.fromMap(Map<String, dynamic> data)
      : nbSomersaults = data["nb_somersaults"],
        modelPath = data["model_path"],
        finalTime = data["final_time"],
        finalTimeMargin = data["final_time_margin"],
        position = data["position"],
        sportType = data["sport_type"],
        preferredTwistSide = data["preferred_twist_side"],
        somersaultInfo =
            (data["somersaults_info"] as List<dynamic>).map((somersault) {
          return Somersault.fromMap(somersault);
        }).toList();
}

class Somersault {
  int nbShootingPoints;
  int nbHalfTwists;
  double duration;
  List<Objective> objectives;
  List<Constraint> constraints;

  Somersault.fromMap(Map<String, dynamic> somersaultData)
      : nbShootingPoints = somersaultData["nb_shooting_points"],
        nbHalfTwists = somersaultData["nb_half_twists"],
        duration = somersaultData["duration"],
        objectives =
            (somersaultData["objectives"] as List<dynamic>).map((objective) {
          return Objective.fromMap(objective);
        }).toList(),
        constraints =
            (somersaultData["constraints"] as List<dynamic>).map((constraint) {
          return Constraint.fromMap(constraint);
        }).toList();
}

abstract class Penalty {
  String penaltyType;
  String nodes;
  bool quadratic;
  bool expand;
  bool multiThread;
  bool derivative;
  dynamic target;
  String integrationRule;
  List<Argument> arguments;

  Penalty.fromMap(Map<String, dynamic> penaltyData)
      : penaltyType = penaltyData["penalty_type"],
        nodes = penaltyData["nodes"],
        quadratic = penaltyData["quadratic"],
        expand = penaltyData["expand"],
        multiThread = penaltyData["multi_thread"],
        derivative = penaltyData["derivative"],
        target = penaltyData["target"],
        integrationRule = penaltyData["integration_rule"],
        arguments = (penaltyData["arguments"] as List<dynamic>).map((argument) {
          return Argument.fromMap(argument);
        }).toList();

  String penaltyTypeToString() {
    return "";
  }
}

class Argument {
  String name;
  String type;
  String value;

  Argument.fromMap(Map<String, dynamic> argumentData)
      : name = argumentData["name"],
        type = argumentData["type"],
        value = argumentData["value"].toString();
}

class Objective extends Penalty {
  String objectiveType;
  double weight;

  Objective.fromMap(Map<String, dynamic> objectiveData)
      : objectiveType = objectiveData["objective_type"],
        weight = objectiveData["weight"],
        super.fromMap(objectiveData);

  @override
  String penaltyTypeToString() {
    return objectiveType.capitalize();
  }
}

class Constraint extends Penalty {
  Constraint.fromMap(Map<String, dynamic> constraintData)
      : super.fromMap(constraintData);

  @override
  String penaltyTypeToString() {
    return "Constraint";
  }
}
