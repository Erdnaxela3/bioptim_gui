import 'dart:convert';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class OCPRequestMaker<T extends OCPData> {
  OCPRequestMaker({required this.prefix, required this.phaseInfoString});

  final String prefix;
  final String phaseInfoString;

  Future<http.Response> updateField(String fieldName, String newValue) async {
    final url = Uri.parse('${APIConfig.url}/$prefix/$fieldName');
    final body = json.encode({fieldName: newValue});
    final response =
        await http.put(url, body: body, headers: APIConfig.headers);

    if (response.statusCode != 200) {
      throw Exception('Failed to update $fieldName');
    }

    if (kDebugMode) print('$fieldName updated with value: $newValue');
    return response;
  }

  Future<void> updatePhaseField(
      int phaseIndex, String fieldName, String newValue) async {
    final url = Uri.parse(
        '${APIConfig.url}/$prefix/$phaseInfoString/$phaseIndex/$fieldName');
    final body = json.encode({fieldName: newValue});
    final response =
        await http.put(url, body: body, headers: APIConfig.headers);

    if (kDebugMode) {
      if (response.statusCode == 200) {
        print(
            '$phaseInfoString $phaseIndex, $fieldName updated with value: $newValue');
      } else {
        print('Failed to update $phaseInfoString $phaseIndex\'s $fieldName');
      }
    }
  }

  Future<http.Response> updateMaximizeMinimize(
      int phaseIndex, int objectiveIndex, String value) async {
    final url = Uri.parse(
        '${APIConfig.url}/$prefix/$phaseInfoString/$phaseIndex/objectives/$objectiveIndex/weight/$value');

    final response = await http.put(url);

    if (response.statusCode != 200) {
      throw Exception(
          'Error while changing $phaseInfoString $phaseIndex\'s objective $objectiveIndex to value $value');
    }

    if (kDebugMode) {
      print(
          '$phaseInfoString $phaseIndex\'s objective $objectiveIndex changed to value $value');
    }

    return response;
  }

  Future<http.Response> updateObjectiveField(
      int phaseIndex, int objectiveIndex, String value) async {
    final url = Uri.parse(
        '${APIConfig.url}/$prefix/$phaseInfoString/$phaseIndex/objectives/$objectiveIndex/objective_type');
    final body = json.encode({"objective_type": value});

    final response =
        await http.put(url, body: body, headers: APIConfig.headers);

    if (response.statusCode != 200) {
      throw Exception(
          'Error while changing $phaseInfoString $phaseIndex}\'s objective $objectiveIndex} to value $value');
    }

    if (kDebugMode) {
      print(
          '$phaseInfoString $phaseIndex\'s objective $objectiveIndex changed to value $value');
    }

    return response;
  }
}
