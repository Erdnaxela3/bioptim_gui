import 'package:bioptim_gui/widgets/utils/custom_http_dropdown.dart';
import 'package:bioptim_gui/widgets/utils/extensions.dart';
import 'package:flutter/material.dart';

class PenaltyChooser extends StatelessWidget {
  const PenaltyChooser({
    super.key,
    required this.width,
    required this.title,
    required this.getEndpoint,
    required this.putEndpoint,
    required this.defaultValue,
  });

  final String title;
  final double width;
  final String defaultValue;
  final String getEndpoint;
  final String putEndpoint;

  @override
  Widget build(BuildContext context) {
    return CustomHttpDropdown(
      title: title,
      width: width,
      defaultValue:
          defaultValue.replaceAll("_", " ").toLowerCase().capitalize(),
      getEndpoint: getEndpoint,
      putEndpoint: putEndpoint,
      requestKey: "penalty_type",
      customStringFormatting: (s) => s.replaceAll(" ", "_").toUpperCase(),
    );
  }
}
