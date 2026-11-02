"""Reviewed word-first introductions for the authored symbolic formulas.

These are deliberately explicit: a symbol can mean different things in
different fields, so a general symbol-to-name replacement is unsafe.
Each introduction uses the existing inline word-bank challenge.
"""
import hashlib

# A sentence with one missing word, the correct block and three distractors.
# The other named quantities make the physical relationship explicit before
# the following exercise asks the learner to build the symbolic formula.
FORMULAS = {
 'gas': ('Pressure p equals density rho times gas constant R-air times T, the absolute ___.', 'temperature', ['velocity', 'altitude', 'mass']),
 'payload_mass': ('Payload mass m-p equals takeoff mass m-to minus operating empty mass m-oem minus fuel ___ m-f.', 'mass', ['speed', 'pressure', 'area']),
 'fuel_remaining': ('Landing fuel equals takeoff fuel minus fuel ___.', 'burned', ['loaded','stored','added']),
 'landing_payload': ('Payload equals the landing mass limit minus operating empty mass minus landing ___.', 'fuel', ['wing','area','speed']),
 'payload_minimum': ('The allowable payload is the smallest of the structural, takeoff and landing ___.', 'limits', ['speeds','temperatures','areas']),
 'reynolds': ('Reynolds number equals density times speed times chord divided by dynamic ___.', 'viscosity', ['pressure','temperature','mass']),
 'reynolds_scale': ('Chord scale equals viscosity ratio divided by density ratio times speed ratio, grouped in the ___.', 'denominator', ['numerator','exponent','sum']),
 'scaled_chord': ('Model chord equals reference chord times chord scale ___.', 'factor', ['mass','pressure','temperature']),
 'spar_moment': ('Bending moment M equals tip force F times spar ___ L.', 'length', ['pressure', 'temperature', 'mass']),
 'yield_load': ('Yield load P-y equals yield stress sigma-y times cross-sectional ___ A.', 'area', ['temperature', 'speed', 'density']),
 'load_factor': ('Load factor n equals capacity P divided by applied ___ F.', 'force', ['temperature', 'area', 'speed']),
 'spar_stress_inertia': ('The section moment I-stress for a stress limit equals moment M times outer-fibre distance c divided by allowable ___ sigma-a.', 'stress', ['density', 'speed', 'temperature']),
 'spar_deflection_inertia': ('The section moment I-deflection for a deflection limit equals tip force F times length L cubed divided by three times Young modulus E-Y times allowable ___ delta-a.', 'deflection', ['density', 'speed', 'pressure']),
 'isothermal_pressure': ('Pressure p equals base pressure p-b times e raised to the negative ___ X.', 'exponent', ['temperature', 'altitude', 'area']),
 'pressure_ratio': ('Pressure ratio r equals pressure p-B divided by ___ p-A.', 'pressure', ['temperature', 'density', 'mass']),
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
 'dynamic_pressure': ('Dynamic pressure q equals one half times airspeed V squared times ___ rho.', 'density', ['pressure', 'area', 'mass']),
 'induced_drag': ('Induced drag coefficient CDi = lift coefficient CL squared / (pi times efficiency e times aspect ___ AR).', 'ratio', ['mass', 'pressure', 'temperature']),
 'thrust': ('Ideal thrust T equals mass flow rate m-dot times the difference between exhaust speed Ve and flight ___ V0.', 'speed', ['mass', 'pressure', 'density']),
 'kinetic_temperature': ('Temperature rise delta-T equals speed V squared divided by twice specific heat cp at constant ___.', 'pressure', ['area', 'mass', 'velocity']),
 'static_temperature': ('Static temperature T equals total temperature Tt minus kinetic temperature ___ delta-T.', 'rise', ['mass', 'area', 'force']),
 'sound': ('Speed of sound a squared equals heat capacity ratio gamma times gas constant R times absolute ___ T.', 'temperature', ['altitude', 'area', 'mass']),
 'mach': ('Mach number M equals airspeed V divided by the speed of ___ a.', 'sound', ['light', 'gravity', 'rotation']),
 'breguet_exponent': ('Exponent x = (range R times gravity g times fuel consumption ce) / (speed V times lift-to-drag ___ E).', 'ratio', ['mass', 'area', 'pressure']),
 'fuel_fraction': ('Fuel fraction m-fuel / mi equals one minus the ___ mass fraction r.', 'remaining', ['initial', 'total', 'payload']),
 'cabin_pressure': ('Outside pressure p equals cabin pressure p-c minus the pressure ___.', 'difference', ['speed', 'area', 'temperature']),
 'mach_pressure': ('Dynamic pressure q equals one half times heat capacity ratio gamma times pressure p times Mach number M ___.', 'squared', ['cubed', 'halved', 'unchanged']),
 'wing_loading': ('Weight W divided by wing area S equals dynamic pressure q times lift ___.', 'coefficient', ['temperature', 'altitude', 'density']),
 'lift': ('Lift L equals dynamic pressure q times wing area S times lift ___.', 'coefficient', ['temperature', 'altitude', 'density']),
 'total_thrust': ('Total thrust T equals momentum thrust T-m plus pressure thrust T-p, the thrust due to pressure ___.', 'difference', ['temperature', 'density', 'altitude']),
 'mean_chord': ('Geometric mean chord c-bar equals wing area S divided by wing ___ b.', 'span', ['pressure', 'mass', 'density']),
}

