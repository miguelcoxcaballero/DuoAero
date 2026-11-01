"""Authored English practice grounded in the user's V6 first-midterm textbook.

The PDF is a source, not an instruction file. Printed page numbers are used.
These records are staged separately until the original controllers pass UI tests.
"""
from formula_exercises import SOURCE


def origin(page):
    return dict(SOURCE, page=page, pdf_page=page + 1)


# topic, node-name hint, page, name, formula, one-gap prefix, correct term,
# distractors, multi-block prefix, ordered blocks, explanation
FORMULAS = [
    ('2.1', 'International Standard Atmosphere', 14, 'Ideal gas',
     r'p=\rho R_aT', 'p = ρ R_a', 'T', ['T²', '1/T', 'V', 'g'],
     'p =', ['ρ', '×', 'R_a T'],
     'Pressure equals density times the specific gas constant times absolute temperature. Use kelvins; at fixed pressure, increasing temperature reduces density.'),
    ('2.4', 'Aerodynamic forces', 41, 'Dynamic pressure',
     r'q=\frac12\rho V^2', 'q = ½ ρ', 'V²', ['V', 'V³', 'S', 'C_L'],
     'q = ½', ['ρ', '×', 'V²'],
     'Dynamic pressure depends on the square of airspeed and on density. Wing area and lift coefficient enter L = q S C_L, not q itself.'),
    ('2.2', 'Breguet equation', 25, 'Jet range',
     r'R=\frac{VE}{gc_T}\ln\frac{m_i}{m_f}', 'R = [V E/(g c_T)]',
     'ln(m_i/m_f)', ['ln(m_f/m_i)', 'm_i − m_f', 'm_f/m_i', 'ln(m_i − m_f)'],
     'R =', ['V E/(g c_T)', '×', 'ln(m_i/m_f)'],
     'This jet Breguet model assumes constant speed, aerodynamic efficiency and mass-based thrust-specific fuel consumption c_T in kg/(N s). The logarithm uses total initial and final aircraft masses.'),
    ('2.3', 'axial loads', 32, 'Axial extension',
     r'\Delta L=\frac{FL}{E_Y A}', 'ΔL = F L /', 'E_Y A',
     ['E_Y I', 'G J', 'E_Y A²', 'E_Y/A'],
     'ΔL =', ['F L', '÷', 'E_Y A'],
     'For a uniform bar under axial force in linear elasticity, extension is F L/(E_Y A). Young modulus E_Y is a material property; A is cross-sectional area, not a second moment of area.'),
    ('2.3', 'Buckling', 33, 'Euler buckling',
     r'P_{cr}=\frac{\pi^2 E_Y I}{(KL)^2}', 'P_cr = π² E_Y I /', '(K L)²',
     ['K L', 'K L³', '(K L)³', 'A²'],
     'P_cr =', ['π² E_Y I', '÷', '(K L)²'],
     'Euler buckling applies to an ideal slender column. Effective length K L is squared. This instability limit must be checked separately from material strength.'),
    ('2.4', 'Three-dimensional aerodynamics', 50, 'Induced drag',
     r'C_{D,i}=\frac{C_L^2}{\pi e AR}', 'C_D,i = C_L² /', 'π e AR',
     ['π e AR²', 'π AR/e', 'π e/AR', '2 π e AR'],
     'C_D,i =', ['C_L²', '÷', 'π e AR'],
     'The finite-wing model gives induced drag proportional to C_L squared and inversely proportional to efficiency factor e and aspect ratio AR. It does not include parasite drag.'),
    ('2.5', 'Thrust', 60, 'Ideal jet thrust',
     r'T=\dot m(V_e-V_0)', 'T = ṁ', '(V_e − V_0)',
     ['(V_e + V_0)', 'V_e', '(V_e² − V_0²)', 'V_0/V_e'],
     'T =', ['ṁ', '×', '(V_e − V_0)'],
     'For equal inlet/outlet mass flow and a pressure-matched exit, thrust is mass flow times velocity increase. Otherwise pressure thrust and separate inlet/outlet momentum flows must be retained.'),
    ('2.6', 'Hydraulic and electrical power', 69, 'Hydraulic power',
     r'P_{hyd}=\Delta p\,Q', 'P_hyd = Δp', 'Q',
     ['A', 'v', 'Q²', '1/Q'],
     'P_hyd =', ['Δp', '×', 'Q'],
     'Ideal hydraulic power is pressure difference times volume flow rate. With F = Δp A and Q = A v, the same power equals F v. Real losses increase the required input power.'),
]


