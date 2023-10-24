import 'dart:convert';
import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/acrobatics_ocp_controllers.dart';
import 'package:bioptim_gui/screens/generate_code_page/acrobatics/acrobatics_header.dart';
import 'package:bioptim_gui/screens/generate_code_page/acrobatics/generate_somersaults.dart';
import 'package:bioptim_gui/models/api_config.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

class LoadExisting extends StatefulWidget {
  const LoadExisting({super.key, this.columnWidth = 400.0});

  final double columnWidth;

  @override
  State<LoadExisting> createState() => _LoadExistingState();
}

class _LoadExistingState extends State<LoadExisting> {
  final _verticalScroll = ScrollController();
  late Future<AcrobaticsData> _data;

  @override
  void dispose() {
    _verticalScroll.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _data = _fetchData();
  }

  Future<AcrobaticsData> _fetchData() async {
    final url = Uri.parse('${APIConfig.url}/acrobatics');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      if (kDebugMode) print("Data fetch success.");

      final data = json.decode(response.body);
      return AcrobaticsData.fromJson(data);
    } else {
      throw Exception("Fetch error");
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<AcrobaticsData>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        } else if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        } else {
          final data = snapshot.data!;
          final controllers = AcrobaticsOCPControllers.instance;
          controllers.setNbSomersaults(data.nbSomersaults);

          return ChangeNotifierProvider<AcrobaticsData>(
              create: (context) => data,
              child: Scaffold(
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
                        _PhaseBuilder(
                          width: widget.columnWidth,
                        ),
                      ],
                    ),
                  ),
                ),
              ));
        }
      },
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
  const _PhaseBuilder({
    required this.width,
  });

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
              ),
            ]),
      ),
    );
  }
}
