"""Check the isolated lesson's sequence, calculations and native models."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'native-base'))
from course_adapter import session
from rocket_lesson import lesson

questions = lesson()
assert len(questions) == 10 and len({q['id'] for q in questions}) == 10
assert [q['type'] for q in questions] == ['gap','formula_named','formula_named','formula_named','choice']*2
seen = set()
for q in questions:
    if q.get('formula_hint'):
        assert q['formula_hint']['prerequisite'] in seen
    seen.add(q['id'])
assert float(questions[4]['options'][questions[4]['answer']]) == 6000/2000
assert float(questions[9]['options'][questions[9]['answer']].split()[0]) == 3000*1.099
native = session(questions, 'rocket-draft')
assert [q['id'] for q in native['challenges']] == [q['id'] for q in questions]
print('PASS: isolated ideal-rocket lesson has ten ordered native models and checked calculations; no Android or course acceptance asserted.')
