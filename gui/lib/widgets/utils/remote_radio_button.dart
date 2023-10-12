import 'dart:convert';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart'
    as http; // Import the http package for making HTTP requests.

class RemoteRadioButton<T> extends StatefulWidget {
  final T defaultValue;
  final String getEndpoint;
  final String putEndpoint;
  final String requestKey;

  const RemoteRadioButton({
    Key? key,
    required this.defaultValue,
    required this.getEndpoint,
    required this.putEndpoint,
    required this.requestKey,
  }) : super(key: key);

  @override
  RemoteRadioButtonState<T> createState() => RemoteRadioButtonState<T>();
}

class RemoteRadioButtonState<T> extends State<RemoteRadioButton<T>> {
  T selectedValue = null as T;
  List<T> _availableValues = ["mayer", "lagrange"];

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        for (var item in widget.items)
          Row(
            children: [
              Radio<T>(
                value: item,
                groupValue: widget.defaultValue,
                onChanged: (newValue) {
                  if (newValue != null) {
                    _makePutRequest(newValue);
                  }
                },
              ),
              Text(item.toString()),
            ],
          ),
      ],
    );
  }

  Future<void> _makePutRequest(T value) async {
    final Uri url = Uri.parse(widget.putEndpoint);

    final response = await http.put(
      url,
      headers: {
        'Content-Type': 'application/json',
      },
      body: json.encode({'value': value}),
    );

    if (response.statusCode == 200) {
      setState(() {
        widget.defaultValue = value;
      });
    }
  }
}