KINDS = {
 'BOOK-V6-01-D1':'gas', 'BOOK-V6-01-D2':'gas', 'ISA-ISOTHERMAL-FORMULA':'isothermal_pressure',
 'MASS-PAYLOAD-FORMULA':'payload_mass', 'MASS-FUEL-REMAINING':'fuel_remaining', 'MASS-LANDING-PAYLOAD':'landing_payload', 'MASS-PAYLOAD-MINIMUM':'payload_minimum',
 'REYNOLDS-FORMULA':'reynolds', 'REYNOLDS-SCALE-FORMULA':'reynolds_scale', 'REYNOLDS-CHORD-FORMULA':'scaled_chord',
 'SPAR-MOMENT-FORMULA':'spar_moment', 'SPAR-STRESS-FORMULA':'spar_stress_inertia',
 'COLUMN-YIELD-FORMULA':'yield_load', 'COLUMN-FACTOR-FORMULA':'load_factor',
 'SPAR-DEFLECTION-FORMULA':'spar_deflection_inertia',
 'ISA-PRESSURE-RATIO':'pressure_ratio',
 'WIND-TAILWIND-FORMULA':'tailwind', 'WIND-TIME-FORMULA':'time', 'WIND-TOTAL-FORMULA':'total_time',
 'BOOK-V6-03-D1':'range', 'BOOK-V6-03-D2':'range',
 'INTRO-AXIAL-STIFFNESS':'axial_stiffness', 'INTRO-CANTILEVER-STIFFNESS':'cantilever',
 'BOOK-V6-05-D1':'buckling', 'BOOK-V6-05-D2':'buckling',
 'BOOK-V6-04-D1':'extension', 'BOOK-V6-04-D2':'extension',
 'INTRO-ASPECT-RATIO':'aspect', 'INTRO-TAPER-RATIO':'taper',
 'BOOK-V6-08-D1':'hydraulic', 'BOOK-V6-08-D2':'hydraulic',
 'BOOK-V6-02-D1':'dynamic_pressure', 'BOOK-V6-02-D2':'dynamic_pressure', 'ISA-DYNAMIC':'dynamic_pressure',
 'BOOK-V6-06-D1':'induced_drag', 'BOOK-V6-06-D2':'induced_drag',
 'BOOK-V6-07-D1':'thrust', 'BOOK-V6-07-D2':'thrust',
 'TA1-0107-D2-F1':'kinetic_temperature', 'TA1-0107-D2-F2':'static_temperature',
 'TA1-0107-D2-F3':'sound', 'TA1-0107-D2-F4':'mach',
 'TA1-0078-D2-F1':'breguet_exponent', 'TA1-0078-D2-F2':'fuel_fraction',
 'CABIN-PRESSURE-FORMULA':'cabin_pressure', 'CABIN-MACH-PRESSURE':'mach_pressure', 'CABIN-WING-LOADING':'wing_loading',
 'LIFT-FORMULA':'lift',
 'TOTAL-THRUST-FORMULA':'total_thrust',
 'MEAN-CHORD-FORMULA':'mean_chord',
}

