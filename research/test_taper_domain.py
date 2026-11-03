"""Prevent algebraic taper solutions outside the physical chord domain."""
import json,math
from pathlib import Path
from taper_domain import bounds
bank=json.loads((Path(__file__).resolve().parents[1]/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
family=[q for q in bank if bounds(q) is not None]
assert len(family)==10
corrected=0;empty=0
for q in family:
 lower,upper=bounds(q);opts=q['options'];chosen=opts[q['answer']]
 assert len(opts)==len(set(opts))==4
 if lower<0:
  corrected+=1
  assert q.get('content_revision')==2 and 'lambda >= 0' in q['stem']
  assert q['rich_text']['stem'][0]['text'].startswith('Find the feasible taper-ratio interval width')
  assert any(r'\lambda\geq 0' in part.get('latex','') for part in q['rich_text']['stem'])
  assert any(r'\lambda_{\max}-\lambda_{\min}' in part.get('latex','') for part in q['rich_text']['stem'])
  assert any(r'\mathrm{kg}/\mathrm{m}^{3}' in part.get('latex','') for part in q['rich_text']['stem'])
  assert q['origin']['kind']=='practice'
  assert 'Intersect the taper bounds with a nonnegative tip chord' in q['steps']
  if upper<0:
   empty+=1;assert chosen=='No feasible taper ratio' and 'No taper ratio satisfies' in q['explanation']
  else:
   assert abs(float(chosen)-upper)<0.000006
   assert 'physical lower bound is 0' in q['explanation']
 else:
  assert lower>=0 and abs(float(chosen)-(upper-lower))<0.0001
 assert set(q['option_explanations'])==set(opts)
assert corrected==8 and empty==3,(corrected,empty)
print('PASS: 10 taper problems, five physical lower-bound corrections and three infeasible cases; Android pending.')
