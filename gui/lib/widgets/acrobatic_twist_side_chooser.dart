import 'package:bioptim_gui/widgets/custom_http_dropdown.dart';
import 'package:flutter/material.dart';

class AcrobaticTwistSideChooser extends StatelessWidget {
  const AcrobaticTwistSideChooser({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return CustomHttpDropdown(
      title: "Preferred twist side *",
      width: width,
      defaultValue: "Left",
      getEndpoint: "/acrobatics/preferred_twist_side",
      putEndpoint: "/acrobatics/preferred_twist_side",
      requestKey: "preferred_twist_side",
      color: Colors.red,
    );
  }
}
