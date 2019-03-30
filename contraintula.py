import sympy


class Resonator:

    def __init__(self):
        self._initialize()

    def _initialize(self):
        inductance = sympy.Symbol('L')
        capacitance = sympy.Symbol('C')
        impedance = sympy.Symbol('Z')
        frequency = sympy.Symbol('omega')

        self.constraints = set([
            frequency - 1 / sympy.sqrt(inductance * capacitance),
            impedance - sympy.sqrt(inductance / capacitance)])

        self.symbols = [
            inductance,
            capacitance,
            impedance,
            frequency,]

        self.set_symbols = set()


    def set_parameter(self, symbol, value):
        if symbol in self._set_symbols:
            raise ValueError("Cannot double set symbol {}.".format(symbol))
        self._set_symbols.add(symbol)
        for constraint in self.constraints:
            self.check_constraint(constraint)

    def check_constraint(self, constraint):
        free_symbols = constraint.free_symbols
        if len(free_symbols.intersection(self.set_symbols)):

