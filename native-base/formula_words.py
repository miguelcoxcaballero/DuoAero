"""Reviewed word-first introductions for the authored symbolic formulas.

These are deliberately explicit: a symbol can mean different things in
different fields, so a general symbol-to-name replacement is unsafe.
Each introduction uses the existing inline word-bank challenge.
"""

# A sentence with one missing word, the correct block and three distractors.
# The other named quantities make the physical relationship explicit before
# the following exercise asks the learner to build the symbolic formula.
FORMULAS = {
 'gas': ('Pressure p equals density ρ times gas constant Rₐ times ___ T.', 'temperature', ['velocity', 'altitude', 'mass']),
 'tailwind': ('Ground speed Vg equals airspeed V plus tailwind ___ w.', 'speed', ['mass', 'pressure', 'area']),
 'time': ('Flight time t equals distance d divided by ground ___.', 'speed', ['mass', 'pressure', 'area']),
 'total_time': ('Total flight time equals outbound time plus ___ time.', 'return', ['takeoff', 'reaction', 'climb']),
 'range': ('Jet range R uses speed V, lift-to-drag ratio E, gravity g, fuel consumption and the logarithm of the initial-to-final ___ ratio.', 'mass', ['temperature', 'pressure', 'area']),
 'axial_stiffness': ('Axial stiffness k equals Young modulus E times area A divided by ___.', 'length', ['pressure', 'density', 'mass']),
 'cantilever': ('Cantilever tip stiffness k equals three times Young modulus E times second moment I divided by ___ cubed.', 'length', ['pressure', 'density', 'mass']),
 'buckling': ('Critical buckling load depends on Young modulus E, second moment I and effective column ___ squared.', 'length', ['mass', 'pressure', 'temperature']),
 'extension': ('Axial extension equals force F times length L divided by Young modulus E times ___.', 'area', ['velocity', 'pressure', 'temperature']),
 'aspect': ('Wing aspect ratio equals wingspan b squared divided by wing ___ S.', 'area', ['mass', 'density', 'pressure']),
 'taper': ('Wing taper ratio equals tip chord divided by root ___.', 'chord', ['pressure', 'mass', 'density']),
 'hydraulic': ('Hydraulic power equals pressure difference times volume ___ rate.', 'flow', ['mass', 'temperature', 'pressure']),
 'dynamic_pressure': ('Dynamic pressure q equals one half times density ρ times airspeed V ___.', 'squared', ['cubed', 'halved', 'doubled']),
 'induced_drag': ('Induced drag coefficient uses lift coefficient squared, efficiency e and wing aspect ___.', 'ratio', ['mass', 'pressure', 'temperature']),
 'thrust': ('Ideal jet thrust equals mass flow rate times the difference between exhaust speed and flight ___.', 'speed', ['mass', 'pressure', 'density']),
 'kinetic_temperature': ('Kinetic temperature rise equals speed squared divided by twice specific heat at constant ___.', 'pressure', ['area', 'mass', 'velocity']),
 'static_temperature': ('Static temperature equals total temperature minus kinetic temperature ___.', 'rise', ['mass', 'area', 'force']),
 'sound': ('Speed of sound squared equals heat capacity ratio γ times gas constant R times absolute ___.', 'temperature', ['altitude', 'area', 'mass']),
 'mach': ('Mach number equals airspeed divided by the speed of ___.', 'sound', ['light', 'gravity', 'rotation']),
 'breguet_exponent': ('The range exponent uses range R, gravity g, fuel consumption, speed V and lift-to-drag ___.', 'ratio', ['mass', 'area', 'pressure']),
 'fuel_fraction': ('Fuel mass fraction equals one minus the ___ mass fraction.', 'remaining', ['initial', 'total', 'payload']),
}

KINDS = {
 'BOOK-V6-01-D1':'gas', 'BOOK-V6-01-D2':'gas',
 'WIND-TAILWIND-FORMULA':'tailwind', 'WIND-TIME-FORMULA':'time', 'WIND-TOTAL-FORMULA':'total_time',
 'BOOK-V6-03-D1':'range', 'BOOK-V6-03-D2':'range',
 'INTRO-AXIAL-STIFFNESS':'axial_stiffness', 'INTRO-CANTILEVER-STIFFNESS':'cantilever',
 'BOOK-V6-05-D1':'buckling', 'BOOK-V6-05-D2':'buckling',
 'BOOK-V6-04-D1':'extension', 'BOOK-V6-04-D2':'extension',
 'INTRO-ASPECT-RATIO':'aspect', 'INTRO-TAPER-RATIO':'taper',
 'BOOK-V6-08-D1':'hydraulic', 'BOOK-V6-08-D2':'hydraulic',
 'BOOK-V6-02-D1':'dynamic_pressure', 'BOOK-V6-02-D2':'dynamic_pressure',
 'BOOK-V6-06-D1':'induced_drag', 'BOOK-V6-06-D2':'induced_drag',
 'BOOK-V6-07-D1':'thrust', 'BOOK-V6-07-D2':'thrust',
 'TA1-0107-D2-F1':'kinetic_temperature', 'TA1-0107-D2-F2':'static_temperature',
 'TA1-0107-D2-F3':'sound', 'TA1-0107-D2-F4':'mach',
 'TA1-0078-D2-F1':'breguet_exponent', 'TA1-0078-D2-F2':'fuel_fraction',
}


def word_introduction(formula):
    """Return a stable, authored word challenge immediately before a formula."""
    sentence, answer, distractors = FORMULAS[KINDS[formula['id']]]
    assert sentence.count('___') == 1 and len({answer, *distractors}) == 4
    return {'id': formula['id']+'-WORDS', 'type':'gap', 'difficulty':formula['difficulty'],
            'stem':'Complete the formula in words: '+sentence, 'answer':[answer],
            'distractors':list(distractors), 'explanation':sentence.replace('___', answer)}
