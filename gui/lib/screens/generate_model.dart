import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class GenerateModel extends StatefulWidget {
  const GenerateModel({Key? key}) : super(key: key);

  @override
  // ignore: library_private_types_in_public_api
  _GenerateModelState createState() => _GenerateModelState();
}

class _GenerateModelState extends State<GenerateModel> {
  final TextEditingController _textEditingController = TextEditingController();
  String _responseMessage = '';

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          TextField(
            controller: _textEditingController,
            onSubmitted: (text) {
              // Handle text changes and make the POST request here
              _makePostRequest(text);
            },
            decoration: const InputDecoration(labelText: 'Enter Text'),
          ),
          const SizedBox(height: 16),
          Text('Response Message: $_responseMessage'),
        ],
      ),
    );
  }

  Future<void> _makePostRequest(String text) async {
    final Uri url =
        Uri.parse('http://localhost:8000/acrobatics/nb_somersaults');
    final Map<String, String> headers = {'Content-Type': 'application/json'};
    final Map<String, int> body = {'nb_somersaults': int.parse(text)};

    final response = await http.put(
      url,
      headers: headers,
      body: json.encode(body),
    );

    if (response.statusCode == 200) {
      final responseData = json.decode(response.body);
      final message = responseData['nb_somersaults'];
      setState(() {
        _responseMessage = message.toString();
      });
    } else {
      setState(() {
        _responseMessage = 'Error: ${response.statusCode}';
      });
    }
  }

  @override
  void dispose() {
    _textEditingController.dispose();
    super.dispose();
  }
}
