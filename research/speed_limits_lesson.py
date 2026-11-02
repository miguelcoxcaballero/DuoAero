"""Isolated word/named/symbolic prerequisites for the limits draft.

The formula renderings and lesson distribution require native Android review.
"""
from speed_limits_steps import MACH_FACTOR, MACH_PRESSURE, LIMIT, LOAD, MASS, draft


def introduce(identifier, sentence, answer, distractors, latex, quantities, quantity_distractors, named_parts, symbols, symbol_parts, missing_after):
    word=dict(id=identifier+'-WORDS',type='gap',difficulty=1,
              stem='Complete the formula in words: '+sentence,answer=[answer],distractors=distractors,
              explanation=sentence.replace('___',answer),formula_word_symbols=True)
    named=dict(id=identifier+'-NAMED-ALL',type='formula_named',difficulty=1,
               stem='Complete the formula with quantities',inline_latex=named_parts,formula_latex=latex,
               answer_blocks=quantities,blocks=quantities+quantity_distractors,explanation=latex)
    single=dict(id=identifier+'-NAMED',type='formula_named',difficulty=1,
                stem='Complete the formula with a quantity',before_latex='',after_latex=missing_after,
                missing_latex=latex.split('=')[0],formula_latex=latex,
                answer_blocks=[quantities[0]],blocks=[quantities[0]]+quantity_distractors[:3],explanation=latex)
    symbolic=dict(id=identifier,type='formula_named',difficulty=1,
                  stem='Complete the formula with symbols',inline_latex=symbol_parts,formula_latex=latex,
                  answer_blocks=symbols,blocks=symbols+['T','h'],explanation=latex,mathematical_blocks=True)
    return [word,named,single,symbolic]


def prerequisites():
    return sum([
      introduce('LIMITS-MACH-FACTOR','The pressure factor is half the heat capacity ratio times ambient ___.',
        'pressure',['area','mass','temperature'],MACH_FACTOR,
        ['pressure factor','heat capacity ratio','ambient pressure'],['mass','area','temperature'],
        ['___','=',r'\frac12',r'\times','___',r'\times','___'],
        ['f','γ','p'],['___','=',r'\frac12',r'\times','___',r'\times','___'],r'=\frac{\gamma p}{2}'),
      introduce('LIMITS-MACH-PRESSURE','The Mach pressure limit is the pressure factor times Mach number ___.',
        'squared',['cubed','halved','unchanged'],MACH_PRESSURE,
        ['Mach pressure limit','pressure factor','Mach number'],['mass','area','temperature'],
        ['___','=','___',r'\times','___^2'],['q_M','f','M'],['___','=','___',r'\times','___^2'],r'=fM^2'),
      introduce('LIMITS-PRESSURE-MIN','The allowed dynamic pressure is the smaller of the pressure cap and the Mach pressure ___.',
        'limit',['area','temperature','mass'],LIMIT,
        ['allowed pressure','pressure cap','Mach pressure limit'],['mass','area','temperature'],
        ['___','=',r'\min','(','___',',','___',')'],['q_allowed','q_cap','q_M'],
        ['___','=',r'\min','(','___',',','___',')'],r'=\min(q_{\mathrm{cap}},q_M)'),
      introduce('LIMITS-MAX-WEIGHT','The maximum weight is pressure times wing area times maximum lift coefficient, divided by 1.25 ___.',
        'squared',['cubed','halved','unchanged'],LOAD,
        ['maximum weight','allowed pressure','wing area','max lift coefficient'],['mass','temperature','speed'],
        ['___','=','(', '___',r'\times','___',r'\times','___',')',r'\div',r'1.25^2'],
        ['W_max','q_allowed','S','C_Lmax'],['___','=','(', '___',r'\times','___',r'\times','___',')',r'\div',r'1.25^2'],
        r'=\frac{q_{\mathrm{allowed}}S C_{L,\max}}{1.25^2}'),
      introduce('LIMITS-MASS','Maximum mass equals maximum weight divided by gravitational ___.',
        'acceleration',['temperature','area','pressure'],MASS,
        ['maximum mass','maximum weight','gravity'],['temperature','area','speed'],
        ['___','=','___/___'],['m_max','W_max','g'],['___','=','___/___'],r'=\frac{W_{\max}}{g}')
    ],[])


def first_case(source):
    return prerequisites()+draft(source)
