import 'dart:convert';
import 'package:bioptim_gui/models/acrobatics_ocp_controllers.dart';
import 'package:bioptim_gui/models/optimal_control_program_controllers.dart';
import 'package:bioptim_gui/models/optimal_control_program_type.dart';
import 'package:bioptim_gui/models/python_interface.dart';
import 'package:bioptim_gui/screens/generate_code_page/acrobatics/acrobatics_header.dart';
import 'package:bioptim_gui/screens/generate_code_page/acrobatics/generate_somersaults.dart';
import 'package:bioptim_gui/screens/generate_code_page/generic/generate_phases.dart';
import 'package:bioptim_gui/screens/generate_code_page/generic/generic_header.dart';
import 'package:bioptim_gui/widgets/console_out.dart';
import 'package:bioptim_gui/widgets/optimal_control_program_type_chooser.dart';
import 'package:bioptim_gui/models/api_config.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:path/path.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class LoadExisting extends StatefulWidget {
  const LoadExisting({super.key, this.columnWidth = 400.0});

  final double columnWidth;

  @override
  State<LoadExisting> createState() => _LoadExistingState();
}

class _LoadExistingState extends State<LoadExisting> {
  final _verticalScroll = ScrollController();

//
// function that calls http request to localhost:8000/acribatics and return the response json

  @override
  void dispose() {
    _verticalScroll.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _fetchData();
    AcrobaticsOCPControllers.instance.registerToStatusChanged(forceRedraw);
  }

  Future<void> _fetchData() async {
    final url = Uri.parse('${APIConfig.url}/acrobatics');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final responseData = json.decode(response.body);
    }
  }

  void forceRedraw() {
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: RawScrollbar(
        controller: _verticalScroll,
        thumbVisibility: true,
        thumbColor: Theme.of(context).colorScheme.secondary,
        thickness: 8,
        radius: const Radius.circular(25),
        child: SingleChildScrollView(
          controller: _verticalScroll,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 12),
              _HeaderBuilder(width: widget.columnWidth),
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 12),
              _PhaseBuilder(width: widget.columnWidth),
            ],
          ),
        ),
      ),
    );
  }
}

class _HeaderBuilder extends StatelessWidget {
  const _HeaderBuilder({
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: width,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 12),
            AcrobaticsHeaderBuilder(width: width),
          ],
        ),
      ),
    );
  }
}

class _PhaseBuilder extends StatefulWidget {
  const _PhaseBuilder({required this.width});

  final double width;

  @override
  State<_PhaseBuilder> createState() => _PhaseBuilderState();
}

class _PhaseBuilderState extends State<_PhaseBuilder> {
  final _horizontalScroll = ScrollController();

  @override
  void dispose() {
    _horizontalScroll.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controllers = OptimalControlProgramControllers.instance;
    return RawScrollbar(
      controller: _horizontalScroll,
      thumbVisibility: true,
      thumbColor: Theme.of(context).colorScheme.secondary,
      thickness: 8,
      radius: const Radius.circular(25),
      child: SingleChildScrollView(
        controller: _horizontalScroll,
        scrollDirection: Axis.horizontal,
        child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SomersaultGenerationMenu(width: widget.width),
            ]),
      ),
    );
  }
}
