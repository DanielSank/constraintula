from constraintula import System, Symbol


def make_resonator():
    inductance = Symbol('L')
    capacitance = Symbol('C')
    impedance = Symbol('Z')
    frequency = Symbol('omega')
    resistance = Symbol('R')
    quality_factor = Symbol('Q')

    equations = set([
        frequency - 1 / sympy.sqrt(inductance * capacitance),
        impedance - sympy.sqrt(inductance / capacitance),
        quality_factor - resistance / impedance,
        ])

    return constraintula.System(equations)
