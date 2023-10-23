import 'package:bioptim_gui/models/acrobatics_ocp.dart';
import 'package:bioptim_gui/models/optimal_control_program.dart';
import 'package:flutter/material.dart';

///
/// This class mimics the strcture of the [OptimalControlProgram] class but in
/// a UI perspective. It creates all the required Controllers as well as it gets
/// or updates the values.
class AcrobaticsOCPControllers {
  static final AcrobaticsOCPControllers _instance =
      AcrobaticsOCPControllers._internal();
  static AcrobaticsOCPControllers get instance => _instance;
  AcrobaticsOCPControllers._internal();

  Function(String path) get exportScript => _ocp.exportScript;
  bool get mustExport => _ocp.mustExport;

  final _ocp = AcrobaticsOCPProgram();
  // This is to keep track of how many controllers we have because we don't
  // delete them if we reduce _nbSomersaults

  ///
  /// This callback can be used so the UI is updated on any change
  void _notifyListeners() {
    if (_hasChanged != null) _hasChanged!();
    _ocp.notifyThatModelHasChanged();
  }

  void Function()? _hasChanged;
  void registerToStatusChanged(Function() callback) {
    _hasChanged = callback;
    _notifyListeners();
  }

  ///
  /// All methods related to controlling the number of somersaults
  late final nbSomersaultsController = TextEditingController(text: '1');

  int get nbSomersaults => int.parse(nbSomersaultsController.text);

  void setNbSomersaults(int value) {
    nbSomersaultsController.text = value.toString();
    _notifyListeners();
  }
}
