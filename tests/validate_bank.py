from pathlib import Path
import json,collections
root=Path(__file__).resolve().parents[1]
bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
nodes=json.loads((root/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
assert len(bank)==1200
assert collections.Counter(q['difficulty'] for q in bank)=={1:400,2:400,3:400}
assert collections.Counter(q['origin']['kind'] for q in bank)=={'exam':106,'reflection':21,'practice':1073}
assert {q['type'] for q in bank}=={'choice','multi','gap','matching','order'}
ids=[q['id'] for q in bank];assert len(set(ids))==1200
for q in bank:
 assert q['section']=='Midterm 1'
 if q['origin']['kind']=='exam':
  assert all(q['origin'].get(k) for k in ['date','number','title','url','source_excerpt','answer_basis'])
 if q['type'] in ['choice','multi']:assert len(q['options'])==4
assigned=[]
for node in nodes:
 assert 1<=len(node['lessons'])<=3
 for lesson in node['lessons']:
  assert 10<=len(lesson['ids'])<=20
  assigned+=lesson['ids']
assert collections.Counter(assigned)==collections.Counter(ids)
print('PASS: 1200 questions, 400/level, 106 exams, 21 reflections, all sources and full path coverage')
