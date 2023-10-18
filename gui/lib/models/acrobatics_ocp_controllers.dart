import 'dart:math';

import 'package:bioptim_gui/models/acrobatics_ocp.dart';
import 'package:bioptim_gui/models/optimal_control_program.dart';
import 'package:bioptim_gui/models/optimal_control_program_controllers.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:flutter/material.dart';

///
/// This class mimics the strcture of the [OptimalControlProgram] class but in
/// a UI perspective. It creates all the required Controllers as well as it gets
/// or updates the values.
class AcrobaticsOCPControllers {
  static final AcrobaticsOCPControllers _instance =
      AcrobaticsOCPControllers._internal();
  static AcrobaticsOCPControllers get instance => _instance;
  AcrobaticsOCPControllers._internal() {
    _updateAllControllers();
  }

  Function(String path) get exportScript => _ocp.exportScript;
  bool get mustExport => _ocp.mustExport;

  final _ocp = AcrobaticsOCPProgram();
  // This is to keep track of how many controllers we have because we don't
  // delete them if we reduce _nbSomersaults
  int _nbSomersaultsMax = 1;

  ///
  /// This callback can be used so the UI is updated on any change
  void _notifyListeners() {
    if (_hasChanged != null) _hasChanged!();
    _ocp.notifyThatModelHasChanged();
  }

  void Function()? _hasChanged;
  void registerToStatusChanged(Function() callback) {
    _hasChanged = callback;
    _updateAllControllers();
    _notifyListeners();
  }

  ///
  /// All methods related to controlling the number of somersaults
  late final nbSomersaultsController = TextEditingController(text: '1')
    ..addListener(_nbSomersaultsControllerListener);

  int get nbSomersaults => _ocp.generic.nbSomersaults;

  void setNbSomersaults(int value) {
    _ocp.generic.nbSomersaults = value;
    _ocp.updateSomersaults();
    _nbSomersaultsMax = max(nbSomersaults, _nbSomersaultsMax);

    if (nbSomersaultsController.text != nbSomersaults.toString()) {
      nbSomersaultsController.text = nbSomersaults.toString();
    }
    // Wait for one frame so the the UI is updated
    WidgetsBinding.instance.addPostFrameCallback((timeStamp) {
      _updateAllControllers();
      _notifyListeners();
    });
  }

  void _nbSomersaultsControllerListener() {
    final tp = int.tryParse(nbSomersaultsController.text);
    if (tp == null || tp < 1 || tp == nbSomersaults) return;
    setNbSomersaults(tp);
  }

  ///
  /// All the methods related to the final time margin
  late final finalTimeMarginController = TextEditingController(text: '0.1');

  double get finalTimeMargin => _ocp.generic.finalTimeMargin;

  void setFinalTimeMargin(double value) {
    _ocp.generic.finalTimeMargin = value;
    finalTimeMarginController.text = value.toString();
  }

  ///
  /// All the methods related to the final time
  late final finalTimeController = TextEditingController(text: '1.0')
    ..addListener(_finalTimeControllerListener);

  double get finalTime => _ocp.generic.finalTime;

  void setFinalTime(double value) {
    _ocp.generic.finalTime = value;
    finalTimeController.text = value.toString();
  }

  void _finalTimeControllerListener() {
    final tp = double.tryParse(finalTimeController.text);
    if (tp == null) return;
    setFinalTime(tp);
  }

  ///
  /// All methods related to the number of shooting points
  final nbShootingPointsControllers = <TextEditingController>[];
  int getNbShootingPoints({required int somersaultIndex}) =>
      _ocp.somersaults[somersaultIndex].nbShootingPoints;
  void setNbShootingPoints(int value, {required int somersaultIndex}) {
    if (value == _ocp.somersaults[somersaultIndex].nbShootingPoints) return;

    _ocp.somersaults[somersaultIndex].nbShootingPoints = value;
    _notifyListeners();
  }

  List<String> get _nbShootingPointsInitialValues => [
        for (int i = 0; i < nbSomersaults; i++)
          getNbShootingPoints(somersaultIndex: i).toString()
      ];
  void _nbShootingPointsListener(String value,
          {required int somersaultIndex}) =>
      setNbShootingPoints(int.tryParse(value) ?? -1,
          somersaultIndex: somersaultIndex);

