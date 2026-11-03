"""Arithmetic and source identity checks only; no claim of lesson acceptance."""
import json
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
        assert step['answer']==0 and len(set(step['options']))==4
        assert abs(float(step['options'][0].split()[0])-step['expected'])<= max(1e-9,abs(step['expected'])*1e-9)
        assert step['formula_hint']['latex'] and step['formula_hint']['prerequisite']
assert counts=={'range':10,'payload':10},counts
print('PASS: 20 source identities, choices and intermediate arithmetic; draft is not integrated or Android validated.')
