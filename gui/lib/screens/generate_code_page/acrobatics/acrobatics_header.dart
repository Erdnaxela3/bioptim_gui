import 'package:bioptim_gui/widgets/acrobatics/acrobatic_bio_model_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_information.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_position_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_sport_type_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_twist_side_chooser.dart';
import 'package:flutter/material.dart';

class AcrobaticsHeaderBuilder extends StatelessWidget {
  const AcrobaticsHeaderBuilder({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        AcrobaticSportTypeChooser(width: width),
        const SizedBox(height: 12),
        AcrobaticBioModelChooser(width: width),
        const SizedBox(height: 12),
        AcrobaticInformation(width: width),
        const SizedBox(height: 12),
        Row(
          children: [
            SizedBox(
              width: width / 2 - 6,
              child: AcrobaticTwistSideChooser(width: width),
            ),
            const SizedBox(width: 12),
            SizedBox(
              width: width / 2 - 6,
              child: AcrobaticPositionChooser(width: width),
            ),
          ],
        ),
      ],
    );
  }
}
