import 'dart:convert';
import 'dart:io';
import 'package:bioptim_gui/models/api_config.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class AcrobaticBioModelChooser extends StatefulWidget {
  const AcrobaticBioModelChooser({
    super.key,
    this.width,
    this.defaultValue = '',
  });

  final double? width;
  final String defaultValue;

  @override
  AcrobaticBioModelChooserState createState() =>
      AcrobaticBioModelChooserState();
}

class AcrobaticBioModelChooserState extends State<AcrobaticBioModelChooser> {
  String modelPath = '';

  @override
  void initState() {
    modelPath = widget.defaultValue;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    final String endpoint = '${APIConfig.url}/acrobatics/model_path';

    return SizedBox(
      width: widget.width,
      child: TextField(
        decoration: InputDecoration(
          labelText: "Model path *",
          enabledBorder: const OutlineInputBorder(
            borderSide: BorderSide(color: Colors.red),
          ),
          focusedBorder: const OutlineInputBorder(
            borderSide: BorderSide(color: Colors.red),
          ),
          suffixIcon: IconButton(
            icon: const Icon(Icons.file_upload_outlined),
            onPressed: () async {
              final results = await FilePicker.platform.pickFiles(
                type: FileType.custom,
                allowedExtensions: ["bioMod"],
              );
              if (results == null) return;

              _updateModelPath(endpoint, results.files.single.path!);
            },
          ),
        ),
        autofocus: true,
        controller: TextEditingController(
          text: modelPath.isEmpty
              ? 'Select the model file'
              : File(modelPath).uri.pathSegments.last,
        ),
        readOnly: true,
        style: const TextStyle(
          color: Colors.black,
        ),
      ),
    );
  }

  Future<void> _updateModelPath(String endpoint, String modelPathValue) async {
    final response = await http.put(
      Uri.parse(endpoint),
      headers: {"Content-Type": "application/json"},
      body: json.encode({'model_path': modelPathValue}),
    );

    if (response.statusCode == 200) {
      setState(() {
        modelPath = modelPathValue;
      });
    }
  }
}
