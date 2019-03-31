import sympy


class ResonatorSolve:
    def __init__(self):
        self._symbols, self.constraints = self._initialize()
        self._set_symbols = set()
        self.solutions = {}

    def _initialize(self):
        inductance = sympy.Symbol('L')
        capacitance = sympy.Symbol('C')
        impedance = sympy.Symbol('Z')
        frequency = sympy.Symbol('omega')
        resistance = sympy.Symbol('R')
        quality_factor = sympy.Symbol('Q')

        symbols = (
            inductance,
            capacitance,
            resistance,
            frequency,
            impedance,
            quality_factor,)

        constraints = set([
            frequency - 1 / sympy.sqrt(inductance * capacitance),
            impedance - sympy.sqrt(inductance / capacitance),
            quality_factor - resistance / impedance,
            ])

        return symbols, constraints

    @property
    def symbols(self):
        return self._symbols

    def set_parameter(self, symbol):
        self._set_parameter(symbol)
        while 1:
            solved = self.check_for_solutions()
            if not len(solved):
                break
            for symbol in solved:
                self._set_parameter(symbol)

    def _set_parameter(self, symbol):
        if symbol in self._set_symbols:
            raise ValueError("Symbol {} already set".format(symbol))
        self._set_symbols.add(symbol)

    def check_for_solutions(self):
        if len(set(self.symbols) - self._set_symbols) == 0:
            return set()

        symbols, expression_sets = sympy.solve(
            self.constraints,
            set(self._symbols) - self._set_symbols,
            set=True,)
        expressions = expression_sets.pop()

        solved = set()
        for symbol, expression in zip(symbols, expressions):
            if not all(symbol in self._set_symbols for symbol in expression.free_symbols):
                continue
            print("Solved for {}".format(symbol))
            solved.add(symbol)
            self.solutions[symbol] = expression
        return solved
