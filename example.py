import constraintula
import sympy


def make_resonator():
    inductance = sympy.Symbol('L')
    capacitance = sympy.Symbol('C')
    impedance = sympy.Symbol('Z')
    frequency = sympy.Symbol('omega')
    resistance = sympy.Symbol('R')
    quality_factor = sympy.Symbol('Q')

    equations = set([
        frequency - 1 / sympy.sqrt(inductance * capacitance),
        impedance - sympy.sqrt(inductance / capacitance),
        quality_factor - resistance / impedance,
        ])

    return constraintula.Constraintulary(equations)
