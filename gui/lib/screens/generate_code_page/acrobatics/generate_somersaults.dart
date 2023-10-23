import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/acrobatics_ocp_controllers.dart';
import 'package:bioptim_gui/widgets/acrobatics/somersault_informations.dart';
import 'package:bioptim_gui/widgets/penalties/test.dart';
import 'package:bioptim_gui/widgets/utils/animated_expanding_widget.dart';
import 'package:flutter/material.dart';

class SomersaultGenerationMenu extends StatelessWidget {
  const SomersaultGenerationMenu({
    super.key,
    required this.width,
    required this.somersaultsInfo,
  });

  final double width;
  final List<Somersault> somersaultsInfo;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (int i = 0; i < somersaultsInfo.length; i++)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 36),
            child: SizedBox(
                width: width,
                child: _buildSomersault(
                    somersaultIndex: i,
                    width: width,
                    somersaultInfo: somersaultsInfo[i])),
          ),
      ],
    );
  }

  Widget _buildSomersault({
    required int somersaultIndex,
    required double width,
    required Somersault somersaultInfo,
  }) {
    final controllers = AcrobaticsOCPControllers.instance;

    return AnimatedExpandingWidget(
      header: Center(
        child: Text(
          controllers.nbSomersaults > 1
              ? 'Information on somersault ${somersaultIndex + 1}'
              : 'Information on the somersault',
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
      initialExpandedState: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 24),
          SomersaultInformation(
            somersaultIndex: somersaultIndex,
            width: width,
            somersaultInfo: somersaultInfo,
          ),
          const SizedBox(height: 12),
          const Divider(),
          PenaltyExpander(
            penaltyType: Objective,
            phaseIndex: somersaultIndex,
            width: width,
            penalties: somersaultsInfo[somersaultIndex].objectives,
          ),
          const Divider(),
          PenaltyExpander(
            penaltyType: Constraint,
            phaseIndex: somersaultIndex,
            width: width,
            penalties: somersaultsInfo[somersaultIndex].constraints,
          ),
        ],
      ),
    );
  }
}
