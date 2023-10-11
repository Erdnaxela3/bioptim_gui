import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/widgets/custom_dropdown_button.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class CustomHttpDropdown extends StatefulWidget {
  const CustomHttpDropdown({
    super.key,
    required this.title,
    required this.width,
    required this.defaultValue,
    required this.getEndpoint,
    required this.putEndpoint,
    required this.requestKey,
    this.color = Colors.black,
    this.customStringFormatting = _defaultToString,
  });

  final String title;
  final double width;
  final String defaultValue;
  final String getEndpoint;
  final String putEndpoint;
  // the key used in the request of the put method
  final String requestKey;
  final Color color;

  final Function(String) customStringFormatting;
  static String _defaultToString(String s) => s.toString().toLowerCase();

  @override
  CustomHttpDropdownState createState() => CustomHttpDropdownState();
}

class CustomHttpDropdownState extends State<CustomHttpDropdown> {
  String _selectedValue = '';
  List<String> _availableValues = [];

  @override
  void initState() {
    super.initState();
    _selectedValue = widget.defaultValue;
    _fetchAvailableValues();
  }

  Future<void> _fetchAvailableValues() async {
    final url = Uri.parse('${APIConfig.url}${widget.getEndpoint}');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final List<dynamic> responseData = json.decode(response.body);
      final values = responseData.map((value) => value.toString()).toList();
      setState(() {
        _availableValues = values;
      });
    }
  }

  Future<void> _updateValue(String value) async {
    final url = Uri.parse('${APIConfig.url}${widget.putEndpoint}');
    final headers = {'Content-Type': 'application/json'};
    final body =
        json.encode({widget.requestKey: widget.customStringFormatting(value)});

    final response = await http.put(url, headers: headers, body: body);

    if (response.statusCode == 200) {
      setState(() {
        _selectedValue = value;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.width,
      child: CustomDropdownButton<String>(
        value: _selectedValue,
        items: _availableValues,
        title: widget.title,
        onSelected: (value) => _updateValue(value),
        color: widget.color,
      ),
    );
  }
}
