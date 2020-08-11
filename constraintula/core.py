# Copyright 2020 The constraintula Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module provides tools for analyzing a system of symbols and constraints
on those symbols. For example, a circle can be described by four different
symbols:
    radius
    diameter
    perimeter
    area
but there's only one degree of freedom because the symbols are constrained by
a set of constraint equations:
    diameter - 2 radius = 0
    perimeter - 2 pi radius = 0
    area - pi radius^2 = 0 .
This module provides classes that help handle this kind of situation. For
example, one class allows you to declare the symbols and their constraints, and
then choose a subset of the symbols to be considered independent. The class then
provides functions that map the independents to the dependents.
"""
import functools
import inspect
from typing import (
    Any,
    Callable,
    FrozenSet,
    Iterable,
    Mapping,
    Optional,
    overload,
    Sequence,
    Type,
    Union,
)

import sympy
from sympy import Expr, Symbol, symbols


class System:
    """A system of constraints that can be solved for a subset of symbols.

    Consider a system with two equations:

        ratio = a / b
        product = a * b

    This system has four symbols: a, b, ratio, and product. Some times we might
    be interested in this system from the point of view where a and b are
    known and the ratio and product are dependent on them. Alternatively, we
    might have a case were the ratio and product are known and a and b are
    thought of as dependent on the ratio and product. This class provides an
    interface for solving the system in whichever way you want.

    Example:
        a, b, ratio, product = symbols('a', 'b', 'ratio', 'product')
        constraints = set([a * b - product, a / b - ratio])
        system = System(constraints)

    Notice that constraints is a set of expressions which are understood to be
    equal to zero.

    Once the system is created, constrain whichever set of symbols you want to
    think of as independent, e.g.

        system.constrain_symbols([ratio, product])

    Attributes:
        constraints: Each element is an expression that constrains the
            relationships between the symbols. There's an implicit
            "equals zero", e.g. a/b - ratio means a/b - ratio = 0.
        solutions: Maps symbols to expressions giving that symbol in terms of
            other symbols which have been explicitly constrained.
    """

    constraints: FrozenSet[Expr]
    symbols: FrozenSet[Symbol]
    independents: FrozenSet[Symbol]
    solutions: Mapping[Symbol, Expr]

    def __init__(
        self,
        constraints: Iterable[Expr],
        independents: Optional[FrozenSet[Symbol]] = None,
        solutions: Optional[Mapping[Symbol, Expr]] = None,
    ):
        self.constraints = frozenset(constraint for constraint in constraints)

        self.symbols = frozenset(
            symbol for constraint in self.constraints for symbol in constraint.free_symbols
        )

        if independents is None:
            self.independents = frozenset()
        else:
            self.independents = independents

        if solutions is None:
            self.solutions = {}
        else:
            self.solutions = solutions

    def evaluate(self, values: Mapping[Symbol, float]) -> Mapping[Symbol, float]:
        """Numerically evaluate symbols given values for explicitly set ones.

        values: Mapping from symbol to its numeric value. May only contain
            symbols that were explicitly constrained on this instance.

        Returns: Mapping from symbol name to numeric values. Includes all
            symbols.
        """
        if not len(self.solutions) == len(self.symbols):
            raise ValueError("System not yet fully constrained")
        if not frozenset(values.keys()) == self.independents:
            raise ValueError("Values must match explicitly set symbols")

        results = {}
        for (symbol, expression) in self.solutions.items():
            substitutions = [(symb, values[symb]) for symb in self.independents]
            results[symbol] = sympy.N(expression.subs(substitutions))
        return results

    def with_independents(self, symbols: Iterable[Symbol]) -> 'System':
        """Get a new System with some symbols considered independent.

        Args:
            symbols: The symbols to mark as constrained.
        """
        system = self
        for symbol in symbols:
            system = system.with_independent(symbol)
        return system

    def with_independent(self, symbol: Symbol) -> 'System':
        """Get a new System with a symbol constrained.

        Args:
            symbol: The symbol to set. To get a list of symbols for this object,
                use the 'symbols' attribute.

        Returns a new System with the additional constrained symbol, and
            possible more solutions.
        """
        if symbol in self.independents:
            raise ValueError(f"Symbol {symbol} already explicitly set")
        if symbol in self.solutions:
            raise ValueError(f"Symbol {symbol} already solved via {self.solutions[symbol]}")
        known_solutions = {symbol: symbol}
        known_solutions.update(self.solutions)

        while True:
            new_solutions = self._check_for_solutions(known_solutions)
            if not new_solutions:
                break
            for _symbol, expression in new_solutions.items():
                known_solutions[_symbol] = expression

        return System(
            constraints=self.constraints,
            independents=self.independents.union({symbol}),
            solutions=known_solutions,
        )

    def _check_for_solutions(self, known_solutions) -> Mapping[Symbol, Expr]:
        # If we have as many known solutions as we do symbols, then we're done
        # and there are no new solutions.
        if len(self.symbols - set(known_solutions.keys())) == 0:
            return {}

        # Solve equations for symbols that don't already have solutions.
        symbols, expression_sets = sympy.solve(
            self.constraints, set(self.symbols) - set(known_solutions.keys()), set=True
        )
        expressions = expression_sets.pop()
        # Chomp chomp...
        # sympy can find multiple solution sets for a set of equations and it
        # returns all of them. Here we're just picking one randomly. This is
        # more or less a bug and would be improved a bit by supporting
        # assumptions about the symbols (i.e. to select the correct sign when
        # we have sqrt and other functions with multivalued inverses).

        solutions = {}
        for symbol, expression in zip(symbols, expressions):
            if not all(symbol in set(known_solutions.keys()) for symbol in expression.free_symbols):
                continue
            solutions[symbol] = expression.subs(known_solutions.items())
        return solutions

    def get_functions(self) -> Mapping[Symbol, Callable]:
        # TODO: check that system is fully constrained
        functions = {}
        for symbol, expression in self.solutions.items():
            functions[symbol] = sympy.lambdify(
                sorted(list(expression.free_symbols), key=lambda x: x.name),
                expression,
                modules="numpy",
            )
        return functions


def solve(
    independents: Mapping[str, Any], variables: Sequence[str], constraints: Iterable[Expr]
) -> Mapping[str, Any]:
    assignments = {Symbol(k): v for k, v in independents.items()}
    values = System(constraints).with_independents(assignments).evaluate(assignments)
    return {k: values[Symbol(k)] for k in variables}


def make_wrapper(
    func: Callable, constraints: Sequence[Expr], skip_first_arg: bool = False
) -> Callable:
    """Wrap a function to allow calling with any complete set of parameters.

    Args:
        func: Callable that takes keyword arguments.
        constraints: Relationships that must hold between args to func.
        skip_first_arg: If True, skip the first argument of func. This is useful
            when making a wrapper for class methods that have a special first
            argument like `self` or `cls`

    Returns:
        A new callable that takes any complete set of parameters for the given
        constraints. We solve for the values of the unspecified parameters and
        then call the given func.
    """
    arg_names = list(inspect.signature(func).parameters.keys())
    if skip_first_arg:
        arg_names = arg_names[skip_first_arg:]

    @functools.lru_cache()
    def get_system(indeps):
        symbols = [Symbol(k) for k in indeps]
        return System(constraints).with_independents(symbols)

    @functools.wraps(func)
    def wrapper(*args, **kw):
        indeps = tuple(sorted(kw))
        system = get_system(indeps)
        values = system.evaluate({Symbol(k): v for k, v in kw.items()})
        kwargs = {k: values[Symbol(k)] for k in arg_names}
        return func(*args, **kwargs)

    return wrapper


def constrain(constraints: Sequence[Expr]) -> Callable[[Type], Type]:
    """Make a function or class callable by any complete set of parameters.

    This decorates a callable object, either a function or class, to make it
    possible to call the object with any complete set of parameters. The
    given constraints will then be solved to determine the values of the other
    parameters and all values will be passed to the underlying function or
    class constructor.

    For classes, this can be used with the attr library for optimally DRY code:

        radius, area = constraintula.symbols('radius area')

        @constrain([area - pi * radius**2])
        @attr.dataclass(frozen=True)
        class Circle:
            radius: float
            area: float

        circle_by_area = Circle(area=4)
        circle_by_radius = Circle(radius=1)

    Using constrain in combination with the attr library makes mypy happy. The
    two variants shown below require explicit signals to tell the typechecker
    that we know what we're doing.

    Here's constrain with a vanilla class:

        radius, area = constraintula.symbols('radius area')

        @constrain([area - pi * radius**2])
        class Circle:
            def __init__(self, radius, area):
                self.radius = radius
                self.area = area

        circle = Circle(area=1)  # pylint: disable=no-value-for-parameter

    The decorator knows to only pass keywords that the class expects, so it
    can be used with classes that expect only a single independent subset of
    its interrelated attributes to be specified. Note, however, that in this
    case the relationship between the variables is written twice: once in
    the call to constrain and again in the @property. In addition, pylint does
    not know about the constraint decorator, so it will warn about calls that
    use alternate parameters and the warning must be explicitly disabled.

        radius, area = constraintula.symbols('radius area')

        @constrain([area - pi * radius**2])
        class Circle:
            def __init__(self, radius):
                self.radius = radius
            @property
            def area(self):
                return pi * self.radius**2

        circle = Circle(area=1)  # pylint: disable=no-value-for-parameter, unexpected-keyword-arg
    """
    return _Constrainer(constraints)


class _Constrainer:
    """Implements the `constrain` decorator; see docstring above for details."""

    def __init__(self, constraints: Sequence[Expr]):
        self.constraints = constraints

    # pylint: disable=function-redefined
    @overload
    def __call__(self, obj: Type) -> Type:
        pass

    @overload
    def __call__(self, obj: Callable) -> Callable:
        pass

    def __call__(self, obj: Union[Type, Callable]) -> Union[Type, Callable]:
        if isinstance(obj, type):
            if obj.__new__ is not object.__new__:
                method = '__new__'
            else:
                method = '__init__'
            wrapped = make_wrapper(getattr(obj, method), self.constraints, skip_first_arg=True)
            setattr(obj, method, wrapped)
            return obj

        return make_wrapper(obj, self.constraints, skip_first_arg=False)

    # pylint: enable=function-redefined
