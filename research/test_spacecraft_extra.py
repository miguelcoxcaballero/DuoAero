"""Check another isolated second-midterm concept draft."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from course_adapter import session
source=json.loads((root/'research/midterm2_spacecraft_extra.json').read_text())
qs=source['questions'];assert source['status']=='draft_not_connected_to_course' and len(qs)==10
assert len({q['id'] for q in qs})==10
assert {q['answer'] for q in qs} == {0,1,2,3}
for q in qs:
 assert q['topic']=='3.3' and q['type']=='choice' and q['stem'].endswith('?')
 assert len(q['options'])==len(set(q['options']))==4 and 0<=q['answer']<4
 assert q['explanation'] and not any(k in q for k in ('url','drive_id','source_excerpt'))
assert [m['id'] for m in session(qs,'extra-spacecraft')['challenges']]==[q['id'] for q in qs]
print('PASS: ten isolated spacecraft concepts; editorial, Android and production-path acceptance remain pending.')
