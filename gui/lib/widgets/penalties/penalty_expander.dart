import 'dart:convert';

import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/optimal_control_program_controllers.dart';
import 'package:bioptim_gui/models/optimal_control_program_type.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:bioptim_gui/widgets/penalties/integration_rule_chooser.dart';
import 'package:bioptim_gui/widgets/penalties/maximize_minimize_radio.dart';
import 'package:bioptim_gui/widgets/penalties/nodes_chooser.dart';
import 'package:bioptim_gui/widgets/penalties/objective_type_radio.dart';
import 'package:bioptim_gui/widgets/penalties/penalty_chooser.dart';
import 'package:bioptim_gui/widgets/utils/animated_expanding_widget.dart';
import 'package:bioptim_gui/widgets/utils/extensions.dart';
import 'package:bioptim_gui/widgets/utils/remote_boolean_switch.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

class PenaltyExpander extends StatefulWidget {
  const PenaltyExpander({
    super.key,
    required this.penaltyType,
    required this.phaseIndex,
    required this.width,
  });

  final Type penaltyType;
  final int phaseIndex;
  final double width;

  @override
  PenaltyExpanderState createState() => PenaltyExpanderState();
}

class PenaltyExpanderState extends State<PenaltyExpander> {
  double width = 0;

  final String endpointPrefix = OptimalControlProgramControllers
              .instance.ocpType ==
          OptimalControlProgramType.ocp
      ? '/generic_ocp/phases_info' // TODO change when api for generic is implemented
      : '/acrobatics/somersaults_info';

