"""Check reviewed column example and formula prerequisites; UI tested separately."""
import json, math, sys
from pathlib import Path
from course_adapter import lesson_questions, session
root=Path(__file__).resolve().parents[1]
bank={q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
original=bank['TA1-0961-D3'];parts=lesson_questions([original],teach_words=True)
for name in ('COLUMN-YIELD-FORMULA','COLUMN-FACTOR-FORMULA'):
    positions=[next(i for i,p in enumerate(parts) if p['id']==name+suffix) for suffix in ('-WORDS','-NAMED-ALL','-NAMED','')]
    assert positions==sorted(positions)
    named=parts[positions[1]];assert named['inline_latex'].count('___')==len(named['answer_blocks'])
r=.0062;section=math.pi*r*r;inertia=math.pi*r**4/4
capacity=math.pi**2*70e9*inertia/(.7*.57)**2;yield_load=225e6*section
expected=[capacity,yield_load,min(capacity,yield_load)/3800]
checks=[parts[-3],parts[-2],parts[-1]]
for q,value,tol in zip(checks,expected,[.1,1,.0001]):
    assert abs(float(q['options'][q['answer']].split()[0])-value)<tol,(q['id'],value)
    assert len(set(q['options']))==4 and len(q['stem'])<160
    assert 'latex' in q['rich_text']['explanation'][0]
assert [p['formula_hint']['prerequisite'] for p in checks]==['BOOK-V6-05-D2','COLUMN-YIELD-FORMULA','COLUMN-FACTOR-FORMULA']
plan=json.loads((root/'app/assets/lesson_plan.json').read_text())
seen=set()
for node in plan:
    for lesson in node['lessons']:
        for q in lesson_questions([bank[i] for i in lesson['ids']],teach_words=True):
            hint=q.get('formula_hint')
            if hint:assert hint['prerequisite'] in seen,(q['id'],hint)
            seen.add(q['id'])
session([original],original['id'],teach_words=True)
print('PASS: column formulas precede three checked numerical controls; Android UI unverified.')
