import 'package:bioptim_gui/models/generic_ocp_data.dart';
import 'package:bioptim_gui/models/generic_ocp_request_maker.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/screens/generate_code_page/generic/generate_phases.dart';
import 'package:bioptim_gui/screens/generate_code_page/generic/generic_header.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class GenericMenu extends StatefulWidget {
  const GenericMenu({super.key, this.columnWidth = 400.0});

  final double columnWidth;

  @override
  State<GenericMenu> createState() => _GenericMenuState();
}

class _GenericMenuState extends State<GenericMenu> {
  final _verticalScroll = ScrollController();
  late Future<GenericOcpData> _data;

  @override
  void dispose() {
    _verticalScroll.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _data = GenericOCPRequestMaker().fetchData();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<GenericOcpData>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        } else if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        } else {
          final data = snapshot.data!;

          return Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              ChangeNotifierProvider<GenericOcpData>(
                create: (context) => data,
                child: _HeaderBuilder(width: widget.columnWidth),
              ),
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 12),
              ChangeNotifierProvider<OCPData>(
                create: (context) => data,
                child: _PhaseBuilder(
                  width: widget.columnWidth,
                ),
              ),
            ],
          );
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
            GenericOCPHeaderBuilder(width: width),
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
              PhaseGenerationMenu(
                width: widget.width,
              ),
            ]),
      ),
    );
  }
}
