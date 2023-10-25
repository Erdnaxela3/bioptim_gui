import 'dart:convert';

import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

class MinMaxRadio extends StatefulWidget {
  const MinMaxRadio({
    super.key,
    required this.weightValue,
    required this.phaseIndex,
    required this.objectiveIndex,
  });

  final double weightValue;
  final int phaseIndex;
  final int objectiveIndex;

  @override
  MinMaxRadioState createState() => MinMaxRadioState();
}

class MinMaxRadioState extends State<MinMaxRadio> {
  String _selectedValue = '';

  @override
  void initState() {
    super.initState();
    _selectedValue = widget.weightValue > 0 ? "minimize" : "maximize";
  }

  Future<http.Response> _updateValue(String value) async {
    final url = Uri.parse(
        '${APIConfig.url}/acrobatics/somersaults_info/${widget.phaseIndex}/objectives/${widget.objectiveIndex}/weight/$value');

    final response = await http.put(url);

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
    return Consumer<AcrobaticsData>(builder: (context, acrobaticsData, child) {
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
                value: "maximize",
                groupValue: _selectedValue,
                onChanged: (newValue) {
                  updatePenalty(newValue!);
                },
              ),
              const Text("Maximize"), // German mark M
            ],
          ),
          Row(
            children: [
              Radio<String>(
                value: "minimize",
                groupValue: _selectedValue,
                onChanged: (newValue) {
                  updatePenalty(newValue!);
                },
              ),
              const Text("Minimize"), // Laplace L
            ],
          ),
        ],
      );
    });
  }
}
