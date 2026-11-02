"""Verify staged trapezoidal wing calculations and prerequisite ordering."""
import json,math,re
from pathlib import Path
from course_adapter import lesson_questions
root=Path(__file__).resolve().parents[1]
bank={q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
ids=('TA1-0062-D2','TA1-0108-D2','TA1-0220-D2','TA1-0315-D2','TA1-0383-D2','TA1-0407-D2','TA1-0556-D2','TA1-0566-D2')
intro=lesson_questions([bank[ids[0]]]);assert intro[0]['id']=='WING-QUANTITIES' and intro[0]['type']=='matching'
assert [q['id'] for q in intro[1:10]]==['WING-SPAN-WORDS','WING-SPAN-NAMED','WING-SPAN','WING-DENOM-WORDS','WING-DENOM-NAMED','WING-DENOM','WING-ROOT-WORDS','WING-ROOT-NAMED','WING-ROOT']
for qid in ids:
 q=bank[qid];m=re.search(r'area (\d+(?:\.\d+)?) m², aspect ratio (\d+(?:\.\d+)?) and taper ratio lambda=(\d+(?:\.\d+)?)',q['stem']);area,ar,taper=map(float,m.groups());span=math.sqrt(area*ar);denom=span*(1+taper);expected=2*area/denom
 steps=lesson_questions([q]);a,b,c=steps[-3:];assert [x['id'] for x in (a,b,c)]==[qid+'-S1',qid+'-S2',qid]
 assert abs(float(a['options'][a['answer']].split()[0])-span)<.000001
 assert abs(float(b['options'][b['answer']].split()[0])-denom)<.000002
 assert abs(float(c['options'][c['answer']].split()[0])-expected)<.000051
 assert [x['formula_hint']['prerequisite'] for x in (a,b,c)]==['WING-SPAN','WING-DENOM','WING-ROOT']
 assert all(len(x['stem'])<160 and len(set(x['options']))==4 and x.get('rich_text') for x in (a,b,c))
print('PASS: eight wing-geometry problems, named prerequisites and exact answers; Android UI remains unverified.')
