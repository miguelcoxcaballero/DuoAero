"""Partial isolated introductions for the staged equal-Mach range draft.

The interactive square-root relationship is still missing; these sequences
alone do not make a valid lesson or justify course integration.
"""
from speed_limits_lesson import introduce
from breguet_ratio_steps import TEMP_RATIO,FUEL_RATIO,RANGE_RATIO


def prerequisites():
    questions = sum([
      introduce('BREGUET-TEMP-RATIO','The temperature ratio is the final absolute temperature divided by the ___ absolute temperature.',
        'initial',['highest','average','outside'],TEMP_RATIO,
        ['temperature ratio','final temperature','initial temperature'],['mass','area','pressure'],
        ['___','=','___/___'],['r_T','T_2','T_1'],['___','=','___/___'],r'=\frac{T_2}{T_1}'),
      introduce('BREGUET-FUEL-RATIO','The thrust-specific fuel consumption ratio is the initial coefficient divided by the ___ coefficient.',
        'final',['largest','average','outside'],FUEL_RATIO,
        ['thrust-specific fuel consumption ratio','initial thrust-specific fuel consumption','final thrust-specific fuel consumption'],['mass','area','pressure'],
        ['___','=','___/___'],['r_c','c_1','c_2'],['___','=','___/___'],r'=\frac{c_1}{c_2}'),
      introduce('BREGUET-RANGE-RATIO','At equal pressure and Mach, the range ratio is the speed ratio times the inverse thrust-specific fuel ___ ratio.',
        'consumption',['temperature','pressure','mass'],RANGE_RATIO,
        ['final range','initial range','speed ratio','thrust-specific fuel consumption ratio'],['mass','area','pressure'],
        ['___/___','=','___',r'\times','___'],['R_2','R_1','r_V','r_c'],['___/___','=','___',r'\times','___'],
        r'=R_1 r_V r_c')
    ],[])

    # The range equation has a ratio on the left. A single hole must replace
    # only one operand, not call the whole ratio "final range".
    single=next(q for q in questions if q['id']=='BREGUET-RANGE-RATIO-NAMED')
    single.update(before_latex=r'\frac{R_2}{R_1}=', after_latex=r'r_c',
                  missing_latex=r'r_V', answer_blocks=['speed ratio'],
                  blocks=['speed ratio','thrust-specific fuel consumption ratio','mass','area'])
    return questions
