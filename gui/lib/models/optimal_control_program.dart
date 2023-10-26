import 'dart:io';

import 'package:bioptim_gui/models/generic_ocp_config.dart';

import 'dart:convert';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:http/http.dart' as http;

///
/// This is the main class holder for the model. Nevertheless, this class should
/// not be instantiated manually but only by the [OptimalControlProgramController].
/// Similarly, it should not be directly access (except from the said calss).
class OptimalControlProgram {
  ///
  /// Constructor

  OptimalControlProgram();

  ///
  /// Setters and Getters

  bool _hasPendingChangesToBeExported = true;
  void notifyThatModelHasChanged() => _hasPendingChangesToBeExported = true;
  bool get mustExport => _hasPendingChangesToBeExported;

  GenericOptimalControlProgram generic = GenericOptimalControlProgram();

  static Future<void> exportScript(String path) async {
    final file = File(path);

    Future<String> getGeneratedContent() async {
      final url = Uri.parse('${APIConfig.url}/generic_ocp/generate_code');
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return response.body;
      } else {
        throw Exception("Code generation failed API level");
      }
    }

    final generatedContent = json.decode(await getGeneratedContent());

    file.writeAsStringSync(generatedContent);
  }
}
