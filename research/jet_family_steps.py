"""Parameterized calculation drafts for the two ideal-jet practice families.

Not connected to the course: prerequisite lessons, session partitioning,
historical migration, native hint/retry, and layout still require acceptance.
This is an intermediate arithmetic scaffold, not a complete lesson. Each
calculation asks for one operation; downstream questions supply their operands.
Prerequisite teaching and session partitioning remain to be implemented.
"""
import math
from audit_jet_families import RANGE, PAYLOAD, audit

FORMULAS = {
 'dry': (r'm_d=m_o+m_p', 'Empty mass plus payload is dry mass.'),
 'tank': (r'm_{t,\mathrm{tank}}=m_d+m_f', 'Dry mass plus fuel capacity is the tank-limited takeoff mass.'),
 'minimum': (r'm_t=\min(m_{t,\max},m_{t,\mathrm{tank}})', 'The takeoff mass is the smaller takeoff limit.'),
 'burn': (r'm_i=m_t-m_b', 'Initial cruise mass is takeoff mass minus fuel burned before cruise.'),
 'reserve': (r'm_e=m_d+m_r', 'Final cruise mass is dry mass plus reserve fuel.'),
 'ratio': (r'\mu=m_i/m_e', 'The mass ratio is initial cruise mass divided by final cruise mass.'),
 'log': (r'L=\ln\mu', 'The logarithm is the natural logarithm of the mass ratio.'),
 'range': (r'R=VE L/(gc_e)', 'Cruise range is speed times aerodynamic efficiency times logarithm, divided by gravity and specific fuel consumption.'),
 'k': (r'k=\exp(Rgc_e/(VE))', 'The mass ratio factor is the exponential of range times gravity and specific fuel consumption, divided by speed and aerodynamic efficiency.'),
 'takeoff_limit': (r'p_t=m_{t,\max}/k-m_o-m_r', 'Takeoff-limited payload is maximum takeoff mass divided by the mass ratio factor, less empty mass and reserve.'),
 'landing_limit': (r'p_l=m_{l,\max}-m_o-m_r', 'Landing-limited payload is maximum landing mass less empty mass and reserve.'),
 'fuel_limit': (r'p_f=(m_{f,\max}-km_r)/(k-1)-m_o', 'Fuel-limited payload is fuel capacity less mass ratio factor times reserve, divided by the factor minus one, then less empty mass.'),
 'payload_min': (r'p=\min(p_s,p_t,p_l,p_f)', 'Allowed payload is the smallest of the structural, takeoff, landing and fuel limits.'),
}

def fmt(value):
    return f'{value:.10g}'

def choice(source, suffix, stem, value, unit, key):
    # Deterministic offsets are intentionally separated at the displayed precision.
    step = max(abs(value)*0.1, 1e-12)
    options = [f'{fmt(x)} {unit}'.strip() for x in (value, value+step, value-step, value+2*step)]
    assert len(set(options)) == 4
    return {'id':source['id']+suffix, 'type':'choice', 'difficulty':1,
            'stem':stem, 'options':options, 'answer':0,
            'explanation':options[0], 'formula_hint':{'latex':FORMULAS[key][0],
                  'prerequisite':'JET-'+key.upper().replace('_','-')}, 'expected':value}

