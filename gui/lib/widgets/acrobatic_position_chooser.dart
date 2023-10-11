import 'package:bioptim_gui/widgets/custom_http_dropdown.dart';
import 'package:flutter/material.dart';

class AcrobaticPositionChooser extends StatelessWidget {
  const AcrobaticPositionChooser({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return CustomHttpDropdown(
      title: "Jump position *",
      width: width,
      defaultValue: "Straight",
      getEndpoint: "/acrobatics/position",
      putEndpoint: "/acrobatics/position",
      requestKey: "position",
      color: Colors.red,
    );
  }
}
