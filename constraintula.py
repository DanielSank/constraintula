import sympy
from sympy import Symbol


class System:
    def __init__(self, equations):
        self.equations = equations
        self._symbols = set().union(
            *[equation.free_symbols for equation in self.equations])

        self._explicitly_constrained_symbols = set()
        self.solutions = {}

    @property
    def symbols(self):
        """Alphabetical list of symbols for this object."""
        return sorted(self._symbols, key=lambda x: x.name)

    def constrain_symbol(self, symbol) -> bool:
        """Explicitly mark a symbol as constrained.

        Args:
            symbol: The symbol to set. To get a list of symbols for this object,
                use the 'symbols' attribute.

        Returns True if the system is fully constrained, False otherwise.
        """
        self._constrain_symbol(symbol)
        while 1:
            solutions = self._check_for_solutions()
            if not len(solutions):
                break
            for symbol, expression in solutions:
                self.solutions[symbol] = expression

        if len(self.solutions) == len(self._symbols):
            fully_constrained = True
        else:
            fully_constrained = False
        return fully_constrained

    def _constrain_symbol(self, symbol):
        if symbol in self._explicitly_constrained_symbols:
            raise ValueError("Symbol {} already explicitly set".format(symbol))
        if symbol in self.solutions:
            raise ValueError("Symbol {} already solved via {}".format(
                symbol, self.solutions[symbol]))
        self._explicitly_constrained_symbols.add(symbol)
        self.solutions[symbol] = symbol

    def _check_for_solutions(self):
        if len(self._symbols - set(self.solutions.keys())) == 0:
            return set()

        symbols, expression_sets = sympy.solve(
            self.equations,
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
