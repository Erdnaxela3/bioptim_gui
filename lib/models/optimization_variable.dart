import 'package:bioptim_gui/models/matrix.dart';

abstract class Path {
  Interpolation get interpolation;

  int get length;
  int get nbRows;
  int get nbCols;

  void changeDimension(int value);
}

enum Interpolation {
  constant,
  constantWithFirstAndLastDifferent,
  // TODO add linear
  ;

  @override
  String toString() {
    switch (this) {
      case constant:
        return 'Constant';
      case constantWithFirstAndLastDifferent:
        return 'Constant except for first and last points';
    }
  }

  String toPythonString() {
    switch (this) {
      case constant:
        return 'InterpolationType.CONSTANT';
      case constantWithFirstAndLastDifferent:
        return 'InterpolationType.CONSTANT_WITH_FIRST_AND_LAST_DIFFERENT';
    }
  }

  int get nbCols => colNames.length;

  List<String> get colNames {
    switch (this) {
      case constant:
        return ['All'];
      case constantWithFirstAndLastDifferent:
        return ['Start', 'Intermediates', 'Last'];
    }
  }
}

class Bound implements Path {
  final Matrix min;
  final Matrix max;
  Interpolation _interpolation;
  @override
  Interpolation get interpolation => _interpolation;
  set interpolation(Interpolation value) {
    _interpolation = value;
    min.changeNbCols(_interpolation.nbCols);
    max.changeNbCols(_interpolation.nbCols);
  }

  @override
  int get length => nbRows * nbCols;
  @override
  int get nbRows => min.nbRows;
  @override
  int get nbCols => min.nbCols;

  @override
  void changeDimension(int value) {
    min.changeNbRows(value);
    max.changeNbRows(value);
  }

  Bound({required int nbElements, required Interpolation interpolation})
      : min = Matrix.zeros(nbRows: nbElements, nbCols: interpolation.nbCols),
        max = Matrix.zeros(nbRows: nbElements, nbCols: interpolation.nbCols),
        _interpolation = interpolation;
}

class InitialGuess implements Path {
  final Matrix guess;
  @override
  final Interpolation interpolation;

  @override
  int get length => nbRows * nbCols;
  @override
  int get nbRows => guess.nbRows;
  @override
  int get nbCols => guess.nbCols;

  @override
  void changeDimension(int value) {
    guess.changeNbRows(value);
  }

  InitialGuess({required int nbElements, required this.interpolation})
      : guess = Matrix.zeros(nbRows: nbElements, nbCols: interpolation.nbCols);
}

class OptimizationVariable {
  final String name;
  final Bound bounds;
  final InitialGuess initialGuess;

  int get dimension => initialGuess.nbRows;
  int get nbRows => dimension;

  void changeDimension(int value) {
    bounds.changeDimension(value);
    initialGuess.changeDimension(value);
  }

  void fillInitialGuess(String name, {required List<double> guess}) {
    initialGuess.guess.fill(guess);
  }

  void fillBounds({
    required List<double> min,
    required List<double> max,
    int? rowIndex,
    int? colIndex,
  }) {
    bounds.min.fill(min, rowIndex: rowIndex, colIndex: colIndex);
    bounds.max.fill(max, rowIndex: rowIndex, colIndex: colIndex);
  }

  const OptimizationVariable({
    required this.name,
    required this.bounds,
    required this.initialGuess,
  });
}

enum OptimizationVariableType {
  state,
  control;

  @override
  String toString() {
    switch (this) {
      case state:
        return 'State';
      case control:
        return 'Control';
    }
  }

  String toPythonString() {
    switch (this) {
      case state:
        return 'x';
      case control:
        return 'u';
    }
  }
}

class OptimizationVariableMap {
  final Map<String, OptimizationVariable> _elements = {};

  final OptimizationVariableType type;
  OptimizationVariableMap(this.type);

  OptimizationVariable operator [](String name) {
    if (_elements[name] == null) {
      throw '$type $name not found';
    }
    return _elements[name]!;
  }

  List<String> get names => _elements.keys.toList();

  void addVariable(OptimizationVariable value) => _elements[value.name] = value;

  void clearVariables() => _elements.clear();

  void replaceVariable(OptimizationVariable value) =>
      _elements[value.name] = value;

  void removeVariable(String name) {
    if (_elements[name] == null) return;
    _elements.remove(name);
  }
}
