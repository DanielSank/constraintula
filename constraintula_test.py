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

import collections
import math

import attr
import numpy as np
import pytest
from sympy import Symbol

import constraintula

PI = np.pi


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def diameter(self):
        return self.radius * 2

    @property
    def circumference(self):
        return self.radius * 2 * PI

    @property
    def area(self):
        return PI * self.radius ** 2


@attr.dataclass
class Foo:
    x: float
    y: float
    z: float


def test_constraintula():
    C = Symbol('C')  # circumference
    D = Symbol('D')  # diameter
    R = Symbol('R')  # radius
    A = Symbol('A')  # area

    system = constraintula.System({D - 2 * R, C - PI * D, A - 2 * PI * R ** 2}).with_independent(C)

    circle = Circle(system.evaluate({C: 10})[R])
    assert np.abs(circle.radius - 10 / (2 * PI)) < 0.001


def test_make_wrapper():
    x, y, z = constraintula.symbols('x y z')
    foo_factory = constraintula.make_wrapper(Foo, [x - y * z])
    foo = foo_factory(y=2, z=3)
    assert math.isclose(foo.x, 6)


def test_circle():
    circumference, diameter, radius, area = \
        constraintula.symbols('circumference diameter radius area')

    @constraintula.constrain([
        diameter - 2 * radius,
        circumference - PI * diameter,
        area - 2 * PI * radius ** 2
    ])
    class Circle:
        def __init__(self, radius):
            self.radius = radius

        @property
        def diameter(self):
            return self.radius * 2

        @property
        def circumference(self):
            return self.radius * 2 * PI

        @property
        def area(self):
            return PI * self.radius ** 2

    # pylint: disable=no-value-for-parameter, unexpected-keyword-arg
    circle = Circle(circumference=10)
    assert np.abs(circle.radius - 10 / (2 * PI)) < 0.001


def test_constrain_with_attr():
    x, y, z = constraintula.symbols('x y z')

    @constraintula.constrain([x * y - z])
    @attr.dataclass(frozen=True)
    class Bar:
        x: float
        y: float
        z: float

    bar = Bar(x=3, z=9)  # y should be 3
    assert math.isclose(bar.y, 3)
    assert isinstance(bar, Bar)
    with pytest.raises(Exception):
        bar.x = 4


def test_constrain_with_vanilla_class():
    x, y, z = constraintula.symbols('x y z')

    @constraintula.constrain([x * y - z])
    class Baz:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    # pylint: disable=no-value-for-parameter
    baz = Baz(x=3, z=9)
    # pylint: enable=no-value-for-parameter
    assert math.isclose(baz.y, 3)
    assert isinstance(baz, Baz)


def test_constrain_with_properties():
    x, y, z = constraintula.symbols('x y z')

    @constraintula.constrain([x * y - z])
    class Milton:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        @property
        def z(self):
            return self.x * self.y

    # pylint: disable=no-value-for-parameter, unexpected-keyword-arg
    milton = Milton(x=3, z=9)
    # pylint: enable=no-value-for-parameter, unexpected-keyword-arg
    assert math.isclose(milton.y, 3)
    assert isinstance(milton, Milton)
    with pytest.raises(Exception):
        milton.z = 4


def test_constrain_named_tuple():
    x, y, z = constraintula.symbols('x y z')

    MiltonOriginal = collections.namedtuple('Milton', ['x', 'y', 'z'])
    Milton = constraintula.constrain([x * y - z])(MiltonOriginal)
    assert Milton is MiltonOriginal

    milton = Milton(x=3, z=9)
    assert math.isclose(milton.y, 3)
    with pytest.raises(Exception):
        milton.z = 4


def test_constrain_function():
    radius, circumference = constraintula.symbols('radius circumference')

    @constraintula.constrain([circumference - 2 * PI * radius])
    def area(radius):
        return PI * radius ** 2

    # pylint: disable=no-value-for-parameter, unexpected-keyword-arg
    result = area(circumference=1)
    # pylint: enable=no-value-for-parameter, unexpected-keyword-arg
    assert math.isclose(result, 1 / (PI * 4))


def test_constrain_with_ints():
    x, y, z = constraintula.symbols('x y z')

    @constraintula.constrain([x * y - z])
    @attr.dataclass(frozen=True)
    class Bar:
        x: int
        y: int
        z: int

    bar = Bar(x=3, z=9)
    assert bar.y == 3
    assert isinstance(bar.y, int)


def test_constrain_with_mixed_types():
    x, y, z = constraintula.symbols('x y z')

    @constraintula.constrain([x * y - z])
    @attr.dataclass(frozen=True)
    class Bar:
        x: int
        y: float
        z: int

    bar = Bar(x=2, z=5)  # y should be 2.5
    assert bar.y == 2.5
    assert isinstance(bar.y, float)

    # There is no integral solution
    with pytest.raises(constraintula.NoSolution):
        Bar(x=1, y=0.1)
