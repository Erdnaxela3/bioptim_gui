import 'dart:convert';
import 'package:bioptim_gui/models/acrobatics_ocp_controllers.dart';
import 'package:bioptim_gui/screens/generate_code_page/acrobatics/acrobatics_header.dart';
import 'package:bioptim_gui/screens/generate_code_page/acrobatics/generate_somersaults.dart';
import 'package:bioptim_gui/models/api_config.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class LoadExisting extends StatefulWidget {
  const LoadExisting({super.key, this.columnWidth = 400.0});

  final double columnWidth;

  @override
  State<LoadExisting> createState() => _LoadExistingState();
}

class _LoadExistingState extends State<LoadExisting> {
  final _verticalScroll = ScrollController();

  @override
  void dispose() {
    _verticalScroll.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
  }

  Future<Map<String, dynamic>> _fetchData() async {
    final url = Uri.parse('${APIConfig.url}/acrobatics');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      if (kDebugMode) {
        print("Data fetch success.");
      }

      final data = json.decode(response.body);
      return data;
    } else {
      throw Exception("Fetch error");
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _fetchData(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        } else if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        } else {
          final data = snapshot.data;
          final controllers = AcrobaticsOCPControllers.instance;
          controllers.setNbSomersaults(data!["nb_somersaults"]);

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
                    _HeaderBuilder(width: widget.columnWidth, data: data),
                    const SizedBox(height: 12),
                    const Divider(),
                    const SizedBox(height: 12),
                    _PhaseBuilder(
                      width: widget.columnWidth,
                      data: data,
                    ),
                  ],
                ),
              ),
            ),
          );
        }
      },
    );
  }
}

class _HeaderBuilder extends StatelessWidget {
  const _HeaderBuilder({
    required this.width,
    required this.data,
  });

  final double width;
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: width,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 12),
            AcrobaticsHeaderBuilder(width: width, data: data),
          ],
        ),
      ),
    );
  }
}

class _PhaseBuilder extends StatefulWidget {
  const _PhaseBuilder({
    required this.width,
    required this.data,
  });

  final double width;
  final Map<String, dynamic> data;

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
              SomersaultGenerationMenu(
                width: widget.width,
                somersaultsInfo: widget.data["somersaults_info"],
              ),
            ]),
      ),
    );
  }
}