# Each item is emitted as mathematical LaTeX inside the surrounding sentence.
# Do not interpret arbitrary course prose as LaTeX: these names are restricted
# to the explicitly authored word-first exercises above.
INLINE_SYMBOLS = {
 'p':'p', 'p-b':r'p_b', 'p-c':r'p_c', 'p-A':r'p_A', 'p-B':r'p_B', 'rho':r'\rho', 'R-air':r'R_a', 'T':'T',
 'm-p':r'm_p', 'm-to':r'm_{to}', 'm-oem':r'm_{oem}', 'm-f':r'm_f',
 'I-stress':r'I_\sigma', 'I-deflection':r'I_\delta', 'F':'F', 'c':'c', 'sigma-a':r'\sigma_a', 'delta-a':r'\delta_a',
 'P-y':r'P_y', 'sigma-y':r'\sigma_y', 'n':'n', 'P':'P',
 'Vg':r'V_g', 'V':'V', 'w':'w', 't':'t', 'd':'d',
 't-total':r't_{\mathrm{total}}', 't-out':r't_{\mathrm{out}}', 't-back':r't_{\mathrm{back}}',
 'R':'R', 'E':'E', 'g':'g', 'cT':r'c_T', 'mi':r'm_i', 'mf':r'm_f',
 'k':'k', 'A':'A', 'L':'L', 'I':'I', 'Pcr':r'P_{cr}', 'E-Y':r'E_Y', 'K':'K',
 'delta-L':r'\Delta L', 'F':'F', 'AR':r'\mathrm{AR}', 'b':'b', 'S':'S',
 'lambda':r'\lambda', 'c-bar':r'\bar{c}', 'c-tip':r'c_t', 'c-root':r'c_r', 'P-hyd':r'P_{\mathrm{hyd}}',
 'delta-p':r'\Delta p', 'T-m':r'T_m', 'T-p':r'T_p', 'Q':'Q', 'q':'q', 'pi':r'\pi', 'CDi':r'C_{D,i}',
 'CL':r'C_L', 'e':'e', 'm-dot':r'\dot{m}', 'Ve':r'V_e', 'V0':r'V_0',
 'delta-T':r'\Delta T', 'cp':r'c_p', 'Tt':r'T_t', 'a':'a',
 'gamma':r'\gamma', 'M':'M', 'x':'x', 'ce':r'c_e', 'm-fuel':r'm_{\mathrm{fuel}}', 'r':'r',
}