MATCHING = [
    ('Match each atmosphere condition to its correct relation',
     [('Fixed pressure: density ratio', 'ρ₂/ρ₁ = T₁/T₂'),
      ('ISA tropospheric temperature', 'T = T₀ − L h'),
      ('Local sound speed in ideal air', 'a = √(γ R_a T)'),
      ('Equivalent airspeed', 'V_E = V_TAS √(ρ/ρ₀)')],
     [14, 15, 17], 'Use absolute temperature. The ISA lapse-rate expression is restricted to its layer; EAS expresses the same dynamic pressure at reference density.'),
    ('Match each aerodynamic quantity to its defining relation',
     [('Dynamic pressure', 'q = ½ ρ V²'), ('Aircraft lift', 'L = q S C_L'),
      ('Aircraft drag', 'D = q S C_D'), ('Pitching moment', 'M = q S c̄ C_m')],
     [41], 'Forces need one reference area; a moment also needs a reference length. The symbol M here denotes moment, not Mach number.'),
    ('Match each constant-parameter Breguet model to its range or endurance',
     [('Jet range; c_T in kg/(N s)', '[V E/(g c_T)] ln(m_i/m_f)'),
      ('Jet endurance; c_T in kg/(N s)', '[E/(g c_T)] ln(m_i/m_f)'),
      ('Propeller range; c_P in kg/(W s)', '[η_p E/(g c_P)] ln(m_i/m_f)'),
      ('Propeller endurance at constant V', '[η_p E/(g c_P V)] ln(m_i/m_f)')],
     [25, 26], 'Mass-based specific consumption requires g in these expressions. Range divided by constant speed gives endurance. The jet and shaft-power definitions of consumption are different.'),
    ('Match each linear-elastic bar quantity to its relation',
     [('Average axial stress', 'σ = F/A'), ('Axial strain', 'ε = ΔL/L'),
      ('Axial stiffness', 'k = E_Y A/L'), ('Axial extension', 'ΔL = F L/(E_Y A)')],
     [32], 'Stress, strain, stiffness and extension are different quantities. The relations assume a uniform bar and linear elasticity.'),
    ('Match each structural idealization to its governing expression',
     [('Slender-column critical load', 'P_cr = π² E_Y I/(K L)²'),
      ('Cantilever tip deflection under tip force', 'δ = F L³/(3 E_Y I)'),
      ('Cantilever tip stiffness', 'k = 3 E_Y I/L³'),
      ('Uniform circular shaft twist', 'θ = T L/(G J)')],
     [33], 'Boundary conditions and load application matter. I is a bending second moment; J is the polar second moment for the circular shaft in this torsion model.'),
    ('Match each parabolic-polar result to its correct expression',
     [('Total drag coefficient', 'C_D = C_D0 + k C_L²'),
      ('Finite-wing induced-drag factor', 'k = 1/(π e AR)'),
      ('Lift coefficient at maximum L/D', 'C_L,opt = √(C_D0/k)'),
      ('Maximum aerodynamic efficiency', 'E_max = 1/[2 √(C_D0 k)]')],
     [50, 51], 'These optimum expressions follow from the parabolic polar with fixed coefficients. At maximum efficiency, induced and parasite contributions to C_D are equal.'),
    ('Match each propulsion definition to its relation',
     [('Ideal jet propulsive efficiency', 'η_p = 2 V₀/(V_e + V₀)'),
      ('Thrust-specific fuel consumption', 'c_T = ṁ_f/T'),
      ('Shaft-power-specific fuel consumption', 'c_P = ṁ_f/P_shaft'),
      ('Rocket specific impulse', 'I_sp = T/(ṁ_propellant g₀)')],
     [61], 'The ideal jet efficiency relation uses equal mass flow and pressure-matched flow. Rocket propellant includes fuel and oxidizer; specific impulse is measured in seconds.'),
    ('Match each ideal actuator quantity to its relation',
     [('Actuator force', 'F = Δp A'), ('Volume flow rate', 'Q = A v'),
      ('Hydraulic power', 'P_hyd = Δp Q'), ('Mechanical output power', 'P_mech = F v')],
     [69], 'In an ideal actuator hydraulic and mechanical power agree. A force increase trades off against speed; it does not create energy.'),
]


