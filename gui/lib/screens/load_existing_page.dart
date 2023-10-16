import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class LoadExisting extends StatefulWidget {
  const LoadExisting({super.key});

  @override
  LoadExistingState createState() => LoadExistingState();
}

class LoadExistingState extends State<LoadExisting> {
  final Map<String, TextEditingController> acrobaticsControllers = {};

  Future<void> fetchData() async {
    final url = Uri.parse('http://localhost:8000/acrobatics/');
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
    final url = Uri.parse('http://localhost:8000/acrobatics/$fieldName');
    final body = json.encode({fieldName: newValue});
    final response = await http
        .put(url, body: body, headers: {'Content-Type': 'application/json'});

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
      child: Column(
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
    );
  }
}