# Name of the quantity occupying the hole in the original equation, plus
# distractors. The rest of each equation comes from the reviewed LaTeX source.
EQUATION_NAMES = {
 'gas':('temperature',['density','pressure','altitude']),
 'payload_mass':('fuel mass',['payload mass','takeoff mass','empty mass']),
 'fuel_remaining':('landing fuel',['takeoff fuel','fuel burned','payload']),
 'landing_payload':('payload',['empty mass','landing fuel','landing limit']),
 'payload_minimum':('payload',['structural limit','takeoff limit','landing limit']),
 'reynolds':('Reynolds number',['density','speed','viscosity']),
 'reynolds_scale':('chord scale',['density ratio','speed ratio','viscosity ratio']),
 'scaled_chord':('model chord',['reference chord','chord scale','density']),
 'spar_moment':('spar length',['tip force','bending moment','pressure']),
 'yield_load':('cross-sectional area',['yield stress','yield load','temperature']),
 'load_factor':('load factor',['capacity','applied force','area']),
 'spar_stress_inertia':('stress-limit inertia',['bending moment','allowable stress','distance']),
 'spar_deflection_inertia':('deflection-limit inertia',['tip force','length','allowable deflection']),
 'isothermal_pressure':('pressure',['base pressure','temperature','density']),
 'pressure_ratio':('pressure ratio',['temperature','density','altitude']),
 'tailwind':('wind speed',['airspeed','ground speed','flight time']),
 'time':('flight time',['distance','ground speed','fuel mass']),
 'total_time':('return time',['outbound time','total time','distance']),
 'range':('range',['speed','fuel mass','altitude']),
 'axial_stiffness':('axial stiffness',['area','length','force']),
 'cantilever':('tip stiffness',['length','force','pressure']),
 'buckling':('critical load',['length','mass','temperature']),
 'extension':('extension',['force','area','density']),
 'aspect':('aspect ratio',['wing area','wingspan','taper ratio']),
 'taper':('taper ratio',['aspect ratio','wingspan','area']),
 'hydraulic':('flow rate',['hydraulic power','pressure','area']),
 'dynamic_pressure':('density',['dynamic pressure','airspeed','wing area']),
 'induced_drag':('induced drag coefficient',['lift coefficient','aspect ratio','efficiency']),
 'thrust':('flight speed',['mass flow','exhaust speed','pressure']),
 'kinetic_temperature':('temperature rise',['speed','specific heat','pressure']),
 'static_temperature':('temperature rise',['total temperature','speed','density']),
 'sound':('temperature',['speed','pressure','density']),
 'mach':('Mach number',['airspeed','sound speed','pressure']),
 'breguet_exponent':('exponent',['range','airspeed','fuel mass']),
 'fuel_fraction':('remaining fraction',['fuel fraction','total mass','speed']),
 'cabin_pressure':('outside pressure',['cabin pressure','difference','temperature']),
 'mach_pressure':('dynamic pressure',['cabin pressure','density','area']),
 'wing_loading':('lift coefficient',['wing area','weight','airspeed']),
 'lift':('lift',['drag','weight','wing area']),
 'total_thrust':('total thrust',['momentum thrust','pressure thrust','wing area']),
 'mean_chord':('mean chord',['wingspan','wing area','aspect ratio']),
}

# Where the quantity is an operand at the top level, keep the hole precisely
# at that operand. The expression on each side remains unchanged. For a nested
# fraction we instead put the hole on the left of the equality so the fraction
# and its bar are preserved as one rendered mathematical object.
IN_PLACE = {
 'gas':(r'p=\rho R_a','T',''),
 'payload_mass':(r'm_p=m_{to}-m_{oem}-',r'm_f',''),
 'fuel_remaining':('',r'm_{f,l}',r'=m_{f,t}-m_b'),
 'landing_payload':('','m_p',r'=m_l-m_o-m_{f,l}'),
 'payload_minimum':('','m_p',r'=\min(m_{p,s},m_{p,t},m_{p,l})'),
 'reynolds':('',r'\mathrm{Re}',r'=\frac{\rho Vc}{\mu}'),
 'reynolds_scale':('','k',r'=\frac{\mu_r}{\rho_r V_r}'),
 'scaled_chord':('','c_2',r'=c_1 k'),
 'spar_moment':(r'M=F',r'L',''),
 'yield_load':(r'P_y=\sigma_y ','A',''),
 'tailwind':(r'V_g=V+','w',''),
 'total_time':(r't_{total}=t_{out}+',r't_{back}',''),
 'hydraulic':(r'P_{hyd}=\Delta p\,','Q',''),
 'dynamic_pressure':(r'q=\frac12',r'\rho',r' V^2'),
 'thrust':(r'T=\dot m(V_e-','V_0',')'),
 'static_temperature':(r'T=T_t-',r'\Delta T',''),
 'sound':(r'a^2=\gamma R','T',''),
 'fuel_fraction':(r'\frac{m_{\mathrm{fuel}}}{m_i}=1-','r',''),
 'cabin_pressure':('','p',r'=p_c-\Delta p'),
 'wing_loading':(r'\frac{W}{S}=q',r'C_L',''),
 'lift':('','L',r'=qSC_L'),
 'total_thrust':('','T',r'=T_m+T_p'),
}


