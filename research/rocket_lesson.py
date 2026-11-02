"""Isolated second-midterm rocket calculation draft; not production content.

The ideal rocket equation neglects external forces and assumes constant
effective exhaust speed. Keep its teaching and hint before the calculation.
"""

def lesson():
    def words(identifier, stem, answer, distractors):
        return dict(id=identifier, type='gap', difficulty=1,
                    stem='Complete the formula in words: '+stem, answer=[answer],
                    distractors=distractors, explanation=stem.replace('___', answer),
                    formula_word_symbols=True)

    def named(identifier, formula, answers, distractors, pieces):
        return dict(id=identifier, type='formula_named', difficulty=1,
                    stem='Complete the formula with quantities', inline_latex=pieces,
                    formula_latex=formula, answer_blocks=answers, blocks=answers+distractors,
                    explanation=formula)

    def one(identifier, formula, answer, distractors, after):
        return dict(id=identifier, type='formula_named', difficulty=1,
                    stem='Complete the formula with a quantity', before_latex='', after_latex=after,
                    missing_latex=formula.split('=')[0], formula_latex=formula,
                    answer_blocks=[answer], blocks=[answer]+distractors, explanation=formula)

    ratio = r'r=\frac{m_i}{m_f}'
    rocket = r'\Delta v=v_e\ln r'
    return [
        words('M2-ROCKET-RATIO-WORDS', 'Initial mass divided by final mass is the mass ___.',
              'ratio', ['force','temperature','area']),
        named('M2-ROCKET-RATIO-NAMED-ALL', ratio,
              ['mass ratio','initial mass','final mass'], ['pressure','speed','area'],
              ['___','=','___/___']),
        one('M2-ROCKET-RATIO-NAMED', ratio, 'mass ratio', ['initial mass','final mass','pressure'], r'=\frac{m_i}{m_f}'),
        dict(id='M2-ROCKET-RATIO', type='formula_blocks', difficulty=1,
             stem='Complete the mass ratio', prefix='r =',
             blocks=[r'\frac{m_i}{m_f}',r'\frac{m_f}{m_i}',r'm_i+m_f',r'm_i-m_f'],
             answer_blocks=[r'\frac{m_i}{m_f}'], formula_latex=ratio, explanation=ratio),
        dict(id='M2-ROCKET-RATIO-CALC', type='choice', difficulty=1,
             stem='Initial mass is 6000 kg and final mass is 2000 kg. What is the mass ratio?',
             options=['3','0.33','4','2'], answer=0, explanation='6000 / 2000 = 3.',
             formula_hint={'latex':ratio,'prerequisite':'M2-ROCKET-RATIO'}),
        words('M2-ROCKET-DELTA-WORDS', 'Ideal velocity change equals effective exhaust speed times the natural logarithm of the mass ___.',
              'ratio',['pressure','temperature','area']),
        named('M2-ROCKET-DELTA-NAMED-ALL', rocket,
              ['velocity change','exhaust speed','mass ratio'], ['pressure','temperature','area'],
              ['___','=','___',r'\times',r'\ln','___']),
        one('M2-ROCKET-DELTA-NAMED', rocket, 'velocity change', ['exhaust speed','mass ratio','pressure'], r'=v_e\ln r'),
        dict(id='M2-ROCKET-DELTA', type='formula_blocks', difficulty=1,
             stem='Complete the ideal rocket equation', prefix=r'\Delta v =',
             blocks=[r'v_e',r'\ln r',r'1/r',r'm_f'], answer_blocks=[r'v_e',r'\ln r'],
             formula_latex=rocket, explanation=rocket),
        dict(id='M2-ROCKET-DELTA-CALC', type='choice', difficulty=1,
             stem='Effective exhaust speed is 3000 m/s and the natural logarithm of mass ratio is 1.099. What is ideal velocity change?',
             options=['3297 m/s','3000 m/s','1099 m/s','2729 m/s'], answer=0,
             explanation='3000 × 1.099 = 3297 m/s.',
             formula_hint={'latex':rocket,'prerequisite':'M2-ROCKET-DELTA'}),
    ]
