"""Check the isolated lesson's sequence, calculations and native models."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'native-base'))
from course_adapter import session
from rocket_lesson import lesson

questions = lesson()
assert len(questions) == 11 and len({q['id'] for q in questions}) == 11
assert [q['type'] for q in questions] == ['gap','formula_named','formula_named','formula_named','choice','choice','gap','formula_named','formula_named','formula_named','choice']
for q in (questions[3],questions[9]):
    assert q['mathematical_blocks'] and not ({'+','-','×','÷',r'\ln'} & set(q['answer_blocks']))
    assert len(q['answer_blocks']) == 3
seen = set()
for q in questions:
    if q.get('formula_hint'):
        assert q['formula_hint']['prerequisite'] in seen
    seen.add(q['id'])
assert float(questions[4]['options'][questions[4]['answer']]) == 6000/2000
assert float(questions[10]['options'][questions[10]['answer']].split()[0]) == 3000*1.099
assert questions[5]['id']=='M2-ROCKET-IDEAL-ASSUMPTIONS' and 'no external forces' in questions[5]['options'][questions[5]['answer']]
assert 'effective exhaust speed' in questions[7]['answer_blocks'] and 'effective exhaust speed' in questions[8]['blocks']
native = session(questions, 'rocket-draft')
assert [q['id'] for q in native['challenges']] == [q['id'] for q in questions]
print('PASS: ideal-rocket lesson has eleven ordered native models and checked calculations; updated Android acceptance remains pending.')
