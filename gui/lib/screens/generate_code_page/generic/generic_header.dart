import 'package:bioptim_gui/widgets/number_of_phases_chooser.dart';
import 'package:flutter/material.dart';

class GenericOCPHeaderBuilder extends StatelessWidget {
  const GenericOCPHeaderBuilder({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 12),
        NumberOfPhasesChooser(width: width),
      ],
    );
  }
}
