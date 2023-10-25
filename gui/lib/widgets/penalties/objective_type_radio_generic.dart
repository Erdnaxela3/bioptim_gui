import 'dart:convert';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/generic_ocp_data.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

class ObjectiveTypeRadio extends StatefulWidget {
  const ObjectiveTypeRadio({
    super.key,
    required this.value,
    required this.phaseIndex,
    required this.objectiveIndex,
  });

  final String value;
  final int phaseIndex;
  final int objectiveIndex;

  @override
  ObjectiveTypeRadioState createState() => ObjectiveTypeRadioState();
}

class ObjectiveTypeRadioState extends State<ObjectiveTypeRadio> {
  String _selectedValue = '';

  @override
  void initState() {
    super.initState();
    _selectedValue = widget.value;
  }

  Future<http.Response> _updateValue(String value) async {
    final url = Uri.parse(
        '${APIConfig.url}/generic_ocp/phases_info/${widget.phaseIndex}/objectives/${widget.objectiveIndex}/objective_type');
    final headers = {'Content-Type': 'application/json'};
    final body = json.encode({"objective_type": value});

    final response = await http.put(url, headers: headers, body: body);

    if (response.statusCode == 200) {
      setState(() {
        _selectedValue = value;
      });

      if (kDebugMode) {
        print(
            'somersault ${widget.phaseIndex}\'s objective ${widget.objectiveIndex} changed to value $value');
      }

      return response;
    } else {
      throw Exception(
          'Error while changing somersault ${widget.phaseIndex}\'s objective ${widget.objectiveIndex} to value $value');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<GenericOcpData>(builder: (context, acrobaticsData, child) {
      void updatePenalty(newValue) async {
        final response = await _updateValue(newValue!);
        final Penalty newObjective = Objective.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
        acrobaticsData.updatePenalty(widget.phaseIndex, "objective",
            widget.objectiveIndex, newObjective);
      }

      return Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Radio<String>(
                value: "mayer",
                groupValue: _selectedValue,
                onChanged: (newValue) async {
                  updatePenalty(newValue);
                },
              ),
              const Text("\u2133"), // German mark M
            ],
          ),
          Row(
            children: [
              Radio<String>(
                value: "lagrange",
                groupValue: _selectedValue,
                onChanged: (newValue) async {
                  updatePenalty(newValue);
                },
              ),
              const Text("\u2112"), // Laplace L
            ],
          ),
        ],
      );
    });
  }
}
