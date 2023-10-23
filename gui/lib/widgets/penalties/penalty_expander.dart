import 'dart:convert';

import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/widgets/penalties/integration_rule_chooser.dart';
import 'package:bioptim_gui/widgets/penalties/maximize_minimize_radio.dart';
import 'package:bioptim_gui/widgets/penalties/nodes_chooser.dart';
import 'package:bioptim_gui/widgets/penalties/objective_type_radio.dart';
import 'package:bioptim_gui/widgets/penalties/penalty_chooser.dart';
import 'package:bioptim_gui/widgets/utils/animated_expanding_widget.dart';
import 'package:bioptim_gui/widgets/utils/remote_boolean_switch.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

class PenaltyExpander extends StatefulWidget {
  const PenaltyExpander({
    super.key,
    required this.penaltyType,
    required this.phaseIndex,
    required this.width,
    required this.penalties,
  });

  final Type penaltyType;
  final int phaseIndex;
  final double width;
  final List<Penalty> penalties;

  @override
  PenaltyExpanderState createState() => PenaltyExpanderState();
}

class PenaltyExpanderState extends State<PenaltyExpander> {
  List<Penalty> penalties = [];
  double width = 0;

  @override
  void initState() {
    penalties = widget.penalties;
    width = widget.width;
    super.initState();
  }

  String _penaltyTypeToString({required bool plural}) {
    switch (widget.penaltyType) {
      case Objective:
        return plural ? 'Objective functions' : 'Objective function';
      case Constraint:
        return plural ? 'Constraints' : 'Constraint';
      default:
        throw 'Wrong penalty type';
    }
  }

  String _penaltyTypeToEndpoint() {
    switch (widget.penaltyType) {
      case Objective:
        return 'objectives';
      case Constraint:
        return 'constraints';
      default:
        throw 'Wrong penalty type';
    }
  }

  Future<void> _createPenalties() async {
    final url = Uri.parse(
        '${APIConfig.url}/acrobatics/somersaults_info/${widget.phaseIndex}/${_penaltyTypeToEndpoint()}');

    final response = await http.post(url);

    if (response.statusCode == 200) {
      if (kDebugMode) print("Created a penalty");
    } else {
      throw Exception("Fetch error");
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedExpandingWidget(
      header: SizedBox(
        width: width,
        height: 50,
        child: Align(
          alignment: Alignment.centerLeft,
          child: Text(
            _penaltyTypeToString(plural: true),
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Align(
            alignment: Alignment.centerRight,
            child: _buildAddButton(
                _penaltyTypeToString(plural: false).toLowerCase()),
          ),
          const SizedBox(height: 24),
          ...penalties.asMap().keys.map((index) => Padding(
                padding: const EdgeInsets.only(bottom: 24.0),
                child: _PathTile(
                    key: ObjectKey(penalties[index]),
                    phaseIndex: widget.phaseIndex,
                    penaltyIndex: index,
                    width: width,
                    penaltyType: widget.penaltyType,
                    penalty: penalties[index]),
              )),
          const SizedBox(height: 26),
        ],
      ),
    );
  }

  Padding _buildAddButton(String name) {
    return Padding(
      padding: const EdgeInsets.only(right: 18.0, top: 12.0),
      child: InkWell(
        onTap: _createPenalties,
        child: Container(
            padding:
                const EdgeInsets.only(left: 12, right: 4, top: 2, bottom: 2),
            decoration: BoxDecoration(
                color: Colors.green, borderRadius: BorderRadius.circular(25)),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'New $name',
                  style: const TextStyle(color: Colors.white),
                ),
                const Icon(
                  Icons.add,
                  color: Colors.white,
                ),
              ],
            )),
      ),
    );
  }
}

class _PathTile extends StatelessWidget {
  const _PathTile({
    required super.key,
    required this.phaseIndex,
    required this.penaltyIndex,
    required this.penaltyType,
    required this.width,
    required this.penalty,
  });

  final int phaseIndex;
  final int penaltyIndex;
  final Type penaltyType;
  final double width;
  final Penalty penalty;

  String _penaltyTypeToEndpoint() {
    switch (penaltyType) {
      case Objective:
        return 'objectives';
      case Constraint:
        return 'constraints';
      default:
        throw 'Wrong penalty type';
    }
  }

  String _penaltyTypeToString({required bool plural}) {
    switch (penaltyType) {
      case Objective:
        return plural ? 'Objective functions' : 'Objective function';
      case Constraint:
        return plural ? 'Constraints' : 'Constraint';
      default:
        throw 'Wrong penalty type';
    }
  }

  Future<void> _deletePenalties() async {
    final url = Uri.parse(
        '${APIConfig.url}/acrobatics/somersaults_info/$phaseIndex/${_penaltyTypeToEndpoint()}/$penaltyIndex');

    final response = await http.delete(url);

    if (response.statusCode == 200) {
      if (kDebugMode) {
        print('Created a penalty (${_penaltyTypeToEndpoint()})');
      }
    } else {
      throw Exception("Fetch error");
    }
  }

