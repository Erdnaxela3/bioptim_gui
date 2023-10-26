import 'package:bioptim_gui/models/optimal_control_program_type.dart';
import 'package:bioptim_gui/models/optimal_control_program.dart';

///
/// This class mimics the strcture of the [OptimalControlProgram] class but in
/// a UI perspective. It creates all the required Controllers as well as it gets
/// or updates the values.
class OptimalControlProgramControllers {
  static final OptimalControlProgramControllers _instance =
      OptimalControlProgramControllers._internal();
  static OptimalControlProgramControllers get instance => _instance;
  OptimalControlProgramControllers._internal();

  final _ocp = OptimalControlProgram();

  ///
  /// All methods related to controlling the ocp type
  OptimalControlProgramType get ocpType => _ocp.generic.ocpType;
  void setOcpType(OptimalControlProgramType value) {
    _ocp.generic.ocpType = value;
  }
}
