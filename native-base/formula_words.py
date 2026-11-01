"""Reviewed word-first introductions for the authored symbolic formulas.

These are deliberately explicit: a symbol can mean different things in
different fields, so a general symbol-to-name replacement is unsafe.
Each introduction uses the existing inline word-bank challenge.
"""

# A sentence with one missing word, the correct block and three distractors.
# The other named quantities make the physical relationship explicit before
# the following exercise asks the learner to build the symbolic formula.
FORMULAS = {
 'gas': ('Pressure p equals density rho times gas constant R-air times ___ T.', 'temperature', ['velocity', 'altitude', 'mass']),
 'tailwind': ('Ground speed Vg equals airspeed V plus tailwind ___ w.', 'speed', ['mass', 'pressure', 'area']),
 'time': ('Flight time t equals distance d divided by ground ___ Vg.', 'speed', ['mass', 'pressure', 'area']),
 'total_time': ('Total flight time t-total equals outbound time t-out plus ___ time t-back.', 'return', ['takeoff', 'reaction', 'climb']),
 'range': ('Range R = (speed V times lift-to-drag ratio E) / (gravity g times fuel consumption cT) times log(initial ___ mi / final mass mf).', 'mass', ['temperature', 'pressure', 'area']),
 'axial_stiffness': ('Axial stiffness k equals Young modulus E times area A divided by ___.', 'length', ['pressure', 'density', 'mass']),
 'cantilever': ('Cantilever tip stiffness k equals three times Young modulus E times second moment I divided by ___ L cubed.', 'length', ['pressure', 'density', 'mass']),
 'buckling': ('Critical load Pcr = pi squared times Young modulus E-Y times second moment I / (factor K times ___ L) squared.', 'length', ['mass', 'pressure', 'temperature']),
 'extension': ('Axial extension delta-L equals force F times length L divided by Young modulus E-Y times ___ A.', 'area', ['velocity', 'pressure', 'temperature']),
 'aspect': ('Wing aspect ratio AR equals wingspan b squared divided by wing ___ S.', 'area', ['mass', 'density', 'pressure']),
 'taper': ('Wing taper ratio lambda equals tip chord c-tip divided by root ___ c-root.', 'chord', ['pressure', 'mass', 'density']),
 'hydraulic': ('Hydraulic power P-hyd equals pressure difference delta-p times volume ___ rate Q.', 'flow', ['mass', 'temperature', 'pressure']),
 'dynamic_pressure': ('Dynamic pressure q equals one half times density rho times airspeed V ___.', 'squared', ['cubed', 'halved', 'doubled']),
 'induced_drag': ('Induced drag coefficient CDi = lift coefficient CL squared / (pi times efficiency e times aspect ___ AR).', 'ratio', ['mass', 'pressure', 'temperature']),
 'thrust': ('Ideal thrust T equals mass flow rate m-dot times the difference between exhaust speed Ve and flight ___ V0.', 'speed', ['mass', 'pressure', 'density']),
 'kinetic_temperature': ('Temperature rise delta-T equals speed V squared divided by twice specific heat cp at constant ___.', 'pressure', ['area', 'mass', 'velocity']),
 'static_temperature': ('Static temperature T equals total temperature Tt minus kinetic temperature ___ delta-T.', 'rise', ['mass', 'area', 'force']),
 'sound': ('Speed of sound a squared equals heat capacity ratio gamma times gas constant R times absolute ___ T.', 'temperature', ['altitude', 'area', 'mass']),
 'mach': ('Mach number M equals airspeed V divided by the speed of ___ a.', 'sound', ['light', 'gravity', 'rotation']),
 'breguet_exponent': ('Exponent x = (range R times gravity g times fuel consumption ce) / (speed V times lift-to-drag ___ E).', 'ratio', ['mass', 'area', 'pressure']),
 'fuel_fraction': ('Fuel fraction m-fuel / mi equals one minus the ___ mass fraction r.', 'remaining', ['initial', 'total', 'payload']),
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
