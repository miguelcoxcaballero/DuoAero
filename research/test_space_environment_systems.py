"""Check source-reviewed environment distinctions; no runtime claim."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from course_adapter import session
source=json.loads((root/'research/midterm2_space_environment_systems.json').read_text())
qs=source['questions'];assert source['status']=='draft_not_connected_to_course' and len(qs)==10
other=[]
for path in (root/'research').glob('midterm2_*.json'):
 if path.name!='midterm2_space_environment_systems.json':other.extend(json.loads(path.read_text()).get('questions',[]))
assert len({q['id'] for q in qs})==10 and not {q['id'] for q in qs}&{q['id'] for q in other}
answers=['Natural buoyancy-driven convection is greatly reduced','Reduced loading can contribute to muscle and bone loss',
 'Help prevent the astronaut or tools drifting away from the spacecraft','Material can outgas or sublime',
 'Shielding and mission planning','Temperature changes can cause differential expansion and contraction',
 'Convert part of radioactive decay heat into electrical power','It can reduce resupply needs but does not recover everything perfectly',
 'By electrolysis of water','Satellite and ground clocks accumulate different timing effects']
for q,expected in zip(qs,answers):
 assert q['topic']=='3.2' and q['type']=='choice' and q['stem'].endswith('?')
 assert len(q['options'])==len(set(q['options']))==4 and q['options'][q['answer']]==expected
 assert q['explanation'] and not any(k in q for k in ('url','drive_id','source_excerpt'))
assert {q['answer'] for q in qs}=={0,1,2,3}
assert [m['id'] for m in session(qs,'space-environment-systems')['challenges']]==[q['id'] for q in qs]
print('PASS: ten isolated environment and life-support distinctions; native UI and course integration remain pending.')