  ///
  /// All methods related to the number of half twists
  final nbHalfTwistsControllers = <TextEditingController>[];
  int getNbHalfTwists({required int somersaultIndex}) =>
      _ocp.somersaults[somersaultIndex].nbHalfTwists;
  void setNbHalfTwists(int value, {required int somersaultIndex}) {
    if (value == _ocp.somersaults[somersaultIndex].nbHalfTwists) return;

    _ocp.somersaults[somersaultIndex].nbHalfTwists = value;
    _notifyListeners();
  }

  List<String> get _nbHalfTwistsInitialValues => [
        for (int i = 0; i < nbSomersaults; i++)
          getNbHalfTwists(somersaultIndex: i).toString()
      ];
  void _nbHalfTwistsListener(String value, {required int somersaultIndex}) =>
      setNbHalfTwists(int.tryParse(value) ?? -1,
          somersaultIndex: somersaultIndex);

  ///
  /// All methods related to the somersault duration
  final somersaultDurationControllers = <TextEditingController>[];
  double getSomersaultDuration({required int somersaultIndex}) =>
      _ocp.somersaults[somersaultIndex].duration;
  void setSomersaultDuration(double value, {required int somersaultIndex}) {
    if (value == _ocp.somersaults[somersaultIndex].duration) return;

    _ocp.somersaults[somersaultIndex].duration = value;
    _notifyListeners();
  }

  List<String> get _somersaultDurationInitialValues => [
        for (int i = 0; i < nbSomersaults; i++)
          getSomersaultDuration(somersaultIndex: i).toString()
      ];

  void _somersaultDurationListener(String value,
          {required int somersaultIndex}) =>
      setSomersaultDuration(double.tryParse(value) ?? -1.0,
          somersaultIndex: somersaultIndex);

  ///
  /// Here are some generic methods for penalties (declared later)
  void _createPenalty(
    Penalty penalty, {
    required List<_PenaltyTextEditingControllers> controllers,
    required List<Penalty> penalties,
  }) {
    penalties.add(penalty);
    controllers.add(_PenaltyTextEditingControllers(penalties.last));
    controllers.last._updateWeight();
    controllers.last._updateTarget();
    controllers.last._updateArguments();
    _notifyListeners();
  }

  void _updatePenalty(
    Penalty penalty, {
    required List<_PenaltyTextEditingControllers> controllers,
    required List<Penalty> penalties,
    required int penaltyIndex,
  }) {
    penalties[penaltyIndex] = penalty;
    controllers[penaltyIndex]._penalty = penalty;
    controllers[penaltyIndex]._updateWeight();
    controllers[penaltyIndex]._updateTarget();
    controllers[penaltyIndex]._updateArguments();
    _notifyListeners();
  }

  void _removePenalty({
    required List<_PenaltyTextEditingControllers> controllers,
    required List<Penalty> penalties,
    required int penaltyIndex,
  }) {
    penalties.removeAt(penaltyIndex);
    controllers[penaltyIndex].dispose();
    controllers.removeAt(penaltyIndex);
    _notifyListeners();
  }

  ///
  /// Here are the objective function methods
  final List<List<_PenaltyTextEditingControllers>> _objectiveControllers = [];

  List<TextEditingController> getObjectiveArgumentsControllers(
          {required int penaltyIndex, required int somersaultIndex}) =>
      _objectiveControllers[somersaultIndex][penaltyIndex].arguments;

  PenaltyInterface objectives({required int somersaultIndex}) =>
      PenaltyInterface(
          create: () => _createObjective(somersaultIndex: somersaultIndex),
          fetch: ({required penaltyIndex}) =>
              _getObjectives(somersaultIndex: somersaultIndex)[penaltyIndex],
          fetchAll: () => _getObjectives(somersaultIndex: somersaultIndex),
          update: (penalty, {required penaltyIndex}) => _updateObjective(
              penalty,
              penaltyIndex: penaltyIndex,
              somersaultIndex: somersaultIndex),
          remove: ({required penaltyIndex}) => _removeObjective(
              penaltyIndex: penaltyIndex, somersaultIndex: somersaultIndex),
          weightController: ({required penaltyIndex}) =>
              _objectiveControllers[somersaultIndex][penaltyIndex].weight,
          targetController: ({required penaltyIndex}) =>
              _objectiveControllers[somersaultIndex][penaltyIndex].target,
          argumentController: (
                  {required penaltyIndex, required argumentIndex}) =>
              _objectiveControllers[somersaultIndex][penaltyIndex]
                  .arguments[argumentIndex]);