def word_introduction(formula):
    """Return a stable, authored word challenge immediately before a formula."""
    sentence, answer, distractors = FORMULAS[KINDS[formula['id']]]
    assert sentence.count('___') == 1 and len({answer, *distractors}) == 4
    return {'id': formula['id']+'-WORDS', 'type':'gap', 'difficulty':formula['difficulty'],
            'stem':'Complete the formula in words: '+sentence, 'answer':[answer],
            'distractors':list(distractors), 'explanation':sentence.replace('___', answer),
            'formula_word_symbols':True}


def choices_in_stable_order(identifier, choices):
    """Vary answer placement without changing saved challenge identities."""
    return sorted(choices, key=lambda choice: hashlib.sha256((identifier+'\0'+choice).encode()).digest())


def named_equation(formula):
    """Put a named quantity into its original place in the LaTeX equation."""
    kind = KINDS[formula['id']]
    answer, distractors = EQUATION_NAMES[kind]
    equation = formula['formula_latex']
    left, separator, right = equation.partition('=')
    if not separator or not left or not right:
        raise ValueError('Reviewed named formula needs an equality: '+formula['id'])
    # An exponent and a fraction are operations that must remain visible. For
    # these formulas the hole therefore replaces a top-level RHS quantity.
    before, missing, after = IN_PLACE.get(kind, ('',left,'='+right))
    if before+missing+after != equation:
        raise ValueError('Named formula no longer matches reviewed equation: '+formula['id'])
    assert len({answer,*distractors}) == 4
    return {'id':formula['id']+'-NAMED', 'type':'formula_named',
            'difficulty':formula['difficulty'], 'stem':'Complete the formula with a quantity',
            'before_latex':before, 'after_latex':after, 'missing_latex':missing, 'formula_latex':equation,
            'answer_blocks':[answer], 'blocks':choices_in_stable_order(formula['id']+'-NAMED',[answer,*distractors]),
            'explanation':equation}


