extension BoolToPythonString on bool {
  String toPythonString() {
    return this ? 'True' : 'False';
  }
}

extension StringExtension on String {
  String capitalize() {
    return "${this[0].toUpperCase()}${substring(1).toLowerCase()}";
  }
}

extension ObjectExtension on Object {
  String capitalize() {
    return toString().capitalize();
  }
}
