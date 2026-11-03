"""Circular-orbit foundation used by the development release path."""

def lesson():
    def words(identifier, sentence, answer, distractors):
        return dict(id=identifier, type='gap', difficulty=1,
                    stem='Complete the formula in words: '+sentence,
                    answer=[answer], distractors=distractors,
                    explanation=sentence.replace('___',answer), formula_word_symbols=True)

    def named(identifier, formula, answers, distractors, pieces, stem='Complete the formula with quantities', symbols=False):
        return dict(id=identifier, type='formula_named', difficulty=1, stem=stem,
                    inline_latex=pieces, formula_latex=formula,
                    answer_blocks=answers, blocks=answers+distractors,
                    explanation=formula, mathematical_blocks=symbols)

    def single(identifier, formula, answer, distractors, after):
        return dict(id=identifier, type='formula_named', difficulty=1,
                    stem='Complete the formula with a quantity', before_latex='', after_latex=after,
                    missing_latex=formula.split('=')[0], formula_latex=formula,
                    answer_blocks=[answer], blocks=[answer]+distractors, explanation=formula)

    circumference = r'C=2\pi r'
    period = r'T=\frac{C}{v}'
    return [
        words('M2-ORBIT-CIRC-WORDS','The circumference of a circular orbit is two pi times its ___.','radius',['mass','temperature','pressure']),
        named('M2-ORBIT-CIRC-NAMED-ALL',circumference,['circumference','radius'],['mass','speed','area'],['___','=','2',r'\pi',r'\times','___']),
        single('M2-ORBIT-CIRC-NAMED',circumference,'circumference',['radius','mass','speed'],r'=2\pi r'),
        named('M2-ORBIT-CIRC',circumference,['C','r'],['T','v'],['___','=','2',r'\pi',r'\times','___'],'Complete the circumference formula with symbols',True),
        dict(id='M2-ORBIT-CIRC-CALC',type='choice',difficulty=1,
             stem='A circular orbit has a radius of 7000 km. Using pi = 3.1416, what is its circumference?',
             options=['43982.4 km','21991.2 km','14000 km','153938.4 km'],answer=0,
             explanation='2 × 3.1416 × 7000 = 43982.4 km.',
             formula_hint={'latex':circumference,'prerequisite':'M2-ORBIT-CIRC'}),
        words('M2-ORBIT-PERIOD-WORDS','For constant orbital speed, period equals distance around the orbit divided by ___.','speed',['mass','density','pressure']),
        named('M2-ORBIT-PERIOD-NAMED-ALL',period,['period','circumference','orbital speed'],['mass','density','pressure'],['___','=','___/___']),
        single('M2-ORBIT-PERIOD-NAMED',period,'period',['circumference','orbital speed','mass'],r'=\frac{C}{v}'),
        named('M2-ORBIT-PERIOD',period,['T','C','v'],['p','r'],['___','=','___/___'],'Complete the orbital period formula with symbols',True),
        dict(id='M2-ORBIT-PERIOD-CALC',type='choice',difficulty=1,
             stem='An orbit is 42000 km around and the constant orbital speed is 7 km/s. What is its period?',
             options=['6000 s','3000 s','7000 s','294000 s'],answer=0,
             explanation='42000 / 7 = 6000 s.',
             formula_hint={'latex':period,'prerequisite':'M2-ORBIT-PERIOD'}),
    ]