def draft(source):
    result = audit(source)
    if not result:
        raise ValueError('Not an audited ideal-jet family')
    family, expected, values = result
    parts = []

    def op(suffix, label, left, symbol, right, key, unit=''):
        # Compute from the actual displayed operands, not hidden precision.
        left, right = float(f'{left:.10g}'), float(f'{right:.10g}')
        value = {'+': lambda: left + right, '-': lambda: left - right,
                 '×': lambda: left * right, '÷': lambda: left / right}[symbol]()
        parts.append(choice(source, '-' + suffix,
            f'{label} Calculate {left:.10g} {symbol} {right:.10g}.', value, unit, key))
        return value

    if family == 'range':
        o,p,mt,tank,burn,reserve,speed,eff,ce,g=map(float,RANGE.match(source['stem']).groups())
        dry=op('DRY','Empty mass plus payload:',o,'+',p,'dry','kg')
        tank_mass=op('TANK','Dry mass plus fuel capacity:',dry,'+',tank,'tank','kg')
        takeoff=min(mt,tank_mass)
        parts.append(choice(source,'-LIMIT',f'Takeoff limits are {fmt(mt)} kg and {fmt(tank_mass)} kg. Which is smaller?',takeoff,'kg','minimum'))
        initial=op('BURN','Takeoff mass less pre-cruise burn:',takeoff,'-',burn,'burn','kg')
        final=op('RESERVE','Dry mass plus reserve:',dry,'+',reserve,'reserve','kg')
        ratio=op('RATIO','Initial cruise mass divided by final cruise mass:',initial,'÷',final,'ratio')
        shown_ratio=float(f'{ratio:.10g}')
        logarithm=math.log(shown_ratio)
        parts.append(choice(source,'-LOG',f'Calculate the natural logarithm of {shown_ratio:.10g}.',logarithm,'','log'))
        numerator=op('VE','Speed times aerodynamic efficiency:',speed,'×',eff,'range')
        numerator=op('VEL','Multiply the previous result by the logarithm:',numerator,'×',logarithm,'range')
        denominator=op('GC','Gravity times specific fuel consumption:',g,'×',ce,'range')
        metres=op('METRES','Divide the numerator by the denominator for range in metres:',numerator,'÷',denominator,'range','m')
        final_value=float(f'{metres:.10g}') / 1000
        question=f'Convert {metres:.10g} m to kilometres by dividing by 1000. Choose the closest value.'
        key='range'
    else:
        o,mt,land,struct,tank,reserve,distance,speed,eff,ce,g=map(float,PAYLOAD.match(source['stem']).groups())
        x=op('RG','Range times gravitational acceleration:',distance,'×',g,'k')
        x=op('RGC','Multiply the result by specific fuel consumption:',x,'×',ce,'k')
        y=op('VE','Speed times aerodynamic efficiency:',speed,'×',eff,'k')
        exponent=op('EXPONENT','Divide the numerator by the denominator:',x,'÷',y,'k')
        shown_exponent=float(f'{exponent:.10g}'); k=math.exp(shown_exponent)
        parts.append(choice(source,'-K',f'Calculate the exponential of {shown_exponent:.10g}.',k,'','k'))
        takeoff=op('TAKEOFF-A','Maximum takeoff mass divided by the mass ratio:',mt,'÷',k,'takeoff_limit','kg')
        takeoff=op('TAKEOFF-B','Subtract empty mass:',takeoff,'-',o,'takeoff_limit','kg')
        takeoff=op('TAKEOFF-C','Subtract reserve:',takeoff,'-',reserve,'takeoff_limit','kg')
        landing=op('LANDING-A','Maximum landing mass less empty mass:',land,'-',o,'landing_limit','kg')
        landing=op('LANDING-B','Subtract reserve:',landing,'-',reserve,'landing_limit','kg')
        fuel=op('FUEL-A','Mass ratio factor times reserve:',k,'×',reserve,'fuel_limit','kg')
        fuel=op('FUEL-B','Fuel capacity less that result:',tank,'-',fuel,'fuel_limit','kg')
        kminus=op('FUEL-C','Mass ratio factor minus one:',k,'-',1,'fuel_limit')
        fuel=op('FUEL-D','Divide the remaining fuel capacity by the factor minus one:',fuel,'÷',kminus,'fuel_limit','kg')
        fuel=op('FUEL-E','Subtract empty mass:',fuel,'-',o,'fuel_limit','kg')
        final_value=min(struct,takeoff,landing,fuel)
        question=f'The limits are {struct:.4f} kg, {takeoff:.4f} kg, {landing:.4f} kg and {fuel:.4f} kg. Which listed value is closest to the smallest?'
        key='payload_min'
    options=[float(x.split()[0]) for x in source['options']]
    assert min(range(len(options)), key=lambda i:abs(options[i]-final_value)) == source['answer'],source['id']
    parts.append({'id':source['id'], 'type':'choice', 'difficulty':source.get('difficulty',1),
        'stem':question, 'options':list(source['options']), 'answer':source['answer'],
        'explanation':f'The closest original option is {source["options"][source["answer"]]}.',
        'formula_hint':{'latex':FORMULAS[key][0], 'prerequisite':'JET-'+key.upper().replace('_','-')},
        'expected':expected})
    return parts
