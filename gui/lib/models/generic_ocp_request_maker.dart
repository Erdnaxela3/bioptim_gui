import 'dart:convert';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/generic_ocp_data.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class GenericOCPRequestMaker {
  static Future<GenericOcpData> fetchData() async {
    final url = Uri.parse('${APIConfig.url}/generic_ocp');
    final response = await http.get(url);

    if (response.statusCode != 200) throw Exception("Fetch error");

    if (kDebugMode) print("Data fetch success.");

    final data = json.decode(response.body);
    return GenericOcpData.fromJson(data);
  }

  static Future<http.Response> updateField(
      String fieldName, String newValue) async {
    final url = Uri.parse('${APIConfig.url}/generic_ocp/$fieldName');
    final headers = {'Content-Type': 'application/json'};
    final body = json.encode({fieldName: newValue});
    final response = await http.put(url, body: body, headers: headers);

    if (response.statusCode != 200) {
      throw Exception('Failed to update $fieldName');
    }

    if (kDebugMode) print('$fieldName updated with value: $newValue');
    return response;
  }

  static Future<void> updatePhaseField(
      int phaseIndex, String fieldName, String newValue) async {
    final url = Uri.parse(
        '${APIConfig.url}/generic_ocp/phases_info/$phaseIndex/$fieldName');
    final headers = {'Content-Type': 'application/json'};
    final body = json.encode({fieldName: newValue});
    final response = await http.put(url, body: body, headers: headers);

    if (kDebugMode) {
      if (response.statusCode == 200) {
        print('Phase $phaseIndex, $fieldName updated with value: $newValue');
      } else {
        print('Failed to update phase $phaseIndex\'s $fieldName');
      }
    }
  }
}
