"""Check matched-Reynolds scaling and retained source answers."""
import json
import re
from decimal import Decimal
from pathlib import Path
from course_adapter import lesson_questions, session

root=Path(__file__).resolve().parents[1]
bank=json.loads((root/'app/assets/questions.json').read_text())
family=[q for q in bank if q.get('stem','').startswith('A wind-tunnel model must match the Reynolds number')]
assert len(family)==7
pattern=re.compile(r'chord ([0-9.]+) m.*?rho2/rho1=([0-9.]+), V2/V1=([0-9.]+), mu2/mu1=([0-9.]+)\.')
for index,q in enumerate(family):
    reference,rho,speed,viscosity=map(Decimal,pattern.search(q['stem']).groups())
    steps=q['lesson_steps'][-3:]
    product=rho*speed;factor=viscosity/product
    assert abs(Decimal(steps[0]['options'][steps[0]['answer']])-product)<Decimal('.00000051')
    assert abs(Decimal(steps[1]['options'][steps[1]['answer']])-factor)<Decimal('.00000051')
    answer=Decimal(q['options'][q['answer']].split()[0])
    assert abs(answer-reference*factor)<Decimal('.000051')
    displayed=reference*Decimal(f'{factor:.6f}')
    numeric=[Decimal(value.split()[0]) for value in q['options']]
    assert min(range(len(numeric)),key=lambda i:abs(numeric[i]-displayed))==q['answer']
    assert steps[-1]['id']==q['id'] and steps[-1]['options']==q['options']
    assert [s['formula_hint']['prerequisite'] for s in steps]==['REYNOLDS-SCALE-FORMULA','REYNOLDS-SCALE-FORMULA','REYNOLDS-CHORD-FORMULA']
    expanded=lesson_questions([q],teach_words=True)
    assert len(expanded)==(15 if index==0 else 3)
    assert len(session([q],'reynolds-diagnostic',teach_words=True)['challenges'])==len(expanded)
print('PASS: seven Reynolds scaling answers and 21 short calculations checked; Android and migration remain unverified.')
