"""Check the isolated circular-orbit draft before Android testing."""
import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'native-base'))
from course_adapter import session
from rich_question import choice_blob
from orbit_lesson import lesson

questions=lesson()
assert len(questions)==10 and len({q['id'] for q in questions})==10
assert [q['type'] for q in questions]==['gap','formula_named','formula_named','formula_named','choice']*2
for q in (questions[3],questions[8]):
    assert q['mathematical_blocks'] and not ({'+','-','×','÷',r'\pi'} & set(q['answer_blocks']))
seen=set()
for q in questions:
    if q.get('formula_hint'):
        assert q['formula_hint']['prerequisite'] in seen
    seen.add(q['id'])
assert abs(float(questions[4]['options'][questions[4]['answer']].split()[0])-2*3.1416*7000)<1e-8
assert r'\\pi' in json.dumps(choice_blob(questions[4]),ensure_ascii=False)
assert float(questions[9]['options'][questions[9]['answer']].split()[0])==42000/7
assert [q['id'] for q in session(questions,'orbit-draft')['challenges']]==[q['id'] for q in questions]
print('PASS: isolated circular-orbit lesson has ten ordered native models and checked calculations; no Android or course acceptance asserted.')
