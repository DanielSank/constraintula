from constraintula import System, Symbol, sqrt


def make_resonator():
    inductance = Symbol('L')
    capacitance = Symbol('C')
    impedance = Symbol('Z')
    frequency = Symbol('omega')
    resistance = Symbol('R')
    quality_factor = Symbol('Q')

    equations = set([
        frequency - 1 / sqrt(inductance * capacitance),
        impedance - sqrt(inductance / capacitance),
        quality_factor - resistance / impedance,
        ])

    return System(equations)
