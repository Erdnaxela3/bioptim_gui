import 'package:bioptim_gui/models/acrobatics_ocp_controllers.dart';
import 'package:bioptim_gui/widgets/utils/positive_integer_text_field.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:bioptim_gui/models/api_config.dart';

class SomersaultInformation extends StatelessWidget {
  const SomersaultInformation({
    super.key,
    required this.somersaultIndex,
    required this.width,
    required this.somersaultInfo,
  });

  final int somersaultIndex;
  final double width;
  final Map<String, dynamic> somersaultInfo;

  @override
  Widget build(BuildContext context) {
    Future<void> updateField(String fieldName, String newValue) async {
      final url = Uri.parse(
          '${APIConfig.url}/acrobatics/somersaults_info/$somersaultIndex/$fieldName');
      final headers = {'Content-Type': 'application/json'};
      final body = json.encode({fieldName: newValue});
      final response = await http.put(url, body: body, headers: headers);

      if (response.statusCode == 200) {
        if (kDebugMode) {
          print(
              'Somersault $somersaultIndex, $fieldName updated with value: $newValue');
        }
      } else {
        if (kDebugMode) {
          print('Failed to update somersault $somersaultIndex\'s $fieldName');
        }
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: width / 2 - 6,
          child: PositiveIntegerTextField(
            label: 'Number of half twists *',
            controller: TextEditingController(
                text: somersaultInfo["nb_half_twists"].toString()),
            color: Colors.red,
            onSubmitted: (newValue) {
              if (newValue.isNotEmpty) {
                updateField("nb_half_twists", newValue);
              }
            },
          ),
        ),
        const SizedBox(height: 24),
        Row(
          children: [
            SizedBox(
              width: width / 2 - 6,
              child: PositiveIntegerTextField(
                label: 'Number of shooting points',
                controller: TextEditingController(
                    text: somersaultInfo["nb_shooting_points"].toString()),
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
                    text: somersaultInfo["duration"].toString()),
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
        )
      ],
    );
  }
}
