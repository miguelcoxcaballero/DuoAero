"""Check the fixed-condition temperature/lift exercise family."""
import json,re
from pathlib import Path
from course_adapter import lesson_questions
root=Path(__file__).resolve().parents[1]
bank={q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
ids=('TA1-0045-D2','TA1-0339-D2','TA1-0509-D2','TA1-0651-D2','TA1-0676-D2','TA1-0778-D2','TA1-0801-D2','TA1-0819-D2')
assert [q['id'] for q in lesson_questions([bank[ids[0]]])[:6]]==['LIFT-TEMP-RATIO-WORDS','LIFT-TEMP-RATIO-NAMED','LIFT-TEMP-RATIO','LIFT-TEMP-UPDATE-WORDS','LIFT-TEMP-UPDATE-NAMED','LIFT-TEMP-UPDATE']
for qid in ids:
 q=bank[qid];m=re.search(r'Temperature changes from (\d+) K to (\d+) K\. Its initial CL is (\d+(?:\.\d+)?)',q['stem']);a,b,cl=map(float,m.groups())
 steps=lesson_questions([q]);one,two=steps[-2:]
 assert [one['id'],two['id']]==[qid+'-S1',qid]
 assert abs(float(one['options'][one['answer']])-b/a)<.00000006
 assert abs(float(two['options'][two['answer']])-cl*b/a)<.000006
 assert one['formula_hint']['prerequisite']=='LIFT-TEMP-RATIO' and two['formula_hint']['prerequisite']=='LIFT-TEMP-UPDATE'
 assert all(len(x['stem'])<180 and len(set(x['options']))==4 and x.get('rich_text') for x in (one,two))
print('PASS: eight two-step calculations and two formula prerequisites; Android remains unverified.')
