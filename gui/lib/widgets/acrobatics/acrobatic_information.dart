import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/widgets/utils/positive_integer_text_field.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:bioptim_gui/models/api_config.dart';
import 'package:provider/provider.dart';

class AcrobaticInformation extends StatelessWidget {
  const AcrobaticInformation({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    Future<dynamic> updateField(String fieldName, String newValue) async {
      final url = Uri.parse('${APIConfig.url}/acrobatics/$fieldName');
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

    return Consumer<AcrobaticsData>(builder: (context, acrobaticsData, child) {
      return Column(
        children: [
          SizedBox(
            width: width,
            child: PositiveIntegerTextField(
              label: 'Number of somersaults *',
              controller: TextEditingController(
                  text: acrobaticsData.nbSomersaults.toString()),
              enabled: true,
              color: Colors.red,
              onSubmitted: (newValue) async {
                if (newValue.isNotEmpty) {
                  final response =
                      await updateField("nb_somersaults", newValue);

                  final updatedData =
                      AcrobaticsData.fromJson(json.decode(response.body));

                  // ignore: use_build_context_synchronously
                  Provider.of<AcrobaticsData>(context, listen: false)
                      .updateData(updatedData);
                }
              },
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              SizedBox(
                width: width / 2 - 6,
                child: TextField(
                  controller: TextEditingController(
                      text: acrobaticsData.finalTime.toString()),
                  decoration: const InputDecoration(
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.red),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.red),
                      ),
                      labelText: 'Final time *',
                      border: OutlineInputBorder()),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9\.]'))
                  ],
                  onSubmitted: (newValue) {
                    if (newValue.isNotEmpty) {
                      updateField("final_time", newValue);
                    }
                  },
                ),
              ),
              const SizedBox(width: 12),
              SizedBox(
                width: width / 2 - 6,
                child: TextField(
                  controller: TextEditingController(
                      text: acrobaticsData.finalTimeMargin.toString()),
                  decoration: const InputDecoration(
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.red),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.red),
                      ),
                      labelText: 'Final time margin *',
                      border: OutlineInputBorder()),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9\.]'))
                  ],
                  onSubmitted: (newValue) {
                    if (newValue.isNotEmpty) {
                      updateField("final_time_margin", newValue);
                    }
                  },
                ),
              ),
            ],
          )
        ],
      );
    });
  }
}
