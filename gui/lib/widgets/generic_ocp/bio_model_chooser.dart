import 'dart:convert';
import 'dart:io';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/bio_model.dart';
import 'package:bioptim_gui/models/generic_ocp_data.dart';
import 'package:bioptim_gui/widgets/utils/custom_dropdown_button.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

class BioModelChooser extends StatefulWidget {
  const BioModelChooser({super.key, required this.phaseIndex, this.width});

  final int phaseIndex;
  final double? width;
  @override
  BioModelChooserState createState() => BioModelChooserState();
}

class BioModelChooserState extends State<BioModelChooser> {
  @override
  Widget build(BuildContext context) {
    String modelPath = '';
    final String endpoint = '${APIConfig.url}/generic_ocp/model_path';

    Future<void> updateModelPath(String endpoint, String modelPathValue) async {
      final response = await http.put(
        Uri.parse(endpoint),
        headers: {"Content-Type": "application/json"},
        body: json.encode({'model_path': modelPathValue}),
      );

      if (response.statusCode == 200) {
        setState(() {
          modelPath = modelPathValue;
        });

        if (kDebugMode) {
          print('Model path set to : $modelPathValue');
        }
      }
    }

    return Consumer<GenericOcpData>(builder: (context, data, child) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const CustomDropdownButton<BioModel>(
            title: 'Dynamic model',
            value: BioModel.biorbd,
            items: BioModel.values,
            // onSelected: (value) => , TODO
            isExpanded: false,
          ),
          Padding(
            padding: const EdgeInsets.only(left: 8.0, top: 4.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                    child: Text(modelPath.isEmpty
                        ? 'Select the model file'
                        : File(data.modelPath).uri.pathSegments.last)),
                Tooltip(
                  message: 'Select model path',
                  child: IconButton(
                    onPressed: () async {
                      final results = await FilePicker.platform.pickFiles(
                        type: FileType.custom,
                        allowedExtensions: ["bioMod"],
                      );
                      if (results == null) return;

                      updateModelPath(endpoint, results.files.single.path!);
                    },
                    icon: const Icon(Icons.file_upload_outlined),
                  ),
                )
              ],
            ),
          )
        ],
      );
    });
  }
}