def formula_questions():
    result = []
    for i, row in enumerate(FORMULAS):
        topic, node, page, name, latex, prefix, term, distractors, multi_prefix, ordered, explanation = row
        base = {'topic': topic, 'subtopic': name, 'node_hint': node,
                'section': 'Midterm 1', 'origin': origin(page), 'explanation': explanation,
                'formula_latex': latex}
        choices = [term] + distractors
        # Fixed rotation makes the authored correct answer position nonconstant.
        shift = (i + 2) % len(choices)
        choices = choices[shift:] + choices[:shift]
        result.append(dict(base, id=f'BOOK-V6-{i+1:02d}-D1', type='formula_blocks', difficulty=1,
                           stem=f'Complete the {name.lower()} formula', prefix=prefix,
                           blocks=choices, answer_blocks=[term]))
        pool = list(dict.fromkeys(ordered + distractors[:3]))
        pool = pool[2:] + pool[:2]
        result.append(dict(base, id=f'BOOK-V6-{i+1:02d}-D2', type='formula_blocks', difficulty=2,
                           stem=f'Build the missing expression for {name.lower()}', prefix=multi_prefix,
                           blocks=pool, answer_blocks=ordered))
        stem, pairs, pages, reasoning = MATCHING[i]
        result.append({'id': f'BOOK-V6-{i+1:02d}-D3', 'type': 'matching', 'difficulty': 3,
                       'topic': topic, 'subtopic': name, 'node_hint': node, 'section': 'Midterm 1',
                       'stem': stem, 'pairs': [list(pair) for pair in pairs], 'explanation': reasoning,
                       'origin': dict(origin(pages[0]), pages=pages)})
    return result


