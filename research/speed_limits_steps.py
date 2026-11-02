"""Arithmetic draft for coupled stall, Mach and dynamic-pressure limits.

Not connected to the course. Formula introductions, lesson sizing, exact
progress migration and Android UI still need implementation and review.
"""
import re
from decimal import Decimal, localcontext

PREFIX = 'An aircraft must maintain V>=1.25Vs at p='
PATTERN = re.compile(r'p=([\d.]+) Pa, T=([\d.]+) K, S=([\d.]+) m² and CLmax=([\d.]+).*?q=([\d.]+) Pa and Mach ([\d.]+)')
MACH_SQUARED = r'M^2=M\times M'
MACH_FACTOR = r'f=\frac{\gamma p}{2}'
MACH_PRESSURE = r'q_M=fM^2'
LIMIT = r'q_{\mathrm{allowed}}=\min(q_{\mathrm{cap}},q_M)'
LOAD = r'W_{\max}=\frac{q_{\mathrm{allowed}}S C_{L,\max}}{1.25^2}'
MASS = r'm_{\max}=W_{\max}/g'


def draft(source):
    assert source['stem'].startswith(PREFIX)
    m = PATTERN.search(source['stem']); assert m, source['id']
    p, temperature, area, cl, cap, mach = (Decimal(x.rstrip('.')) for x in m.groups())
    assert min(p, temperature, area, cl, cap, mach) > 0
    with localcontext() as ctx:
        ctx.prec = 28
        m2 = mach*mach
        factor = Decimal('.7')*p # gamma = 1.4
        qmach = factor*m2
        allowed = min(cap,qmach)
        qa = allowed*area
        qalift = qa*cl
        weight = qalift/Decimal('1.5625')
        mass = weight/Decimal('9.81')
        shown_mass = (weight.quantize(Decimal('.000001'))/Decimal('9.81'))
        original = Decimal(source['options'][source['answer']].split()[0])
        assert abs(mass-original) < Decimal('.51'), (source['id'],mass,original)
        distances = sorted((abs(shown_mass-Decimal(o.split()[0])),i) for i,o in enumerate(source['options']))
        assert distances[0][1] == source['answer'] and distances[0][0] < distances[1][0]
        def step(suffix,stem,value,latex,prerequisite,unit=''):
            offset=max(abs(value)*Decimal('.1'),Decimal('.1'))
            options=[f'{v:.6f}'+unit for v in (value,value+offset,value-offset,value+2*offset)]
            assert len(set(options))==4
            return dict(id=source['id']+suffix,type='choice',difficulty=3,stem=stem,options=options,answer=0,
                        explanation=options[0],formula_hint={'latex':latex,'prerequisite':prerequisite})
        return [
            step('-M2',f'The Mach limit is {mach}. What is its square?',m2,MACH_SQUARED,'LIMITS-MACH-SQUARED'),
            step('-F',f'The pressure is {p} Pa and half of gamma is 0.7. What is 0.7 times pressure?',factor,MACH_FACTOR,'LIMITS-MACH-FACTOR',' Pa'),
            step('-QM',f'The pressure factor is {factor:.6f} Pa and the Mach square is {m2:.6f}. What is the Mach pressure limit?',qmach,MACH_PRESSURE,'LIMITS-MACH-PRESSURE',' Pa'),
            step('-Q',f'The pressure limit is {cap} Pa and the Mach pressure limit is {qmach:.6f} Pa. What is the lower limit?',allowed,LIMIT,'LIMITS-PRESSURE-MIN',' Pa'),
            step('-QS',f'The allowed dynamic pressure is {allowed:.6f} Pa and the wing area is {area} m². What is their product?',qa,LOAD,'LIMITS-MAX-WEIGHT',' N'),
            step('-CL',f'The pressure-area product is {qa:.6f} N and the maximum lift coefficient is {cl}. What is their product?',qalift,LOAD,'LIMITS-MAX-WEIGHT',' N'),
            step('-W',f'The force product is {qalift:.6f} N. Dividing by 1.25² = 1.5625, what is the maximum weight?',weight,LOAD,'LIMITS-MAX-WEIGHT',' N'),
            dict(id=source['id'],type='choice',difficulty=3,
                 stem=f'The maximum weight is {weight:.6f} N. With g = 9.81 m/s², what is the maximum mass?',
                 options=list(source['options']),answer=source['answer'],
                 explanation=f'{weight:.6f} / 9.81 = {shown_mass:.4f} kg; the closest option is {source["options"][source["answer"]]}.',
                 formula_hint={'latex':MASS,'prerequisite':'LIMITS-MASS'})]
