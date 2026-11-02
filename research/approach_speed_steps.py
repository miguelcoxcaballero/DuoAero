"""Arithmetic draft for approach speed from measured pressure/temperature.

The original problems contain an ISA pressure-altitude inversion. Since their
question asks only for true approach speed from measured pressure and measured
temperature, that inversion is not required for the requested result. This is
an isolated draft, not an accepted production lesson.
"""
import re
from decimal import Decimal, localcontext
PREFIX='Measured airfield pressure is '
PATTERN=re.compile(r'pressure is ([0-9.]+) Pa and measured temperature is ([0-9.]+) K.*?weight ([0-9.]+) N, area ([0-9.]+) m² and CLmax=([0-9.]+)')
DENSITY=r'\rho=\frac{p}{RT}'
STALL=r'V_s=\sqrt{\frac{2W}{\rho S C_{L,\max}}}'
APPROACH=r'V_{\mathrm{app}}=1.3V_s'
CONVERT=r'V_{\mathrm{km/h}}=3.6V_{\mathrm{m/s}}'


def draft(source):
    assert source['stem'].startswith(PREFIX)
    match=PATTERN.search(source['stem']);assert match,source['id']
    p,t,w,area,cl=(Decimal(x.rstrip('.')) for x in match.groups())
    assert min(p,t,w,area,cl)>0
    with localcontext() as ctx:
        ctx.prec=28
        quantum=Decimal('.000001')
        rt=Decimal(287)*t
        rho=(p/rt).quantize(quantum)
        twice=2*w
        rhoarea=(rho*area).quantize(quantum)
        denom=(rhoarea*cl).quantize(quantum)
        v2=(twice/denom).quantize(quantum)
        stall=v2.sqrt().quantize(quantum)
        app=(Decimal('1.3')*stall).quantize(quantum)
        speed=Decimal('3.6')*app
        exact=Decimal('3.6')*Decimal('1.3')*(2*w/((p/(Decimal(287)*t))*area*cl)).sqrt()
        distances=sorted((abs(speed-Decimal(o.split()[0])),i) for i,o in enumerate(source['options']))
        assert distances[0][1]==source['answer'] and distances[0][0]<distances[1][0]
        assert abs(speed-exact)<Decimal('.001'),(source['id'],speed,exact)
        def step(suffix,stem,value,latex,prerequisite,unit=''):
            delta=max(abs(value)*Decimal('.1'),Decimal('.01'))
            options=[f'{v:.6f}'+unit for v in (value,value+delta,value-delta,value+2*delta)]
            assert len(set(options))==4
            return dict(id=source['id']+suffix,type='choice',difficulty=3,stem=stem,
                        options=options,answer=0,explanation=options[0],
                        formula_hint={'latex':latex,'prerequisite':prerequisite})
        return [
            step('-RT',f'R is 287 J/(kg K) and temperature is {t} K. What is R times temperature?',rt,DENSITY,'APPROACH-DENSITY'),
            step('-RHO',f'The pressure is {p} Pa and R times temperature is {rt:.6f}. What is the air density?',rho,DENSITY,'APPROACH-DENSITY',' kg/m³'),
            step('-2W',f'The aircraft weight is {w} N. What is twice its weight?',twice,STALL,'APPROACH-STALL',' N'),
            step('-RHOS',f'Density is {rho:.6f} kg/m³ and wing area is {area} m². What is their product?',rhoarea,STALL,'APPROACH-STALL'),
            step('-DEN',f'The density-area product is {rhoarea:.6f} and the maximum lift coefficient is {cl}. What is their product?',denom,STALL,'APPROACH-STALL'),
            step('-V2',f'Twice the weight is {twice:.6f} N and the denominator is {denom:.6f}. What is their quotient?',v2,STALL,'APPROACH-STALL'),
            step('-VS',f'The squared stall speed is {v2:.6f} m²/s². What is the stall speed?',stall,STALL,'APPROACH-STALL',' m/s'),
            step('-APP',f'The stall speed is {stall:.6f} m/s. What is 1.3 times that speed?',app,APPROACH,'APPROACH-FACTOR',' m/s'),
            dict(id=source['id'],type='choice',difficulty=3,
                 stem=f'The approach speed is {app:.6f} m/s. Multiply by 3.6: what is the closest speed in km/h?',
                 options=list(source['options']),answer=source['answer'],
                 explanation=f'{app:.6f} × 3.6 = {speed:.4f} km/h; the closest option is {source["options"][source["answer"]]}.',
                 formula_hint={'latex':CONVERT,'prerequisite':'APPROACH-CONVERT'})]
