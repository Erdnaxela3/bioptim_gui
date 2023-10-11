import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class LoadExisting extends StatefulWidget {
  const LoadExisting({Key? key}) : super(key: key);

  @override
  // ignore: library_private_types_in_public_api
  _LoadExistingState createState() => _LoadExistingState();
}

class _LoadExistingState extends State<LoadExisting> {
  String message = 'Load existing solution page';

  Future<void> fetchNewMessage() async {
    final response =
        await http.get(Uri.parse('http://localhost:8000/acrobatics/'));
    if (response.statusCode == 200) {
      final jsonData = jsonDecode(response.body);
      final newMessage = jsonData['nb_somersaults'];
      setState(() {
        message = newMessage.toString();
      });
    } else {
      throw Exception('Failed to load new message');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(message),
          ElevatedButton(
            onPressed: () {
              fetchNewMessage();
            },
            child: const Text('Fetch New Message'),
          ),
        ],
      ),
    );
  }
}
