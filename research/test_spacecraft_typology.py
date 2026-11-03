"""Review of mission roles; this does not establish device or course acceptance."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from course_adapter import session
source=json.loads((root/'research/midterm2_spacecraft_typology.json').read_text())
qs=source['questions'];assert source['status']=='draft_not_connected_to_course' and len(qs)==10
assert len({q['id'] for q in qs})==10
other=[]
for path in (root/'research').glob('midterm2_*.json'):
 if path.name!='midterm2_spacecraft_typology.json':other.extend(json.loads(path.read_text()).get('questions',[]))
assert not {q['id'] for q in qs}&{q['id'] for q in other}
expected=['Flyby','It enters an orbit around the target body','Reduced solar generation and cooling',
 'Earth occultation by the target body','Measure atmospheric conditions during descent',
 'To protect it from entry heating','An atmospheric balloon',
 'It is designed to enter the surface through impact',
 'Signals can take minutes to travel between Earth and Mars',
 'An inhabited orbital structure supported by visiting transport vehicles']
for q,answer in zip(qs,expected):
 assert q['topic']=='3.3' and q['type']=='choice' and q['stem'].endswith('?')
 assert len(q['options'])==len(set(q['options']))==4 and q['options'][q['answer']]==answer
 assert q['explanation'] and not any(k in q for k in ('url','drive_id','source_excerpt'))
assert {q['answer'] for q in qs}=={0,1,2,3}
assert [m['id'] for m in session(qs,'space-typology')['challenges']]==[q['id'] for q in qs]
print('PASS: ten spacecraft mission distinctions and unique reviewed answer positions; Android and course integration remain pending.')
