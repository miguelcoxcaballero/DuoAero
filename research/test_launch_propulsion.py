"""Check launch propulsion concepts without claiming device acceptance."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from course_adapter import session
source=json.loads((root/'research/midterm2_launch_propulsion.json').read_text())
qs=source['questions'];assert source['status']=='draft_not_connected_to_course' and len(qs)==10
other=[]
for path in (root/'research').glob('midterm2_*.json'):
 if path.name!='midterm2_launch_propulsion.json':other.extend(json.loads(path.read_text()).get('questions',[]))
assert len({q['id'] for q in qs})==10 and not {q['id'] for q in qs}&{q['id'] for q in other}
expected=['The exposed burning surface and propellant characteristics','Changing propellant flow to adjust thrust',
 'It must be stored at a very low temperature','The fuel and oxidizer ignite on contact',
 'There is no surrounding atmosphere to supply it','It can remain stable for long periods under suitable storage conditions',
 'Its mass and recovery propellant can reduce payload capability','Thermal and mechanical loads can wear components',
 'Re-entry and atmospheric flight can produce high heating','Planning transport and recovery at the landing location']
for q,correct in zip(qs,expected):
 assert q['topic']=='3.1' and q['type']=='choice' and q['stem'].endswith('?')
 assert len(q['options'])==len(set(q['options']))==4 and q['options'][q['answer']]==correct
 assert q['explanation'] and not any(k in q for k in ('url','drive_id','source_excerpt'))
assert 'bipropellant' in next(q for q in qs if q['id']=='M2-LV-015')['stem']
assert 'Thermal and mechanical loads' in next(q for q in qs if q['id']=='M2-LV-018')['explanation']
assert {q['answer'] for q in qs}=={0,1,2,3}
assert [m['id'] for m in session(qs,'launch-propulsion')['challenges']]==[q['id'] for q in qs]
print('PASS: ten isolated launch propulsion and recovery distinctions; native UI and course integration remain pending.')
