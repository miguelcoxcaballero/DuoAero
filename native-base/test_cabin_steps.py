"""Recalculate ten staged cabin problems from their original source values."""
import json
import re
from decimal import Decimal
from pathlib import Path
from course_adapter import lesson_questions
from math_notation import parts

root=Path(__file__).resolve().parents[1]
bank=json.loads((root/'app/assets/questions.json').read_text())
family=[q for q in bank if 'exp[-g(h-11000)/(RT)]' in q.get('stem','')]
assert len(family)==10
for index,q in enumerate(family):
    m=re.search(r'Cabin pressure is (\d+) Pa and maximum pressure differential is (\d+) Pa.*?W=([0-9.e+]+) N and S=(\d+) m² flies at Mach (\d+(?:\.\d+)?)',q['stem'])
    cabin,difference,weight,area,mach=map(Decimal,m.groups())
    p=cabin-difference
    dynamic=Decimal('.7')*p*mach*mach
    original=Decimal(q['options'][q['answer']])
    assert abs(weight/(dynamic*area)-original)<Decimal('.000006'),q['id']
    steps=lesson_questions([q],teach_words=True)
    questions=[s for s in steps if s.get('type')=='choice']
    assert len(questions)==(3 if index==1 else 4)
    assert all(len(s['stem'])<160 and len(set(s['options']))==4 for s in questions)
    assert Decimal(questions[0]['options'][questions[0]['answer']].split()[0])==p
    q_step=questions[-2]
    assert {'latex':r'\gamma=1.4'} in parts(q_step['stem'])
    shown=Decimal(q_step['options'][q_step['answer']].split()[0])
    assert abs(shown-dynamic)<Decimal('.006')
    last=questions[-1]
    assert last['id']==q['id'] and last['options'][last['answer']]==q['options'][q['answer']]
    assert abs(weight/(shown*area)-original)<Decimal('.000006')
    assert all(s.get('formula_hint',{}).get('prerequisite','').startswith('CABIN-') for s in questions)
    if index==0:
        for name in ('CABIN-PRESSURE-FORMULA','CABIN-MACH-PRESSURE','CABIN-WING-LOADING'):
            ids=[s['id'] for s in steps]
            assert ids.index(name+'-WORDS') < ids.index(name+'-NAMED-ALL') < ids.index(name+'-NAMED') < ids.index(name) < ids.index(questions[0]['id'])
print('PASS: ten original cabin answers match independently recomputed short steps; Android UI and touch still require validation.')
