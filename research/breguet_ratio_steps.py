"""Reviewed arithmetic draft; not yet connected to the production path.

At equal pressure and Mach, dynamic pressure is unchanged. With equal weight,
wing area, drag polar and mass ratio, L/D and the logarithmic factor are also
unchanged. Thus the Breguet range ratio is sqrt(T2/T1) * c1/c2. The source
questions contain additional data, but no ISA inversion is needed.
"""
import re
from decimal import Decimal, localcontext

PREFIX = 'Two ideal jet cruises retain pressure'
PATTERN = re.compile(r'Temperature changes from ([0-9.]+) to ([0-9.]+) K; ce1=([0-9.e+-]+) and ce2=([0-9.e+-]+)')
TEMP_RATIO = r'r_T=\frac{T_2}{T_1}'
SPEED_RATIO = r'r_V=\sqrt{r_T}'
FUEL_RATIO = r'r_c=\frac{c_1}{c_2}'
RANGE_RATIO = r'\frac{R_2}{R_1}=r_V r_c'


def draft(source):
    assert source['stem'].startswith(PREFIX)
    match = PATTERN.search(source['stem'])
    assert match, source['id']
    t1, t2, c1, c2 = map(Decimal, match.groups())
    assert min(t1, t2, c1, c2) > 0
    with localcontext() as ctx:
        ctx.prec = 28
        temp = t2 / t1
        speed = temp.sqrt()
        fuel = c1 / c2
        final = speed * fuel
        answer = Decimal(source['options'][source['answer']].split()[0])
        assert abs(final - answer) < Decimal('0.0001'), (source['id'], final, answer)
        # Intermediate values are explicitly rounded in both the prompt and the
        # checked answer; the original final options still have a unique nearest.
        temp_display = temp.quantize(Decimal('.000001'))
        speed_display = speed.quantize(Decimal('.000001'))
        fuel_display = fuel.quantize(Decimal('.000001'))
        shown_final = speed_display * fuel_display
        distances = sorted((abs(shown_final - Decimal(x.split()[0])), i)
                           for i, x in enumerate(source['options']))
        assert distances[0][1] == source['answer'] and distances[0][0] < distances[1][0]

        def question(suffix, stem, value, latex, prerequisite):
            values = [value, value + Decimal('.1'), value - Decimal('.1'), value + Decimal('.2')]
            options = [str(v.quantize(Decimal('.000001'))) for v in values]
            assert len(set(options)) == 4
            return dict(id=source['id'] + suffix, type='choice', difficulty=3,
                        stem=stem, options=options, answer=0,
                        explanation=options[0],
                        formula_hint={'latex': latex, 'prerequisite': prerequisite})

        return [
            question('-TEMP', f'The initial temperature is {t1} K and the final temperature is {t2} K. What is the final-to-initial temperature ratio?', temp, TEMP_RATIO, 'BREGUET-TEMP-RATIO'),
            question('-SPEED', f'The temperature ratio is {temp_display}. At equal Mach, what is the speed ratio?', temp_display.sqrt(), SPEED_RATIO, 'BREGUET-SPEED-RATIO'),
            question('-FUEL', f'The initial thrust-specific fuel consumption is {c1} and the final value is {c2}. What is the initial-to-final coefficient ratio?', fuel, FUEL_RATIO, 'BREGUET-FUEL-RATIO'),
            dict(id=source['id'], type='choice', difficulty=3,
                 stem=f'At equal pressure, Mach, weight, area, polar and mass ratio, the speed ratio is {speed_display} and the inverse consumption ratio is {fuel_display}. What is the range ratio?',
                 options=list(source['options']), answer=source['answer'],
                 explanation=f'{speed_display} × {fuel_display} = {shown_final:.6f}; the closest option is {source["options"][source["answer"]]}.',
                 formula_hint={'latex': RANGE_RATIO, 'prerequisite': 'BREGUET-RANGE-RATIO'})]
