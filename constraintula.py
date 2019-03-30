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

        self.symbols = set(symbol for constraint in self.constraints
                for symbol in constraint.free_symbols)

        self.set_symbols = set()

    def set_parameter(self, symbol, value):
        if symbol in self._set_symbols:
            raise ValueError("Symbol {} already set".format(symbol))
        self.set_symbols.add(symbol)

    def check_constraints(self):
        free_symbols = set()
