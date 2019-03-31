import sympy


class Resonator:
    def __init__(self):
        self._symbols, self.constraints = self._initialize()
        self._explicitly_set_symbols = set()  # Symbols *explicitly* set.
        self.solutions = {}

    def _initialize(self):
        inductance = sympy.Symbol('L')
        capacitance = sympy.Symbol('C')
        impedance = sympy.Symbol('Z')
        frequency = sympy.Symbol('omega')
        resistance = sympy.Symbol('R')
        quality_factor = sympy.Symbol('Q')

        constraints = set([
            frequency - 1 / sympy.sqrt(inductance * capacitance),
            impedance - sympy.sqrt(inductance / capacitance),
            quality_factor - resistance / impedance,
            ])

        symbols = set().union(
            *[constraint.free_symbols for constraint in constraints])

        return symbols, constraints

    @property
    def symbols(self):
        return sorted(self._symbols, key=lambda x: x.name)

    def set_parameter(self, symbol):
        self._set_parameter(symbol)
        while 1:
            solutions = self.check_for_solutions()
            if not len(solutions):
                break
            for symbol, expression in solutions:
                self.solutions[symbol] = expression

    def _set_parameter(self, symbol):
        if symbol in self._explicitly_set_symbols:
            raise ValueError("Symbol {} already explicitly set".format(symbol))
        if symbol in self.solutions:
            raise ValueError("Symbol {} already solved via {}".format(
                symbol, self.solutions[symbol]))
        self._explicitly_set_symbols.add(symbol)
        self.solutions[symbol] = symbol

    def check_for_solutions(self):
        if len(self._symbols - set(self.solutions.keys())) == 0:
            return set()

        symbols, expression_sets = sympy.solve(
            self.constraints,
            set(self._symbols) - set(self.solutions.keys()),
            set=True,)
        expressions = expression_sets.pop()

        solutions = set()
        for symbol, expression in zip(symbols, expressions):
            if not all(symbol in set(self.solutions.keys()) for symbol in expression.free_symbols):
                continue
            print("Solved for {}".format(symbol))
            solutions.add((symbol, expression))
        return solutions
