import 'package:bioptim_gui/widgets/custom_http_dropdown.dart';
import 'package:flutter/material.dart';

class AcrobaticSportTypeChooser extends StatelessWidget {
  const AcrobaticSportTypeChooser({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return CustomHttpDropdown(
      title: "Sport type",
      width: width,
      defaultValue: "Trampoline",
      getEndpoint: "/acrobatics/sport_type",
      putEndpoint: "/acrobatics/sport_type",
      requestKey: "sport_type",
    );
  }
}