  @override
  Widget build(BuildContext context) {
    final arguments = penalty.arguments;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          SizedBox(
            width: (penaltyType == Objective)
                ? width *
                    0.87 // can't get it smaller because of the dropdown's text
                : width,
            child: PenaltyChooser(
              title:
                  '${_penaltyTypeToString(plural: false)} ${penaltyIndex + 1} (${penalty.penaltyTypeToString()})',
              width: width,
              defaultValue: penalty.penaltyType,
              getEndpoint:
                  '/acrobatics/somersaults_info/$phaseIndex/${_penaltyTypeToEndpoint()}/$penaltyIndex',
              putEndpoint:
                  '/acrobatics/somersaults_info/$phaseIndex/${_penaltyTypeToEndpoint()}/$penaltyIndex/penalty_type',
            ),
          ),
          if (penaltyType == Objective)
            SizedBox(
              width: width * 0.13,
              child: ObjectiveTypeRadio(
                value: (penalty as Objective).objectiveType,
                phaseIndex: phaseIndex,
                objectiveIndex: penaltyIndex,
              ),
            ),
        ]),
        const SizedBox(height: 12),
        ...arguments.map((argument) => Padding(
              padding: const EdgeInsets.only(bottom: 12.0),
              child: Row(
                children: [
                  SizedBox(
                    width: width,
                    child: TextField(
                      controller: TextEditingController(text: argument.value),
                      decoration: InputDecoration(
                          label: Text(
                              'Argument: ${argument.name} (${argument.type})'),
                          border: const OutlineInputBorder()),
                      // inputFormatters: [FilteringTextInputFormatter.allow()],
                    ),
                  ),
                ],
              ),
            )),
        Row(
          children: [
            SizedBox(
                width: (penaltyType == Objective) ? width / 2 - 3 : width,
                child: NodesChooser(
                  width: width,
                  putEndpoint: (penaltyType == Objective)
                      ? '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/nodes'
                      : '/acrobatics/somersaults_info/$phaseIndex/constraints/$penaltyIndex/nodes',
                )),
            if (penaltyType == Objective)
              SizedBox(
                width: width / 4 - 3,
                child: TextField(
                  controller: TextEditingController(
                    text: (penalty as Objective).weight.abs().toString(),
                  ),
                  decoration: const InputDecoration(
                      label: Text('Weight'), border: OutlineInputBorder()),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9\.]')),
                  ],
                  onSubmitted: (value) => {
                    http.put(
                      Uri.parse(
                          '${APIConfig.url}/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/weight'),
                      headers: {'Content-Type': 'application/json'},
                      body: json.encode({"weight": double.parse(value)}),
                    )
                  },
                ),
              ),
            if (penaltyType == Objective)
              SizedBox(
                  width: width / 4 + 6,
                  child: MinMaxRadio(
                    weightValue: (penalty as Objective).weight,
                    phaseIndex: phaseIndex,
                    objectiveIndex: penaltyIndex,
                  )),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: TextField(
                  controller:
                      TextEditingController(text: penalty.target.toString()),
                  decoration: const InputDecoration(
                      label: Text('Target'), border: OutlineInputBorder()),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9\.,]'))
                  ]),
            ),
          ],
        ),
        // Mayer objectives don't have integration_rule
        if (penaltyType != Objective ||
            (penalty as Objective).objectiveType != "mayer")
          const SizedBox(height: 12),
        if (penaltyType != Objective ||
            (penalty as Objective).objectiveType != "mayer")
          Row(
            children: [
              SizedBox(
                width: width,
                child: IntegrationRuleChooser(
                  width: width,
                  putEndpoint: (penaltyType == Objective)
                      ? '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/integration_rule'
                      : '/acrobatics/somersaults_info/$phaseIndex/constraints/$penaltyIndex/integration_rule',
                ),
              ),
            ],
          ),
        const SizedBox(height: 12),
        Row(
          children: [
            RemoteBooleanSwitch(
                endpoint:
                    '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/quadratic',
                defaultValue: true,
                leftText: "Quadratic",
                width: width / 2 - 6,
                requestKey: "quadratic"),
            const SizedBox(width: 12),
            RemoteBooleanSwitch(
                endpoint:
                    '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/expand',
                defaultValue: true,
                leftText: "Expand",
                width: width / 2 - 6,
                requestKey: "expand"),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            RemoteBooleanSwitch(
                endpoint:
                    '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/multi_thread',
                defaultValue: false,
                leftText: "MultiThread",
                width: width / 2 - 6,
                requestKey: "multi_thread"),
            const SizedBox(width: 12),
            RemoteBooleanSwitch(
                endpoint:
                    '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/derivative',
                defaultValue: false,
                leftText: "Derivative",
                width: width / 2 - 6,
                requestKey: "derivative"),
          ],
        ),
        Align(
          alignment: Alignment.centerRight,
          child: InkWell(
            onTap: () {
              _deletePenalties();
            },
            borderRadius: BorderRadius.circular(25),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Remove ${penalty is Objective ? 'objective' : 'constraint'}',
                    style: const TextStyle(color: Colors.red),
                  ),
                  const SizedBox(width: 8),
                  const Icon(
                    Icons.delete,
                    color: Colors.red,
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 14),
      ],
    );
  }
}
