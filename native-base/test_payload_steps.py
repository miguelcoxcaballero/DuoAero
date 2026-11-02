"""Check split payload limits against the original physical constraints."""
import json
import re
from pathlib import Path
from course_adapter import lesson_questions, session

root=Path(__file__).resolve().parents[1]
bank=json.loads((root/'app/assets/questions.json').read_text())
family=[q for q in bank if q.get('stem','').startswith('An aircraft has OEM=')
        and 'maximum landing mass=' in q['stem'] and 'maximum payload=' in q['stem']]
assert len(family)==8
pattern=re.compile(r'OEM=(\d+) kg, MTOM=(\d+) kg, maximum landing mass=(\d+) kg and maximum payload=(\d+) kg.*?with (\d+) kg of fuel and burns (\d+) kg')
for index,q in enumerate(family):
    empty,takeoff,landing,structural,fuel,burned=map(int,pattern.search(q['stem']).groups())
    remaining=fuel-burned
    takeoff_nonpayload=empty+fuel
    landing_nonpayload=empty+remaining
    expected=[remaining,takeoff_nonpayload,takeoff-takeoff_nonpayload,
              landing_nonpayload,landing-landing_nonpayload]
    steps=q['lesson_steps'][-6:]
    for step,value in zip(steps[:5],expected):
        assert int(step['options'][step['answer']].split()[0])==value
        assert step['formula_hint']['prerequisite']
    final=min(structural,expected[2],expected[4])
    assert int(q['options'][q['answer']].split()[0])==final
    assert steps[-1]['id']==q['id'] and steps[-1]['options']==q['options']
    expanded=lesson_questions([q],teach_words=True)
    assert len(expanded)==(14 if index==0 else 6)
    assert len(session([q],'payload-diagnostic',teach_words=True)['challenges'])==len(expanded)
print('PASS: eight payload constraints and 48 short steps checked; Android layout, touch and migration remain unverified.')
