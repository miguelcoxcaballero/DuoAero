"""Check the authored isothermal prerequisite and 20 kPa example.

This verifies course data and arithmetic, not native Android rendering.
"""
from decimal import Decimal
import base64
import json
from pathlib import Path
from course_adapter import lesson_questions, session
from rich_question import choice_blob

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root/'app/assets/questions.json').read_text())}
plan = json.loads((root/'app/assets/lesson_plan.json').read_text())
lesson = next(lesson for node in plan for lesson in node['lessons']
              if lesson['id'] == '2.1-5-point-0-lesson-0')
expanded = lesson_questions([bank[qid] for qid in lesson['ids']], teach_words=True)
ids = [q['id'] for q in expanded]
formula_id = 'ISA-ISOTHERMAL-FORMULA'
word, named, formula, calculation = [next(q for q in expanded if q['id']==qid)
    for qid in (formula_id+'-WORDS', formula_id+'-NAMED', formula_id, 'TA1-0182-F1')]
assert ids.index(word['id']) < ids.index(named['id']) < ids.index(formula_id) < ids.index(calculation['id'])
assert named['before_latex'] + named['missing_latex'] + named['after_latex'] == formula['formula_latex'] == r'p=p_b e^{-X}'
assert named['answer_blocks'] == ['pressure']
assert formula['answer_blocks'] == [r'p_b e^{-X}']
assert calculation['formula_hint'] == {'latex':r'p=p_b e^{-X}', 'prerequisite':formula_id}
assert Decimal('20') * Decimal('0.50') == Decimal('10')
assert calculation['options'][calculation['answer']] == '10 kPa'
later = lesson_questions([bank['TA1-0397-D2']])
first_step = later[0]
assert first_step['id'] == 'TA1-0397-D2-S1'
assert first_step['formula_hint'] == calculation['formula_hint']
assert (Decimal('22.63') * Decimal('0.854')).quantize(Decimal('0.01')) == Decimal('19.33')
assert first_step['options'][first_step['answer']] == '19.33 kPa'
ratio_lesson = next(lesson for node in plan for lesson in node['lessons']
                    if lesson['id'] == '2.1-5-point-1-lesson-0')
ratio_questions = lesson_questions([bank[qid] for qid in ratio_lesson['ids']], teach_words=True)
ratio_ids = [q['id'] for q in ratio_questions]
for prior, following in zip(('ISA-PRESSURE-RATIO-WORDS','ISA-PRESSURE-RATIO-NAMED',
                             'ISA-PRESSURE-RATIO','TA1-0463-D2-S1'),
                            ('ISA-PRESSURE-RATIO-NAMED','ISA-PRESSURE-RATIO',
                             'TA1-0463-D2-S1','TA1-0463-D2')):
    assert ratio_ids.index(prior) < ratio_ids.index(following)
new_steps = lesson_questions([bank['TA1-0463-D2']])
assert (Decimal('22.63') * Decimal('0.7528')).quantize(Decimal('0.01')) == Decimal('17.04')
assert (Decimal('17.04') / Decimal('30.28')).quantize(Decimal('0.001')) == Decimal('0.563')
assert new_steps[1]['options'][new_steps[1]['answer']] == '17.04 kPa'
assert new_steps[2]['options'][new_steps[2]['answer']] == '0.563'
assert new_steps[1]['formula_hint']['prerequisite'] == formula_id
assert new_steps[2]['formula_hint']['prerequisite'] == 'ISA-PRESSURE-RATIO'
assert all(len(set(q['options'])) == len(q['options']) for q in new_steps[1:])
blob = json.loads(choice_blob(calculation, include_formula_hint=True)['challengeBlob'])
assert 'grading_function' in blob
original = json.loads((root/'native-base/session-history/1.3.7.json').read_text())
old_ids = [q['id'] for q in original[lesson['id']]['challenges']]
assert 'TA1-0209' in old_ids and formula_id not in old_ids
assert 'TA1-0209' not in ids and 'TA1-0182-F1' in ids
native = session([bank[qid] for qid in lesson['ids']], lesson['id'], teach_words=True)
assert [q['id'] for q in native['challenges']] == ids
named_native = next(q for q in native['challenges'] if q['id']==formula_id+'-NAMED')
text = named_native['promptInputChallenge']['prompt']['body']['taggedTextElement']['text']
parts = json.loads(base64.b64decode(text.split('duoaero-gap:',1)[1]))
assert parts == ['___', r'duoaero-math:formula:\textstyle =p_b e^{-X}']
print('PASS: reviewed isothermal formula before the pressure calculation; 20 kPa × 0.50 = 10 kPa. Android UI remains unverified.')