  List<Penalty> _getObjectives({required int somersaultIndex}) =>
      _ocp.somersaults[somersaultIndex].objectives;

  void _createObjective({required int somersaultIndex}) =>
      _createPenalty(Objective.generic(),
          controllers: _objectiveControllers[somersaultIndex],
          penalties: _ocp.somersaults[somersaultIndex].objectives);

  void _updateObjective(Penalty penalty,
          {required int penaltyIndex, required int somersaultIndex}) =>
      _updatePenalty(penalty,
          controllers: _objectiveControllers[somersaultIndex],
          penalties: _ocp.somersaults[somersaultIndex].objectives,
          penaltyIndex: penaltyIndex);

  void _removeObjective(
          {required int penaltyIndex, required int somersaultIndex}) =>
      _removePenalty(
          controllers: _objectiveControllers[somersaultIndex],
          penalties: _ocp.somersaults[somersaultIndex].objectives,
          penaltyIndex: penaltyIndex);

  ///
  /// Here are all the constraint methods
  final List<List<_PenaltyTextEditingControllers>> _constraintControllers = [];

  List<TextEditingController> getConstraintArgumentsControllers(
          {required int penaltyIndex, required int somersaultIndex}) =>
      _constraintControllers[somersaultIndex][penaltyIndex].arguments;

  PenaltyInterface constraints({required int somersaultIndex}) =>
      PenaltyInterface(
          create: () => _createConstraint(somersaultIndex: somersaultIndex),
          fetch: ({required penaltyIndex}) =>
              _getConstraints(somersaultIndex: somersaultIndex)[penaltyIndex],
          fetchAll: () => _getConstraints(somersaultIndex: somersaultIndex),
          update: (penalty, {required penaltyIndex}) => _updateConstraint(
              penalty,
              penaltyIndex: penaltyIndex,
              somersaultIndex: somersaultIndex),
          remove: ({required penaltyIndex}) => _removeConstraint(
              penaltyIndex: penaltyIndex, somersaultIndex: somersaultIndex),
          targetController: ({required penaltyIndex}) =>
              _constraintControllers[somersaultIndex][penaltyIndex].target,
          argumentController: (
                  {required penaltyIndex, required argumentIndex}) =>
              _constraintControllers[somersaultIndex][penaltyIndex]
                  .arguments[argumentIndex]);

  List<Penalty> _getConstraints({required int somersaultIndex}) =>
      _ocp.somersaults[somersaultIndex].constraints;

  void _createConstraint({required int somersaultIndex}) =>
      _createPenalty(Constraint.generic(),
          controllers: _constraintControllers[somersaultIndex],
          penalties: _ocp.somersaults[somersaultIndex].constraints);

  void _updateConstraint(Penalty penalty,
          {required int penaltyIndex, required int somersaultIndex}) =>
      _updatePenalty(penalty,
          controllers: _constraintControllers[somersaultIndex],
          penalties: _ocp.somersaults[somersaultIndex].constraints,
          penaltyIndex: penaltyIndex);

  void _removeConstraint(
          {required int penaltyIndex, required int somersaultIndex}) =>
      _removePenalty(
          controllers: _constraintControllers[somersaultIndex],
          penalties: _ocp.somersaults[somersaultIndex].constraints,
          penaltyIndex: penaltyIndex);

  ///
  /// Here are the internal methods that ensures all the controllers are sane
  void _updateAllControllers() {
    _updateTextControllers(
      nbShootingPointsControllers,
      initialValue: _nbShootingPointsInitialValues,
      onChanged: _nbShootingPointsListener,
    );
    _updateTextControllers(
      nbHalfTwistsControllers,
      initialValue: _nbHalfTwistsInitialValues,
      onChanged: _nbHalfTwistsListener,
    );
    _updateTextControllers(
      somersaultDurationControllers,
      initialValue: _somersaultDurationInitialValues,
      onChanged: _somersaultDurationListener,
    );

    _updatePenaltyControllers(_objectiveControllers);
    _updatePenaltyControllers(_constraintControllers);
  }

