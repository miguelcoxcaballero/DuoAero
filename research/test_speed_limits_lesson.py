"""Model and prerequisite order checks; Android rendering is separate."""
import json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'native-base'))
from course_adapter import session
from formula_exercises import math_latex
from speed_limits_steps import PREFIX
from speed_limits_lesson import first_case
bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
source=next(q for q in bank if q['stem'].startswith(PREFIX))
questions=first_case(source)
assert len(questions)==28 and len({q['id'] for q in questions})==28
assert [q['type'] for q in questions[:20]]==['gap','formula_named','formula_named','formula_named']*5
seen=set()
for q in questions:
    hint=q.get('formula_hint')
    if hint: assert hint['prerequisite'] in seen, q['id']
    seen.add(q['id'])
assert math_latex('q_allowed') == r'\textstyle q_{\mathrm{allowed}}'
assert math_latex('C_Lmax') == r'\textstyle C_{L,\max}'
models=session(questions,'speed-limits-draft')['challenges']
assert [m['id'] for m in models]==[q['id'] for q in questions]
print('PASS: five isolated word/named/symbol formula sequences precede eight calculation steps; split, Android and curriculum acceptance remain pending.')
