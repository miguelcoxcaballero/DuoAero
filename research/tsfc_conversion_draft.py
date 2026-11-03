"""Isolated split of the original TSFC unit conversion; not in production.

The original asks for 20 g/(kN s) in kg/(N s). First convert the grams,
then account for the thousand newtons in one kilonewton. Both steps are
preceded by word, quantity and symbol exercises for the conversion factors.
"""
from speed_limits_lesson import introduce

GRAM = r'm_{\mathrm{kg}}=10^{-3}m_{\mathrm{g}}'
THRUST = r'F_{\mathrm{N}}=10^3F_{\mathrm{kN}}'
TSFC = r'c_{\mathrm{kg/(N\,s)}}=10^{-6}c_{\mathrm{g/(kN\,s)}}'
PER_NEWTON = r'c_{N}=c_{kN}\div 1000'


def draft(source):
    assert source['id']=='TA1-0173-F1' and source['options'][source['answer']]=='2.0 × 10^-5 kg/(N s)'
    teaching = introduce('TSFC-GRAM', 'Mass in kilograms is mass in grams multiplied by ___.',
        '0.001', ['1000','100','10'], GRAM,
        ['mass in kilograms','mass in grams'], ['thrust','time','pressure'],
        ['___','=','0.001',r'\times','___'], ['m_kg','m_g'],
        ['___','=','0.001',r'\times','___'], r'=10^{-3}m_{\mathrm g}')
    teaching += introduce('TSFC-THRUST', 'Thrust in newtons is thrust in kilonewtons multiplied by ___.',
        '1000', ['0.001','100','10'], THRUST,
        ['thrust in newtons','thrust in kilonewtons'], ['mass','time','pressure'],
        ['___','=','1000',r'\times','___'], ['F_N','F_kN'],
        ['___','=','1000',r'\times','___'], r'=10^3F_{\mathrm{kN}}')
    teaching += introduce('TSFC-PER-NEWTON',
        'Specific fuel consumption per newton equals consumption per kilonewton divided by ___.',
        '1000', ['0.001','100','10'], PER_NEWTON,
        ['specific fuel consumption per newton','specific fuel consumption per kilonewton'],
        ['mass','time','pressure'],
        ['___','=','___',r'\div','1000'], ['c_N','c_kN'],
        ['___','=','___',r'\div','1000'], r'=c_{\mathrm{kN}}\div1000')
    return teaching + [
        dict(id=source['id']+'-GRAM',type='choice',difficulty=1,
             stem='Convert 20 g to kilograms.',options=['0.02 kg','20 kg','2000 kg','0.2 kg'],answer=0,
             explanation='20 × 0.001 = 0.02 kg.',formula_hint={'latex':GRAM,'prerequisite':'TSFC-GRAM'}),
        dict(id=source['id'],type='choice',difficulty=1,
             stem='A consumption is 0.02 kg/(kN s). Divide by 1000 to express it in kg/(N s).',
             options=list(source['options']),answer=source['answer'],
             explanation='0.02 / 1000 = 0.00002 kg/(N s).',
             formula_hint={'latex':PER_NEWTON,'prerequisite':'TSFC-PER-NEWTON'})]
