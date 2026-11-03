"""Arithmetic and source identity checks only; no claim of lesson acceptance."""
import json
import re
from decimal import Decimal
from pathlib import Path
from audit_jet_families import audit
from jet_family_steps import draft

bank=json.loads((Path(__file__).resolve().parents[1]/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
counts={'range':0,'payload':0}
for source in bank:
    result=audit(source)
    if result is None: continue
    family, expected, _=result
    counts[family]+=1
    steps=draft(source)
    assert steps[-1]['id']==source['id']
    assert steps[-1]['options']==source['options'] and steps[-1]['answer']==source['answer']
    assert len({s['id'] for s in steps})==len(steps)
    assert abs(steps[-1]['expected']-expected)<1e-8
    for step in steps[:-1]:
        assert 0 <= step['answer'] < 4 and len(set(step['options']))==4
        assert abs(float(step['options'][step['answer']].split()[0])-step['expected'])<= max(1e-9,abs(step['expected'])*1e-9)
        assert step['formula_hint']['latex'] and step['formula_hint']['prerequisite']
        match=re.search(r'Calculate ([0-9.eE+-]+) ([+×÷-]) ([0-9.eE+-]+)\.',step['stem'])
        if match:
            a,b=Decimal(match[1]),Decimal(match[3])
            independent={'+':lambda:a+b,'-':lambda:a-b,'×':lambda:a*b,'÷':lambda:a/b}[match[2]]()
            shown=Decimal(step['options'][step['answer']].split()[0])
            assert abs(shown-independent)<=max(Decimal('1e-9'),abs(independent)*Decimal('1e-9')),step['id']

assert counts=={'range':10,'payload':10},counts
positions={step['answer'] for q in bank if audit(q) for step in draft(q)[:-1]}
assert positions=={0,1,2,3},positions
for q in bank:
 if audit(q) and audit(q)[0]=='range':
  assert draft(q)[-1]['formula_hint']['prerequisite']=='JET-KM'
for q in bank:
 if audit(q):
  for step in draft(q)[:-1]:
   if 'rich_text' in step:
    assert any('latex' in p for p in step['rich_text']['stem'])

print('PASS: 20 source identities, choices and intermediate arithmetic; draft is not integrated or Android validated.')
