import 'dart:convert';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/generic_ocp_data.dart';
import 'package:bioptim_gui/widgets/utils/positive_integer_text_field.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

class NumberOfPhasesChooser extends StatelessWidget {
  const NumberOfPhasesChooser({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    Future<dynamic> updateField(String fieldName, String newValue) async {
      final url = Uri.parse('${APIConfig.url}/generic_ocp/$fieldName');
      final headers = {'Content-Type': 'application/json'};
      final body = json.encode({fieldName: newValue});
      final response = await http.put(url, body: body, headers: headers);

      if (response.statusCode == 200) {
        if (kDebugMode) {
          print('$fieldName updated with value: $newValue');
          return response;
        }
      } else {
        if (kDebugMode) {
          print('Failed to update $fieldName');
          throw Exception('Failed to update $fieldName');
        }
      }
    }

    return Consumer<GenericOcpData>(builder: (context, data, child) {
      return SizedBox(
        width: width * 1 / 2 - 6,
        child: PositiveIntegerTextField(
          label: 'Number of phases',
          controller: TextEditingController(text: data.nbPhases.toString()),
          enabled: true,
          onSubmitted: (newValue) async {
            if (newValue.isNotEmpty) {
              final response = await updateField("nb_phases", newValue);

              final updatedData =
                  GenericOcpData.fromJson(json.decode(response.body));

              // ignore: use_build_context_synchronously
              Provider.of<GenericOcpData>(context, listen: false)
                  .updateData(updatedData);
            }
          },
        ),
      );
    });
  }
}
