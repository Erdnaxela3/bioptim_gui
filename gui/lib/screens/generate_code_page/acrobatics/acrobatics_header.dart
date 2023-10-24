import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_bio_model_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_information.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_position_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_sport_type_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_twist_side_chooser.dart';
import 'package:bioptim_gui/widgets/utils/extensions.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class AcrobaticsHeaderBuilder extends StatelessWidget {
  const AcrobaticsHeaderBuilder({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return Consumer<AcrobaticsData>(builder: (context, acrobaticsData, child) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AcrobaticSportTypeChooser(
              width: width,
              defaultValue: acrobaticsData.sportType.capitalize()),
          const SizedBox(height: 12),
          AcrobaticBioModelChooser(
            width: width,
            defaultValue: acrobaticsData.modelPath,
          ),
          const SizedBox(height: 12),
          AcrobaticInformation(
            width: width,
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              SizedBox(
                  width: width / 2 - 6,
                  child: AcrobaticTwistSideChooser(
                    width: width,
                    defaultValue:
                        acrobaticsData.preferredTwistSide.capitalize(),
                  )),
              const SizedBox(width: 12),
              SizedBox(
                  width: width / 2 - 6,
                  child: AcrobaticPositionChooser(
                    width: width,
                    defaultValue: acrobaticsData.position.capitalize(),
                  )),
            ],
          ),
        ],
      );
    });
  }
}