MULTI_NAMED = {
 'gas': (r'p=\rho R_aT', ['pressure','density','gas constant','temperature'],
         ['velocity','altitude','mass','area'], ['___','=','___',r'\times','___',r'\times','___']),
 'isothermal_pressure': (r'p=p_b e^{-X}', ['pressure','base pressure','exponent'],
                         ['temperature','density','area'], ['___','=','___',r'\times','e^-___']),
 'payload_mass': (r'm_p=m_{to}-m_{oem}-m_f', ['payload mass','takeoff mass','empty mass','fuel mass'],
                  ['pressure','density','altitude','speed'], ['___','=','___','-','___','-','___']),
 'fuel_remaining': (r'm_{f,l}=m_{f,t}-m_b', ['landing fuel','takeoff fuel','fuel burned'],
                    ['payload','empty mass','pressure'], ['___','=','___','-','___']),
 'landing_payload': (r'm_p=m_l-m_o-m_{f,l}', ['payload','landing limit','empty mass','landing fuel'],
                     ['temperature','speed','pressure'], ['___','=','___','-','___','-','___']),
 'payload_minimum': (r'm_p=\min(m_{p,s},m_{p,t},m_{p,l})', ['payload','structural limit','takeoff limit','landing limit'],
                     ['temperature','speed','pressure'], ['___','=',r'\min','(', '___',',','___',',','___',')']),
 'reynolds': (r'\mathrm{Re}=\frac{\rho Vc}{\mu}', ['Reynolds number','density','speed','chord','viscosity'],
              ['pressure','temperature'], ['___','=','(', '___',r'\times','___',r'\times','___',')',r'\div','___']),
 'reynolds_scale': (r'k=\frac{\mu_r}{\rho_r V_r}', ['chord scale','viscosity ratio','density ratio','speed ratio'],
                    ['temperature','mass'], ['___','=','___',r'\div','(', '___',r'\times','___',')']),
 'scaled_chord': (r'c_2=c_1 k', ['model chord','reference chord','chord scale'],
                  ['temperature','mass','pressure'], ['___','=','___',r'\times','___']),
 'spar_moment': (r'M=FL', ['bending moment','tip force','spar length'],
                 ['pressure','temperature','mass'], ['___','=','___',r'\times','___']),
 'yield_load': (r'P_y=\sigma_y A', ['yield load','yield stress','area'],
                ['temperature','speed','density'], ['___','=','___',r'\times','___']),
 'load_factor': (r'n=\frac{P}{F}', ['factor','capacity','force'],
                 ['temperature','area','speed'], ['___','=','___/___']),
 'taper': (r'\lambda=\frac{c_t}{c_r}', ['taper ratio','tip chord','root chord'],
           ['area','speed','mass'], ['___','=','___/___']),
 'aspect': (r'\mathrm{AR}=\frac{b^2}{S}', ['aspect ratio','wingspan','wing area'],
            ['speed','mass','density'], ['___','=','___^2/___']),
 'time': (r't=\frac{d}{V_g}', ['flight time','distance','ground speed'],
          ['altitude','mass','pressure'], ['___','=','___/___']),
 'pressure_ratio': (r'r=\frac{p_B}{p_A}', ['pressure ratio','pressure B','pressure A'],
                    ['temperature','density','altitude'], ['___','=','___/___']),
 'mach': (r'M=\frac{V}{a}', ['Mach number','airspeed','sound speed'],
          ['pressure','density','altitude'], ['___','=','___/___']),
 'kinetic_temperature': (r'\Delta T=\frac{V^2}{2c_p}', ['temperature rise','airspeed','specific heat'],
                         ['pressure','density','altitude'], ['___','=','___^2',r'\div','(','2',r'\times','___',')']),
 'breguet_exponent': (r'x=\frac{Rgc_e}{VE}', ['exponent','range','gravity','fuel consumption','airspeed','lift-to-drag ratio'],
                      ['mass','altitude'], ['___','=','(', '___',r'\times','___',r'\times','___',')',r'\div','(', '___',r'\times','___',')']),
 'range': (r'R=\frac{VE}{gc_T}\ln\frac{m_i}{m_f}', ['range','airspeed','lift-to-drag ratio','gravity','fuel consumption','initial mass','final mass'],
           ['density','pressure'], ['___','=','(', '___',r'\times','___',')',r'\div','(', '___',r'\times','___',')',r'\times',r'\ln','___/___']),
 'induced_drag': (r'C_{D,i}=\frac{C_L^2}{\pi e AR}', ['induced drag coefficient','lift coefficient','efficiency','aspect ratio'],
                  ['mass','speed','pressure'], ['___','=','___^2',r'\div','(',r'\pi',r'\times','___',r'\times','___',')']),
 'cantilever': (r'k=\frac{3EI}{L^3}', ['stiffness','Young modulus','second moment','length'],
                ['mass','pressure','speed'], ['___','=','(', '3',r'\times','___',r'\times','___',')',r'\div','___^3']),
 'buckling': (r'P_{cr}=\frac{\pi^2 E_Y I}{(KL)^2}', ['critical load','Young modulus','second moment','end factor','length'],
              ['mass','pressure'], ['___','=','(',r'\pi^2',r'\times','___',r'\times','___',')',r'\div','(', '___',r'\times','___',r')^2']),
 'static_temperature': (r'T=T_t-\Delta T', ['static temperature','total temperature','temperature rise'],
                        ['airspeed','pressure','density'], ['___','=','___','-','___']),
 'sound': (r'a^2=\gamma RT', ['sound speed','heat capacity ratio','gas constant','temperature'],
           ['pressure','density','altitude'], ['___^2','=','___',r'\times','___',r'\times','___']),
 'dynamic_pressure': (r'q=\frac12\rho V^2', ['dynamic pressure','density','airspeed'],
                      ['temperature','area','mass'], ['___','=',r'\frac12',r'\times','___',r'\times','___^2']),
 'cabin_pressure': (r'p=p_c-\Delta p', ['outside pressure','cabin pressure','pressure difference'],
                    ['temperature','speed','area'], ['___','=','___','-','___']),
 'mach_pressure': (r'q=\frac12\gamma pM^2', ['dynamic pressure','heat capacity ratio','outside pressure','Mach number'],
                   ['temperature','area','mass'], ['___','=',r'\frac12',r'\times','___',r'\times','___',r'\times','___^2']),
 'wing_loading': (r'\frac{W}{S}=qC_L', ['weight','wing area','dynamic pressure','lift coefficient'],
                  ['temperature','altitude','mass'], ['___/___','=','___',r'\times','___']),
 'lift': (r'L=qSC_L', ['lift','dynamic pressure','wing area','lift coefficient'],
          ['temperature','altitude','mass'], ['___','=','___',r'\times','___',r'\times','___']),
 # The preceding word challenge names both contributions as thrust. Keep the
 # tiles compact enough that the original two-column bank and Check stay on
 # screen at large font sizes.
 'total_thrust': (r'T=T_m+T_p', ['total thrust','momentum part','pressure part'],
                  ['temperature','altitude','mass'], ['___','=','___','+','___']),
 'mean_chord': (r'\bar{c}=\frac{S}{b}', ['mean chord','wing area','wingspan'],
                ['temperature','density','mass'], ['___','=','___/___']),
 'thrust': (r'T=\dot m(V_e-V_0)', ['thrust','mass flow','exhaust speed','flight speed'],
            ['pressure','density','altitude'], ['___','=','___',r'\times','(','___','-','___',')']),
 'fuel_fraction': (r'\frac{m_{\mathrm{fuel}}}{m_i}=1-r', ['fuel mass','initial mass','fraction left'],
                   ['temperature','pressure','area'], ['___/___','=','1','-','___']),
 'spar_stress_inertia': (r'I_\sigma=\frac{Mc}{\sigma_a}', ['inertia','moment','distance','stress'],
                         ['pressure','speed','temperature'], ['___','=','___*___/___']),
 'axial_stiffness': (r'k=\frac{EA}{L}', ['stiffness','Young modulus','area','length'],
                     ['pressure','temperature','speed'], ['___','=','___*___/___']),
 'extension': (r'\Delta L=\frac{FL}{E_Y A}', ['extension','force','length','Young modulus','area'],
               ['pressure','temperature','speed'], ['___','=','___*___/___*___']),
 'spar_deflection_inertia': (r'I_\delta=\frac{FL^3}{3E\delta_a}', ['inertia','force','length','Young modulus','deflection'],
                             ['pressure','speed','temperature'], ['___','=','(', '___',r'\times','___^3',')',r'\div','(', '3',r'\times','___',r'\times','___',')']),
 'tailwind': (r'V_g=V+w', ['ground speed','airspeed','wind speed'],
              ['distance','flight time','altitude'], ['___','=','___','+','___']),
 'total_time': (r't_{total}=t_{out}+t_{back}', ['total time','outbound time','return time'],
                ['distance','ground speed','wind speed'], ['___','=','___','+','___']),
 'hydraulic': (r'P_{hyd}=\Delta p\,Q', ['hydraulic power','pressure difference','flow rate'],
               ['mass','temperature','altitude'], ['___','=','___',r'\times','___']),
}


