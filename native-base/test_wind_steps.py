"""Check wind question arithmetic, teaching order and stable lesson identities.

This is a host check; original Android interaction still needs device testing.
"""
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import re
from course_adapter import lesson_questions
from formula_exercises import formula_challenge

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))}
plan = json.loads((root/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
ids = ['TA1-0092-D2', 'TA1-0120-D2', 'TA1-0130-D2',
       'TA1-0263-D2', 'TA1-0268-D2', 'TA1-0366-D2']
round4 = lambda n: n.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
pattern = re.compile(r'two legs of (\d+) km each\. Airspeed is (\d+) km/h and steady along-track wind is (\d+)')
tailwind_steps = lesson_questions([bank['TA1-0012-F1']])
assert [q['id'] for q in tailwind_steps] == ['WIND-TAILWIND-FORMULA',
    'WIND-TIME-FORMULA', 'WIND-TOTAL-FORMULA', 'TA1-0012-F1']
assert tailwind_steps[-1]['options'][tailwind_steps[-1]['answer']] == '280 km/h'
assert 250 + 30 == 280
for formula in (tailwind_steps[0], tailwind_steps[2]):
    assert formula['literal_operator_blocks'] is True
    input_data = formula_challenge(formula)['promptInputChallenge']['input']['expressionBuildInput']
    plus = next(c for c in input_data['dragChoices']
                if c['underlyingEntity'].get('entity', {}).get('variable', {}).get('algebraic', {}).get('name') == 'duoaero:+')
    assert plus['taggedTextElement']['text'] == r'duoaero-latex:\textstyle +'
    expected = input_data['gradingSpecification']['gradingRules'][0]['exactGrading'][0]['exactAnswer']['list']['values']
    assert any(v.get('variable', {}).get('algebraic', {}).get('name') == 'duoaero:+' for v in expected)
for qid in ids:
    original = bank[qid]
    match = pattern.search(original['stem'])
    assert match, qid
    distance, speed, wind = map(Decimal, match.groups())
    a = round4(distance / (speed - wind))
    b = round4(distance / (speed + wind))
    steps = lesson_questions([original])
    assert [q['id'] for q in steps] == [qid+'-S1', qid]
    assert Decimal(steps[0]['options'][steps[0]['answer']].split()[0]) == a
    assert Decimal(steps[1]['options'][steps[1]['answer']].split()[0]) == a+b
    assert steps[0]['formula_hint']['prerequisite'] == 'WIND-TIME-FORMULA'
    assert steps[1]['formula_hint']['prerequisite'] == 'WIND-TOTAL-FORMULA'
    assert all(len(set(q['options'])) == len(q['options']) and len(q['stem']) < 160 for q in steps)

seen = set()
for node in plan:
    for lesson in node['lessons']:
        expanded = lesson_questions([bank[qid] for qid in lesson['ids']])
        assert len(expanded) <= 20, lesson['id']
        for q in expanded:
            if q.get('formula_hint'):
                assert q['formula_hint']['prerequisite'] in seen, q['id']
            seen.add(q['id'])
assert {'WIND-TAILWIND-FORMULA','WIND-TIME-FORMULA','WIND-TOTAL-FORMULA'} <= seen
print('PASS: six wind problems, three taught formulas and stable lesson size; Android UI unverified.')
