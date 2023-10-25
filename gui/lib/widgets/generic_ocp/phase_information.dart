import 'dart:convert';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/generic_ocp_data.dart';
import 'package:bioptim_gui/widgets/utils/positive_integer_text_field.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

class PhaseInformation extends StatelessWidget {
  const PhaseInformation({
    super.key,
    required this.phaseIndex,
    required this.width,
  });

  final int phaseIndex;
  final double width;

  @override
  Widget build(BuildContext context) {
    Future<void> updateField(String fieldName, String newValue) async {
      final url = Uri.parse(
          '${APIConfig.url}/generic_ocp/phases_info/$phaseIndex/$fieldName');
      final headers = {'Content-Type': 'application/json'};
      final body = json.encode({fieldName: newValue});
      final response = await http.put(url, body: body, headers: headers);

      if (response.statusCode == 200) {
        if (kDebugMode) {
          print('Phase $phaseIndex, $fieldName updated with value: $newValue');
        }
      } else {
        if (kDebugMode) {
          print('Failed to update phase $phaseIndex\'s $fieldName');
        }
      }
    }

    return Consumer<GenericOcpData>(builder: (context, data, child) {
      return Row(
        children: [
          SizedBox(
            width: width / 2 - 6,
            child: PositiveIntegerTextField(
              label: 'Number of shooting points',
              controller: TextEditingController(
                  text: data.phaseInfo[phaseIndex].nbShootingPoints.toString()),
              onSubmitted: (newValue) {
                if (newValue.isNotEmpty) {
                  updateField("nb_shooting_points", newValue);
                }
              },
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: TextEditingController(
                  text: data.phaseInfo[phaseIndex].duration.toString()),
              decoration: const InputDecoration(
                  labelText: 'Phase time (s)', border: OutlineInputBorder()),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[0-9\.]'))
              ],
              onSubmitted: (newValue) {
                if (newValue.isNotEmpty) {
                  updateField("duration", newValue);
                }
              },
            ),
          ),
        ],
      );
    });
  }
}
