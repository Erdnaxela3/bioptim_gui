// import 'package:bioptim_gui/models/acrobatics_data.dart';
// import 'package:bioptim_gui/models/api_config.dart';
// import 'package:bioptim_gui/models/objective_type.dart';
// import 'package:bioptim_gui/widgets/penalties/integration_rule_chooser.dart';
// import 'package:bioptim_gui/widgets/penalties/nodes_chooser.dart';
// import 'package:bioptim_gui/widgets/penalties/objective_type_radio.dart';
// import 'package:bioptim_gui/widgets/utils/animated_expanding_widget.dart';
// import 'package:bioptim_gui/widgets/utils/remote_boolean_switch.dart';
// import 'package:flutter/foundation.dart';
// import 'package:flutter/material.dart';
// import 'package:flutter/services.dart';
// import 'package:http/http.dart' as http;

// class PenaltyExpander extends StatelessWidget {
//   const PenaltyExpander({
//     super.key,
//     required this.penaltyType,
//     required this.phaseIndex,
//     required this.width,
//     required this.penalties,
//   });

//   final Type penaltyType;
//   final int phaseIndex;
//   final double width;
//   final List<dynamic> penalties;

//   String _penaltyTypeToString({required bool plural}) {
//     switch (penaltyType) {
//       case ObjectiveFcn:
//         return plural ? 'Objective functions' : 'Objective function';
//       case ConstraintFcn:
//         return plural ? 'Constraints' : 'Constraint';
//       default:
//         throw 'Wrong penalty type';
//     }
//   }

//   Future<void> _createPenalties() async {
//     final url = Uri.parse(
//         '${APIConfig.url}/acrobatics/somersaults_info/$phaseIndex/objectives');

//     final response = await http.post(url);

//     if (response.statusCode == 200) {
//       if (kDebugMode) {
//         print("Created a penalty");
//       }
//     } else {
//       throw Exception("Fetch error");
//     }
//   }

//   @override
//   Widget build(BuildContext context) {
//     return AnimatedExpandingWidget(
//       header: SizedBox(
//         width: width,
//         height: 50,
//         child: Align(
//           alignment: Alignment.centerLeft,
//           child: Text(
//             _penaltyTypeToString(plural: true),
//             style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
//           ),
//         ),
//       ),
//       child: Column(
//         crossAxisAlignment: CrossAxisAlignment.start,
//         children: [
//           Align(
//             alignment: Alignment.centerRight,
//             child: _buildAddButton(
//                 _penaltyTypeToString(plural: false).toLowerCase()),
//           ),
//           const SizedBox(height: 24),
//           ...penalties.asMap().keys.map((index) => Padding(
//                 padding: const EdgeInsets.only(bottom: 24.0),
//                 child: _PathTile(
//                     key: ObjectKey(penalties[index]),
//                     phaseIndex: phaseIndex,
//                     penaltyIndex: index,
//                     width: width,
//                     penaltyType: penaltyType,
//                     penalty: penalties[index]),
//               )),
//           const SizedBox(height: 26),
//         ],
//       ),
//     );
//   }

//   Padding _buildAddButton(String name) {
//     return Padding(
//       padding: const EdgeInsets.only(right: 18.0, top: 12.0),
//       child: InkWell(
//         onTap: _createPenalties,
//         child: Container(
//             padding:
//                 const EdgeInsets.only(left: 12, right: 4, top: 2, bottom: 2),
//             decoration: BoxDecoration(
//                 color: Colors.green, borderRadius: BorderRadius.circular(25)),
//             child: Row(
//               mainAxisSize: MainAxisSize.min,
//               children: [
//                 Text(
//                   'New $name',
//                   style: const TextStyle(color: Colors.white),
//                 ),
//                 const Icon(
//                   Icons.add,
//                   color: Colors.white,
//                 ),
//               ],
//             )),
//       ),
//     );
//   }
// }

// class _PathTile extends StatelessWidget {
//   const _PathTile({
//     required super.key,
//     required this.phaseIndex,
//     required this.penaltyIndex,
//     required this.penaltyType,
//     required this.width,
//     required this.penalty,
//   });

//   final int phaseIndex;
//   final int penaltyIndex;
//   final Type penaltyType;
//   final double width;
//   final Map<String, dynamic> penalty;

//   @override
//   Widget build(BuildContext context) {
//     final arguments = penalty["argument"];

