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
            impedance - sympy.sqrt(inductance / capacitance)
        ])

        self._symbols = [inductance, capacitance, impedance, frequency]

        self._set_symbols = {}

    @property
    def symbols(self):
        return self._symbols

    def is_set(self, symbol):
        return symbol in self._set_symbols

    def set_parameter(self, symbol, value):
        if symbol in self._set_symbols:
            raise ValueError("Symbol {} already set".format(symbol))
        self._set_symbols[symbol] = value

    def check_constraints(self):
        go_again = False
        free_symbols = set(self._symbols) - set(self._set_symbols.keys())
        print("Free symbols: {}".format(free_symbols))
        exprs = sympy.solve(self.constraints, *list(free_symbols), dict=True)[0]

        print("Expressions: {}".format(exprs))

        for symbol, expr in exprs.items():
            if len(expr.free_symbols - set(self._set_symbols.keys())) == 0:
                self._set_symbols[symbol] = expr.subs(symbol, self._set_symbols)
