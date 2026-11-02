"""Author checked, short steps for the ten cabin/ISA lift calculations.

The source stems and correct options remain in the bank. This script adds
reviewable native lesson steps; it does not change the private source fields.
"""
import json
import re
from decimal import Decimal
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'app/assets/questions.json'
original_text = path.read_text(encoding='utf-8-sig')
bank = json.loads(original_text)
family = [q for q in bank if 'exp[-g(h-11000)/(RT)]' in q.get('stem', '')]
assert len(family) == 10

formulas = [
    dict(id='CABIN-PRESSURE-FORMULA', type='formula_blocks', difficulty=1,
         stem='Complete the outside-pressure formula', prefix='p =',
         blocks=['p_c','−','Δp','+','p'], answer_blocks=['p_c','−','Δp'],
         formula_latex=r'p=p_c-\Delta p', explanation=r'p=p_c-\Delta p', literal_operator_blocks=True),
    dict(id='CABIN-MACH-PRESSURE', type='formula_blocks', difficulty=1,
         stem='Complete dynamic pressure using Mach', prefix='q = ½ γ',
         blocks=['p','M²','M','S','T'], answer_blocks=['p','M²'],
         formula_latex=r'q=\frac12\gamma pM^2', explanation=r'q=\frac12\gamma pM^2'),
    dict(id='CABIN-WING-LOADING', type='formula_blocks', difficulty=1,
         stem='Complete the level-flight wing-loading formula', prefix=r'\frac{W}{S} = q',
         blocks=['C_L','C_D','M','V'], answer_blocks=['C_L'],
         formula_latex=r'\frac{W}{S}=qC_L', explanation=r'\frac{W}{S}=qC_L'),
]

def fmt(value, places):
    return f'{value:.{places}f}'

def choice(identifier, stem, values, unit, explanation, formula, prerequisite):
    options = [value + unit for value in values]
    assert len(options) == len(set(options)) == 4
    return dict(id=identifier, stem=stem, options=options, answer=0,
                explanation=explanation,
                formula_hint={'latex': formula, 'prerequisite': prerequisite})

for index, question in enumerate(family):
    match = re.search(r'Cabin pressure is (\d+) Pa and maximum pressure differential is (\d+) Pa.*?W=([0-9.e+]+) N and S=(\d+) m² flies at Mach (\d+(?:\.\d+)?)', question['stem'])
    assert match, question['id']
    cabin, differential, weight, area, mach = map(Decimal, match.groups())
    outside = cabin-differential
    square = (mach*mach).quantize(Decimal('.000001'))
    dynamic = (Decimal('.7')*outside*square).quantize(Decimal('.01'))
    original = Decimal(question['options'][question['answer']])
    assert abs(weight/(dynamic*area)-original) < Decimal('.000006'), question['id']
    prefix = question['id']
    steps = list(formulas) if index == 0 else []
    steps.append(choice(prefix+'-S1',
        f'At the limit, cabin pressure is {cabin} Pa and the pressure difference is {differential} Pa. What is outside pressure?',
        [str(outside),str(cabin+differential),str(cabin),str(differential)], ' Pa',
        f'{cabin} − {differential} = {outside} Pa.',r'p=p_c-\Delta p','CABIN-PRESSURE-FORMULA'))
    # One problem uses a single q formula calculation to keep its lesson at 20.
    if index != 1:
        steps.append(choice(prefix+'-S2', f'Mach number is {mach}. What is its square?',
            [fmt(square,6),fmt(mach,6),fmt(square*2,6),fmt(square/2,6)], '',
            f'{mach} × {mach} = {fmt(square,6)}.',r'q=\frac12\gamma pM^2','CABIN-MACH-PRESSURE'))
        dynamic_stem=f'Outside pressure is {outside} Pa and Mach squared is {fmt(square,6)}. For gamma = 1.4, what is dynamic pressure?'
    else:
        dynamic_stem=f'Outside pressure is {outside} Pa and Mach is {mach}. For gamma = 1.4, what is dynamic pressure?'
    steps.append(choice(prefix+'-S3', dynamic_stem,
        [fmt(dynamic,2),fmt(dynamic*2,2),fmt(dynamic/2,2),fmt(dynamic*Decimal('1.2'),2)], ' Pa',
        f'0.7 × {outside} × {fmt(square,6)} = {fmt(dynamic,2)} Pa.',
        r'q=\frac12\gamma pM^2','CABIN-MACH-PRESSURE'))
    steps.append(dict(id=prefix,
        stem=f'Weight is {weight} N, wing area is {area} m² and dynamic pressure is {fmt(dynamic,2)} Pa. What lift coefficient maintains level flight?',
        options=list(question['options']), answer=question['answer'],
        explanation=f'C_L = {weight} / ({fmt(dynamic,2)} × {area}) ≈ {question["options"][question["answer"]]}.',
        formula_hint={'latex':r'\frac{W}{S}=qC_L','prerequisite':'CABIN-WING-LOADING'}))
    question['lesson_steps'] = steps

updates={q['id']:q for q in family}
decoder=json.JSONDecoder(); offset=original_text.index('[')+1; edits=[]
while True:
    while original_text[offset] in ' \t\r\n,': offset+=1
    if original_text[offset]==']': break
    old,end=decoder.raw_decode(original_text,offset)
    if old['id'] in updates:
        edits.append((offset,end,json.dumps(updates[old['id']],ensure_ascii=False,indent=2).replace('\n','\n  ')))
    offset=end
assert len(edits)==10
for start,end,replacement in reversed(edits):
    original_text=original_text[:start]+replacement+original_text[end:]
path.write_text(original_text,encoding='utf-8')
print('Authored four short cabin calculations with three prior formulas for ten source questions.')