//     return Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         Row(children: [
//           // SizedBox(
//           //   width: (penaltyType == ObjectiveFcn)
//           //       ? width *
//           //           0.87 // can't get it smaller because of the dropdown's text
//           //       : width,
//           //   child:
//           // CustomDropdownButton<PenaltyFcn>(
//           //   title:
//           //       '${penalty.fcn.penaltyType} ${penaltyIndex + 1} (${penalty.fcn.penaltyTypeToString})',
//           //   value: (penaltyType == ObjectiveFcn)
//           //       ? (penalty as Objective).genericFcn
//           //       : penalty.fcn,
//           //   items: (penaltyType == ObjectiveFcn)
//           //       ? GenericFcn.values
//           //       : penalty.fcn.fcnValues,
//           // ),
//           // ),
//           if (penaltyType == ObjectiveFcn)
//             SizedBox(
//               width: width * 0.13,
//               child: ObjectiveTypeRadio(
//                 value: ObjectiveType.mayer,
//                 customOnChanged: (ObjectiveType? value) {},
//               ),
//             ),
//         ]),
//         const SizedBox(height: 12),
//         ...arguments.map((argument) => Padding(
//               padding: const EdgeInsets.only(bottom: 12.0),
//               child: Row(
//                 children: [
//                   SizedBox(
//                     width: width,
//                     child: TextField(
//                       controller: TextEditingController(text: 'arg'),
//                       decoration: InputDecoration(
//                           label: Text(
//                               'Argument: ${argument["name"]} (${arguments["type"]})'),
//                           border: const OutlineInputBorder()),
//                       // inputFormatters: [FilteringTextInputFormatter.allow()],
//                     ),
//                   ),
//                 ],
//               ),
//             )),
//         Row(
//           children: [
//             SizedBox(
//                 width: (penaltyType == ObjectiveFcn) ? width / 2 - 3 : width,
//                 child: NodesChooser(
//                   width: width,
//                   putEndpoint: (penaltyType == ObjectiveFcn)
//                       ? '/acrobatics/somersaults_info/0/objectives/$penaltyIndex/nodes'
//                       : '/acrobatics/somersaults_info/0/constraints/$penaltyIndex/nodes',
//                 )),
//             if (penaltyType == ObjectiveFcn)
//               SizedBox(
//                 width: width / 4 - 3,
//                 child: TextField(
//                     controller: TextEditingController(
//                         text: '${penalty["weight"].toString()}}'),
//                     decoration: const InputDecoration(
//                         label: Text('Weight'), border: OutlineInputBorder()),
//                     inputFormatters: [
//                       FilteringTextInputFormatter.allow(RegExp(r'[0-9\.]'))
//                     ]),
//               ),
//             if (penaltyType == ObjectiveFcn)
//               // SizedBox(
//               //     width: width / 4 + 6,
//               //     child: MinMaxRadio(
//               //         value: (penalty as Objective).minimizeOrMaximize,
//               //         customOnChanged: (value) {})),
//           ],
//         ),
//         const SizedBox(height: 12),
//         Row(
//           children: [
//             Expanded(
//               child: TextField(
//                   controller: TextEditingController(
//                       text: '${penalty["target"].toString()}}'),
//                   decoration: const InputDecoration(
//                       label: Text('Target'), border: OutlineInputBorder()),
//                   inputFormatters: [
//                     FilteringTextInputFormatter.allow(RegExp(r'[0-9\.,]'))
//                   ]),
//             ),
//           ],
//         ),
//         // Mayer objectives don't have integration_rule
//         if (penalty.runtimeType != Objective ||
//             (penalty as Objective).objectiveType != ObjectiveType.mayer)
//           const SizedBox(height: 12),
//         if (penalty.runtimeType != Objective ||
//             (penalty as Objective).objectiveType != ObjectiveType.mayer)
//           Row(
//             children: [
//               SizedBox(
//                 width: width,
//                 child: IntegrationRuleChooser(
//                   width: width,
//                   putEndpoint: (penaltyType == ObjectiveFcn)
//                       ? '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/integration_rule'
//                       : '/acrobatics/somersaults_info/$phaseIndex/constraints/$penaltyIndex/integration_rule',
//                 ),
//               ),
//             ],
//           ),
//         const SizedBox(height: 12),
//         Row(
//           children: [
//             RemoteBooleanSwitch(
//                 endpoint:
//                     '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/quadratic',
//                 defaultValue: true,
//                 leftText: "Quadratic",
//                 width: width / 2 - 6,
//                 requestKey: "quadratic"),
//             const SizedBox(width: 12),
//             RemoteBooleanSwitch(
//                 endpoint:
//                     '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/expand',
//                 defaultValue: true,
//                 leftText: "Expand",
//                 width: width / 2 - 6,
//                 requestKey: "expand"),
//           ],
//         ),
//         const SizedBox(height: 12),
//         Row(
//           children: [
//             RemoteBooleanSwitch(
//                 endpoint:
//                     '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/multi_thread',
//                 defaultValue: false,
//                 leftText: "MultiThread",
//                 width: width / 2 - 6,
//                 requestKey: "multi_thread"),
//             const SizedBox(width: 12),
//             RemoteBooleanSwitch(
//                 endpoint:
//                     '/acrobatics/somersaults_info/$phaseIndex/objectives/$penaltyIndex/derivative',
//                 defaultValue: false,
//                 leftText: "Derivative",
//                 width: width / 2 - 6,
//                 requestKey: "derivative"),
//           ],
//         ),
//         Align(
//           alignment: Alignment.centerRight,
//           child: InkWell(
//             onTap: () {
//               // TODO call delete on constraint
//             },
//             borderRadius: BorderRadius.circular(25),
//             child: const Padding(
//               padding: EdgeInsets.all(12),
//               child: Row(
//                 mainAxisSize: MainAxisSize.min,
//                 children: [
//                   Text(
//                     'Remove TODO Constraint/Objective', // TODO
//                     style: TextStyle(color: Colors.red),
//                   ),
//                   SizedBox(width: 8),
//                   Icon(
//                     Icons.delete,
//                     color: Colors.red,
//                   ),
//                 ],
//               ),
//             ),
//           ),
//         ),
//         const SizedBox(height: 14),
//       ],
//     );
//   }
// }