  @override
  void initState() {
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

  String _penaltyTypeToEndpoint({required bool plural}) {
    switch (widget.penaltyType) {
      case Objective:
        return plural ? 'objectives' : 'objective';
      case Constraint:
        return plural ? 'constraints' : 'constraint';
      default:
        throw 'Wrong penalty type';
    }
  }

  Future<http.Response> _createPenalties() async {
    final url = Uri.parse(
        '${APIConfig.url}$endpointPrefix/${widget.phaseIndex}/${_penaltyTypeToEndpoint(plural: true)}');

    final response = await http.post(url);

    if (response.statusCode == 200) {
      if (kDebugMode) print("Created a penalty");

      return response;
    } else {
      throw Exception("Fetch error");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AcrobaticsData>(builder: (context, acrobaticsData, child) {
      final penalties = (widget.penaltyType == Constraint)
          ? acrobaticsData.somersaultInfo[widget.phaseIndex].constraints
          : acrobaticsData.somersaultInfo[widget.phaseIndex].objectives;

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
                  penalty: penalties[index],
                  endpointPrefix: endpointPrefix,
                ))),
            const SizedBox(height: 26),
          ],
        ),
      );
    });
  }

  Consumer<AcrobaticsData> _buildAddButton(String name) {
    return Consumer<AcrobaticsData>(builder: (context, acrobaticsData, child) {
      return Padding(
        padding: const EdgeInsets.only(right: 18.0, top: 12.0),
        child: InkWell(
          onTap: () async {
            final response = await _createPenalties();
            final newPenalties = (widget.penaltyType == Constraint)
                ? (json.decode(response.body) as List<dynamic>)
                    .map((c) => Constraint.fromJson(c))
                    .toList()
                : (json.decode(response.body) as List<dynamic>)
                    .map((o) => Objective.fromJson(o))
                    .toList();
            acrobaticsData.updatePenalties(widget.phaseIndex,
                _penaltyTypeToEndpoint(plural: false), newPenalties);
          },
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
    });
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
    required this.endpointPrefix,
  });

  final int phaseIndex;
  final int penaltyIndex;
  final Type penaltyType;
  final double width;
  final Penalty penalty;
  final String endpointPrefix;

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

  String _penaltyTypeToEndpoint({required bool plural}) {
    switch (penaltyType) {
      case Objective:
        return plural ? 'objectives' : 'objective';
      case Constraint:
        return plural ? 'constraints' : 'constraint';
      default:
        throw 'Wrong penalty type';
    }
  }

  Future<http.Response> _deletePenalties() async {
    final url = Uri.parse(
        '${APIConfig.url}$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex');

    final response = await http.delete(url);

    if (response.statusCode == 200) {
      if (kDebugMode) {
        print('Removed a penalty (${_penaltyTypeToEndpoint(plural: true)})');
      }
      return response;
    } else {
      throw Exception("Fetch error");
    }
  }

  @override
  Widget build(BuildContext context) {
    final arguments = penalty.arguments;

    return Consumer<AcrobaticsData>(builder: (context, acrobaticsData, child) {
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
                    '$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex',
                putEndpoint:
                    '$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/penalty_type',
                customCallBack: (response) {
                  final Penalty newPenalty = (penaltyType == Objective)
                      ? Objective.fromJson(
                          json.decode(response.body) as Map<String, dynamic>)
                      : Constraint.fromJson(
                          json.decode(response.body) as Map<String, dynamic>);

                  acrobaticsData.updatePenalty(
                      phaseIndex,
                      _penaltyTypeToEndpoint(plural: false),
                      penaltyIndex,
                      newPenalty);
                },
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
                        onSubmitted: (value) => {
                          http.put(
                            Uri.parse(
                                '${APIConfig.url}$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/arguments/${argument.name}'),
                            headers: {'Content-Type': 'application/json'},
                            body: json.encode(
                                {"type": argument.type, "value": value}),
                          )
                        },
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
                    putEndpoint:
                        '$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/nodes',
                    defaultValue: penalty.nodes,
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
                            '${APIConfig.url}$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/weight'),
                        headers: {'Content-Type': 'application/json'},
                        body: json
                            .encode({"weight": double.tryParse(value) ?? 0}),
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
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9\.,\[\]]'))
                  ],
                  onSubmitted: (value) => {
                    http.put(
                      Uri.parse(
                          '${APIConfig.url}$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/target'),
                      headers: {'Content-Type': 'application/json'},
                      body: json.encode({"target": value.tryParseDoubleList()}),
                    )
                  },
                ),
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
                    putEndpoint:
                        '$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/integration_rule',
                    defaultValue: penalty.integrationRule,
                  ),
                ),
              ],
            ),
          const SizedBox(height: 12),
          Row(
            children: [
              RemoteBooleanSwitch(
                  endpoint:
                      '$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/quadratic',
                  defaultValue: penalty.quadratic,
                  leftText: "Quadratic",
                  width: width / 2 - 6,
                  requestKey: "quadratic"),
              const SizedBox(width: 12),
              RemoteBooleanSwitch(
                  endpoint:
                      '$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/expand',
                  defaultValue: penalty.expand,
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
                      '$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/multi_thread',
                  defaultValue: penalty.multiThread,
                  leftText: "MultiThread",
                  width: width / 2 - 6,
                  requestKey: "multi_thread"),
              const SizedBox(width: 12),
              RemoteBooleanSwitch(
                  endpoint:
                      '$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex/derivative',
                  defaultValue: penalty.derivative,
                  leftText: "Derivative",
                  width: width / 2 - 6,
                  requestKey: "derivative"),
            ],
          ),
          Align(
            alignment: Alignment.centerRight,
            child: InkWell(
              onTap: () async {
                final response = await _deletePenalties();
                final newPenalties = (penaltyType == Constraint)
                    ? (json.decode(response.body) as List<dynamic>)
                        .map((c) => Constraint.fromJson(c))
                        .toList()
                    : (json.decode(response.body) as List<dynamic>)
                        .map((o) => Objective.fromJson(o))
                        .toList();
                acrobaticsData.updatePenalties(phaseIndex,
                    _penaltyTypeToEndpoint(plural: false), newPenalties);
              },
              borderRadius: BorderRadius.circular(25),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Remove ${_penaltyTypeToEndpoint(plural: false)}',
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
    });
  }
}
