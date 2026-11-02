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
