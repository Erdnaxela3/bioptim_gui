import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/acrobatics_request_maker.dart';
import 'package:bioptim_gui/widgets/utils/positive_float_text_field.dart';
import 'package:bioptim_gui/widgets/utils/positive_integer_text_field.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class SomersaultInformation extends StatelessWidget {
  const SomersaultInformation({
    super.key,
    required this.somersaultIndex,
    required this.width,
  });

  final int somersaultIndex;
  final double width;

  @override
  Widget build(BuildContext context) {
    return Consumer<AcrobaticsData>(builder: (context, acrobaticsData, child) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: width / 2 - 6,
            child: PositiveIntegerTextField(
              label: 'Number of half twists *',
              value: acrobaticsData.somersaultInfo[somersaultIndex].nbHalfTwists
                  .toString(),
              onSubmitted: (newValue) {
                if (newValue.isNotEmpty) {
                  AcrobaticsRequestMaker.updateSomersaultField(
                      somersaultIndex, "nb_half_twists", newValue);
                }
              },
            ),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              SizedBox(
                width: width / 2 - 6,
                child: PositiveIntegerTextField(
                  label: 'Number of shooting points',
                  value: acrobaticsData
                      .somersaultInfo[somersaultIndex].nbShootingPoints
                      .toString(),
                  onSubmitted: (newValue) {
                    if (newValue.isNotEmpty) {
                      AcrobaticsRequestMaker.updateSomersaultField(
                          somersaultIndex, "nb_shooting_points", newValue);
                    }
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: PositiveFloatTextField(
                  value: acrobaticsData.somersaultInfo[somersaultIndex].duration
                      .toString(),
                  label: 'Phase time (s)',
                  onSubmitted: (newValue) {
                    if (newValue.isNotEmpty) {
                      AcrobaticsRequestMaker.updateSomersaultField(
                          somersaultIndex, "duration", newValue);
                    }
                  },
                ),
              ),
            ],
          )
        ],
      );
    });
  }
}