def named_equation_all(formula):
    """Put reviewed quantity names in place while keeping every operation."""
    expected, answers, distractors, parts = MULTI_NAMED[KINDS[formula['id']]]
    if formula['formula_latex'] != expected:
        raise ValueError('Multi-slot equation no longer matches reviewed formula: ' + formula['id'])
    assert sum(4 if p == '___*___/___*___' else 3 if p == '___*___/___' else 2 if p in ('___/___','___^2/___','___^2/2*___') else 1 if p in ('___','e^-___') or p.startswith('___^') else 0 for p in parts) == len(answers)
    assert len(set(answers+distractors)) == len(answers+distractors)
    return {'id':formula['id']+'-NAMED-ALL', 'type':'formula_named',
            'difficulty':formula['difficulty'],
            'stem':('Complete thrust using its contributions' if KINDS[formula['id']]=='total_thrust'
                    else 'Complete the formula with quantities'),
            # The symbolic product is implicit; explicit multiplication signs
            # keep the relationship readable when word tiles wrap to a line.
            'inline_latex':list(parts),
            'formula_latex':formula['formula_latex'],
            'answer_blocks':answers,
            'blocks':choices_in_stable_order(formula['id']+'-NAMED-ALL',answers+distractors),
            'explanation':formula['formula_latex']}
