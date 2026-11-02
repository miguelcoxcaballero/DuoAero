"""Check the staged warm-day approach calculation and its prerequisites."""
import json, math
from pathlib import Path
from course_adapter import lesson_questions
root=Path(__file__).resolve().parents[1]
bank=json.loads((root/'app/assets/questions.json').read_text())
q=next(q for q in bank if q['id']=='TA1-0806-D3')
a=lesson_questions([q],teach_words=True)
assert len(a)==19 and a[-1]['id']==q['id']
matching=next(x for x in a if x['id']=='APPROACH-STALL-QUANTITIES')
assert matching['type']=='matching' and len(matching['pairs'])==4
assert a.index(matching) < next(i for i,x in enumerate(a) if x['id']=='APPROACH-STALL-SQUARED-WORDS')
seen={'ISA-DENSITY'}
for item in a:
 if item.get('symbol_prerequisite'): seen.add(item['id'])
 if item.get('formula_hint'): assert item['formula_hint']['prerequisite'] in seen
 if item['type']=='choice':
  assert len(item['stem'])<170 and len(set(item['options']))==4
  assert item.get('rich_text')
p,t,r,w,area,cl=71906,281.95,287,43164,27,1.75
rho=p/(r*t); vs2=2*w/(rho*area*cl);vs=math.sqrt(vs2);approach=1.3*vs;kmh=3.6*approach
expected=(rho,vs2,vs,approach,kmh); tolerances=(.00001,.01,.001,.001,.01)
for step,value,tol in zip([x for x in a if x.get('formula_hint')],expected,tolerances):
 assert abs(float(step['options'][step['answer']].split()[0])-value)<tol,step['id']
for prefix in ('APPROACH-STALL-SQUARED','APPROACH-STALL-ROOT','APPROACH-SPEED','APPROACH-CONVERT'):
 indices=[next(i for i,x in enumerate(a) if x['id']==prefix+suffix) for suffix in ('-WORDS','-NAMED','')]
 assert indices==sorted(indices)
for name in ('APPROACH-SPEED-NAMED','APPROACH-CONVERT-NAMED'):
 item=next(x for x in a if x['id']==name)
 assert item['inline_latex'].count('___') == len(item['answer_blocks']) == 2
 assert r'\times' in item['inline_latex']
print('PASS: 19 staged exercises, formula order and numerical answers; Android UI remains unverified.')
