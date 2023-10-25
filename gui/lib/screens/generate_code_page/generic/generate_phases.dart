import 'package:bioptim_gui/models/generic_ocp_data.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:bioptim_gui/widgets/generic_ocp/bio_model_chooser.dart';
import 'package:bioptim_gui/widgets/generic_ocp/phase_information.dart';
import 'package:bioptim_gui/widgets/penalties/penalty_expander_generic.dart';
import 'package:bioptim_gui/widgets/utils/animated_expanding_widget.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class PhaseGenerationMenu extends StatelessWidget {
  const PhaseGenerationMenu({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return Consumer<GenericOcpData>(builder: (context, data, child) {
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          for (int i = 0; i < data.nbPhases; i++)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 36),
              child: SizedBox(width: width, child: _buildPhase(phaseIndex: i)),
            ),
        ],
      );
    });
  }

  Widget _buildPhase({required int phaseIndex}) {
    return Consumer<GenericOcpData>(builder: (context, data, child) {
      return AnimatedExpandingWidget(
        header: Center(
          child: Text(
            data.nbPhases > 1
                ? 'Information on phase ${phaseIndex + 1}'
                : 'Information on the phase',
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ),
        initialExpandedState: true,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 24),
            BioModelChooser(phaseIndex: phaseIndex),
            const SizedBox(height: 12),
            PhaseInformation(phaseIndex: phaseIndex, width: width),
            const SizedBox(height: 12),
            // DynamicsChooser(
            //   phaseIndex: phaseIndex,
            //   width: width,
            // ),
            // const SizedBox(height: 12),
            // const Divider(),
            // DecisionVariableExpander(
            //     from: DecisionVariableType.state,
            //     phaseIndex: phaseIndex,
            //     width: width),
            // const SizedBox(height: 12),
            // const Divider(),
            // DecisionVariableExpander(
            //   from: DecisionVariableType.control,
            //   phaseIndex: phaseIndex,
            //   width: width,
            // ),
            const SizedBox(height: 12),
            const Divider(),
            PenaltyExpander(
              penaltyType: Objective,
              phaseIndex: phaseIndex,
              width: width,
            ),
            const Divider(),
            PenaltyExpander(
              penaltyType: Constraint,
              phaseIndex: phaseIndex,
              width: width,
            ),
          ],
        ),
      );
    });
  }
}
