import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_bio_model_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_information.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_position_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_sport_type_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_twist_side_chooser.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class LoadExisting extends StatefulWidget {
  const LoadExisting({
    super.key,
    required this.width,
  });

  final double width;

  @override
  LoadExistingState createState() => LoadExistingState();
}

class LoadExistingState extends State<LoadExisting> {
  final Map<String, TextEditingController> acrobaticsControllers = {};

  Future<void> fetchData() async {
    final url = Uri.parse('${APIConfig.url}/acrobatics/');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        data.forEach((fieldName, value) {
          acrobaticsControllers[fieldName] =
              TextEditingController(text: value.toString());
        });
      });
    } else {
      throw Exception('Failed to load data');
    }
  }

  Future<void> updateField(String fieldName, String newValue) async {
    final url = Uri.parse('${APIConfig.url}/acrobatics/$fieldName');
    final headers = {'Content-Type': 'application/json'};
    final body = json.encode({fieldName: newValue});
    final response = await http.put(url, body: body, headers: headers);

    if (response.statusCode == 200) {
      if (kDebugMode) {
        print('$fieldName updated with value: $newValue');
      }
    } else {
      if (kDebugMode) {
        print('Failed to update $fieldName');
      }
    }
  }

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  @override
  void dispose() {
    // Dispose the controllers to prevent memory leaks.
    acrobaticsControllers.values.forEach((controller) => controller.dispose());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(children: [
        AcrobaticSportTypeChooser(width: widget.width),
        const SizedBox(height: 12),
        AcrobaticBioModelChooser(width: widget.width),
        const SizedBox(height: 12),
        AcrobaticInformation(width: widget.width),
        const SizedBox(height: 12),
        Row(
          children: [
            SizedBox(
              width: widget.width / 2 - 6,
              child: AcrobaticTwistSideChooser(width: widget.width),
            ),
            const SizedBox(width: 12),
            SizedBox(
              width: widget.width / 2 - 6,
              child: AcrobaticPositionChooser(width: widget.width),
            ),
          ],
        ),
        Column(
          children: acrobaticsControllers.keys.map((fieldName) {
            final controller = acrobaticsControllers[fieldName];

            return Column(
              children: [
                ListTile(
                  title: Text(fieldName),
                  subtitle: TextField(
                    controller: controller,
                    decoration: const InputDecoration(
                      labelText: 'New Value',
                    ),
                    onSubmitted: (newValue) {
                      if (newValue.isNotEmpty) {
                        controller?.text = newValue;
                        updateField(fieldName, newValue);
                      }
                    },
                  ),
                ),
                const Divider(),
              ],
            );
          }).toList(),
        ),
      ]),
    );
  }
}