  void _updateTextControllers(List<TextEditingController> controllers,
      {required List<String> initialValue,
      required Function(String value, {required int somersaultIndex})
          onChanged}) {
    if (controllers.length < nbSomersaults) {
      for (int i = controllers.length; i < nbSomersaults; i++) {
        controllers.add(TextEditingController());
        controllers[i].text = initialValue[i];
        controllers[i].addListener(
            () => onChanged(controllers[i].text, somersaultIndex: i));
      }
    } else if (controllers.length > nbSomersaults) {
      for (int i = controllers.length - 1; i >= nbSomersaults; i--) {
        controllers[i].dispose();
        controllers.removeAt(i);
      }
    } else {
      // Do not change anything if we already have the right number of somersaults
    }
  }

  void _updatePenaltyControllers(
      List<List<_PenaltyTextEditingControllers>> controllers) {
    if (controllers.length < nbSomersaults) {
      // For each of the new somersaults, declare all the required variables
      for (int i = controllers.length; i < nbSomersaults; i++) {
        controllers.add([]);

        // adding default penalties, that will be added for each somersault
        if (_objectiveControllers[i].isEmpty) {
          _createPenalty(Objective.acrobaticGenericLagrangeMinimizeControls(),
              controllers: _objectiveControllers[i],
              penalties: _ocp.somersaults[i].objectives);

          _createPenalty(
              Objective.acrobaticGenericMayerMinimizeTime(
                  minBound:
                      double.parse(somersaultDurationControllers[i].text) -
                          finalTimeMargin,
                  maxBound:
                      double.parse(somersaultDurationControllers[i].text) +
                          finalTimeMargin),
              controllers: _objectiveControllers[i],
              penalties: _ocp.somersaults[i].objectives);
        }
      }
    } else if (controllers.length > nbSomersaults) {
      for (int i = controllers.length - 1; i >= nbSomersaults; i--) {
        for (final controller in controllers[i]) {
          controller.dispose();
        }
        controllers.removeAt(i);
      }
    } else {
      // Do not change anything if we already have the right number of somersaults
    }
  }

  void dispose() {
    nbSomersaultsController.dispose();
    for (final controller in nbShootingPointsControllers) {
      controller.dispose();
    }
    nbShootingPointsControllers.clear();
    for (final controller in somersaultDurationControllers) {
      controller.dispose();
    }
    somersaultDurationControllers.clear();
  }
}

class _PenaltyTextEditingControllers {
  final weight = TextEditingController(text: '1.0');
  final target = TextEditingController(text: 'None');
  Penalty _penalty;
  final arguments = <TextEditingController>[];

  _PenaltyTextEditingControllers(this._penalty) {
    weight.addListener(() {
      if (_penalty.runtimeType != Objective) return;
      final newWeight = double.tryParse(weight.text);
      if (newWeight == null || newWeight == (_penalty as Objective).weight) {
        return;
      }

      (_penalty as Objective).weight = newWeight;
      AcrobaticsOCPControllers.instance._notifyListeners();
    });

    target.addListener(() {
      final newTarget = target.text;
      if (newTarget == _penalty.target) {
        return;
      }

      _penalty.target = newTarget;
      AcrobaticsOCPControllers.instance._notifyListeners();
    });

    _updateArguments();
  }

  void _updateWeight() {
    if (_penalty.runtimeType != Objective) return;
    weight.text = (_penalty as Objective).weight.toString();
  }

  void _updateTarget() {
    target.text = _penalty.target.toString();
  }

  void _updateArguments() {
    _disposeArguments();
    final names = _penalty.arguments.keys.toList();
    for (int i = 0; i < _penalty.arguments.length; i++) {
      final name = names[i];

      arguments.add(TextEditingController(
          text: _penalty.arguments[name]?.toString() ?? ''));
      arguments[i].addListener(() {
        final value = arguments[i].text;
        if (value == _penalty.arguments[name].toString()) return;
        _penalty.arguments[name] = value;
        AcrobaticsOCPControllers.instance._notifyListeners();
      });
    }
  }

  void _disposeArguments() {
    for (final controller in arguments) {
      controller.dispose();
    }
    arguments.clear();
  }

  void dispose() {
    weight.dispose();
    target.dispose();
    _disposeArguments();
  }
}