def systems_questions():
    # stem, correct choice, three misconception-based distractors, rationale,
    # printed source page. Seven additional questions per difficulty; the three
    # hydraulic formula records above make 24 systems questions in total.
    levels = {
        1: [
            ('What supplies the spring action in an oleopneumatic landing-gear strut?', 'Compressed gas', ['Oil flowing through an orifice', 'The retraction actuator', 'The wheel brake'], 'Compressed gas stores elastic energy; restricted oil flow dissipates energy.', 67),
            ('What is the primary purpose of a fuel-tank vent?', 'Allow pressure compensation as fuel volume changes', ['Meter fuel into each combustion chamber', 'Keep the tank completely sealed from gas entry', 'Increase fuel octane rating'], 'Withdrawing liquid requires pressure compensation; a blocked vent can impair supply and load the tank structure.', 68),
            ('Does fly-by-wire require electrically powered surface actuators?', 'No; electrical command signals can control hydraulic actuators', ['Yes; hydraulic actuators are incompatible', 'No; it requires mechanical command cables', 'Yes; the signal itself supplies all actuator power'], 'Command transmission and actuator power source are different parts of the system.', 70),
            ('Which pressure source does a barometric altimeter principally use?', 'Static pressure', ['Pitot total pressure alone', 'Dynamic pressure alone', 'Cabin pressure alone'], 'A barometric altimeter converts static pressure to altitude using a pressure reference.', 71),
            ('What does a radio altimeter measure?', 'Height above the terrain beneath the aircraft', ['Pressure altitude above mean sea level', 'Altitude from static pressure', 'Distance to the nearest VOR'], 'It uses radio signals to estimate distance to the terrain, so its reading differs from barometric altitude.', 71),
            ('What does an aircraft APU usually provide?', 'Electrical and/or pneumatic power for support functions', ['The main cruise propulsive thrust', 'An unlimited battery energy store', 'A replacement for all flight-control sensors'], 'An auxiliary power unit supports ground operation, starting and selected backup functions; it is not normally the main propulsion engine.', 69),
            ('How does ADS-B differ from secondary surveillance radar interrogation?', 'ADS-B broadcasts onboard position and other data', ['ADS-B requires a reflected echo from the airframe', 'ADS-B measures static pressure at a ground station', 'ADS-B is the braking command link'], 'Secondary radar interrogates a transponder; ADS-B broadcasts information from the aircraft.', 72),
        ],
        2: [
            ('A 20 MPa pressure difference acts on a 5 cm² piston. What ideal force results?', '10 kN', ['100 kN', '1 kN', '1000 kN'], '5 cm² = 5 × 10⁻⁴ m²; F = 20 × 10⁶ × 5 × 10⁻⁴ = 10000 N.', 69),
            ('A 5 cm² piston moves at 0.1 m/s. What volume flow is required?', '3 L/min', ['0.3 L/min', '30 L/min', '300 L/min'], 'Q = A v = 5 × 10⁻⁵ m³/s. Multiply by 1000 L/m³ and 60 s/min.', 69),
            ('An ideal 28 V, 40 Ah battery supplies a constant 560 W load. What is its ideal endurance?', '2 h', ['0.5 h', '20 h', '40 h'], 'Energy is 28 × 40 = 1120 Wh, so ideal duration is 1120/560 = 2 h; usable duration can be lower.', 70),
            ('Cabin pressure is 75 kPa and exterior pressure falls from 25 to 20 kPa. How does the pressure difference change?', 'It rises from 50 to 55 kPa', ['It falls from 50 to 45 kPa', 'It stays at 75 kPa', 'It rises from 25 to 30 kPa'], 'Subtract exterior pressure from cabin pressure in each case; unchanged cabin pressure does not imply unchanged structural loading.', 71),
            ('In incompressible flow, pitot minus static pressure is 2000 Pa and density is 1.25 kg/m³. What is airspeed?', '56.6 m/s', ['40.0 m/s', '80.0 m/s', '1600 m/s'], 'V = √[2(p_t − p_s)/ρ] = √3200 = 56.57 m/s; the pressure difference is required.', 71),
            ('A 100 kN aircraft has main gear at x = 0, nose gear at 5 m and its CG at 1 m. What is the static nose-gear load?', '20 kN', ['80 kN', '100 kN', '5 kN'], 'Taking moments about the main gear gives N_nose × 5 = 100 × 1. The main gear carries the other 80 kN.', 67),
            ('A 1000 kg effective landing mass has vertical speed 2 m/s. What kinetic energy must be considered?', '2000 J', ['1000 J', '4000 J', '9810 J'], 'The vertical kinetic energy is ½ m v² = ½ × 1000 × 4 = 2000 J. Weight also does work while the strut compresses.', 68),
        ],
        3: [
            ('For an ideal hydraulic supply with fixed pressure difference and flow, piston area doubles. Which combination is correct?', 'Force doubles, speed halves, power stays constant', ['Force doubles, speed stays constant, power doubles', 'Force halves, speed doubles, power stays constant', 'Force and speed both double, power quadruples'], 'F = Δp A doubles; v = Q/A halves. Their product remains Δp Q.', 69),
            ('A 1000 kg effective mass contacts the ground at 2 m/s and stops over 0.2 m, with no residual lift. What is the mean total vertical reaction in this model?', 'About 19.81 kN', ['10.00 kN', '9.81 kN', '29.81 kN'], 'The mean net stopping force is (½ m v²)/s = 10 kN. The total reaction also balances the 9.81 kN weight.', 68),
            ('A 28 V, 40 Ah battery has 70% usable stored energy; its converter is 80% efficient. How long can it supply 560 W?', '1.12 h', ['2.00 h', '1.40 h', '2.50 h'], 'Useful energy is 28 × 40 × 0.70 × 0.80 = 627.2 Wh. Divide by the useful load power: 627.2/560 = 1.12 h.', 70),
            ('A cabin-pressure differential limit is fixed. Ambient pressure decreases during climb. What happens to the maximum permitted cabin absolute pressure?', 'It must decrease with ambient pressure to respect the same differential limit', ['It must increase by the same amount', 'It can remain fixed at any altitude', 'It must equal zero regardless of the differential limit'], 'p_cabin,max = p_ambient + Δp_max. Holding cabin pressure fixed while ambient pressure falls raises the differential.', 70),
            ('A CG moves from 1.0 m to 0.5 m ahead of the main gear while weight and 5 m wheelbase are unchanged. How does static nose-gear reaction change?', 'It halves; this alone does not establish safety during braking', ['It doubles and proves the design safe during braking', 'It is unchanged because total weight is unchanged', 'It becomes negative even though the CG remains between supports'], 'N_nose = W a/L halves. Static support reactions omit braking and other dynamic loads.', 67),
            ('Two redundant flight-control computers share one unprotected power feed. What weakness remains?', 'A common power failure can disable both channels', ['Redundancy guarantees operation after any failure', 'Only the hydraulic actuators can fail simultaneously', 'Adding software channels removes all power dependence'], 'A common cause can defeat redundant channels. Independence of essential supplies matters as well as the number of computers.', 89),
            ('An incompressible pitot-static model gives the same pressure difference at two densities. If the second density is half the first, how do the true airspeeds compare?', 'V₂ = √2 V₁', ['V₂ = 2 V₁', 'V₂ = V₁/√2', 'V₂ = V₁'], 'With fixed p_t − p_s, V = √[2(p_t − p_s)/ρ]. Halving density raises true airspeed by √2; a pressure difference alone does not fix TAS.', 71),
        ],
    }
    result = []
    for difficulty, records in levels.items():
        for i, (stem, correct, distractors, explanation, page) in enumerate(records):
            choices = [correct] + distractors
            shift = (i + difficulty) % 4
            choices = choices[shift:] + choices[:shift]
            result.append({'id': f'BOOK-V6-SYS-{i+1:02d}-D{difficulty}', 'type': 'choice',
                           'difficulty': difficulty, 'topic': '2.6', 'subtopic': 'Aircraft systems',
                           'section': 'Midterm 1', 'stem': stem, 'options': choices,
                           'answer': choices.index(correct), 'explanation': explanation,
                           'origin': origin(page)})
    return result


if __name__ == '__main__':
    import json
    from pathlib import Path
    questions = formula_questions() + systems_questions()
    path = Path(__file__).parent / 'tests/fixtures/textbook_v6_questions.json'
    path.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(questions)} authored textbook questions, 15 per difficulty; staged pending native-controller tests.')
