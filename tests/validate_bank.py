from pathlib import Path
import json,collections,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'native-base'))
from course_adapter import lesson_questions
bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
nodes=json.loads((root/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
assert len(bank)==1200
assert collections.Counter(q['difficulty'] for q in bank)=={1:400,2:400,3:400}
assert collections.Counter(q['origin']['kind'] for q in bank)=={'exam':106,'reflection':21,'practice':1073}
assert {q['type'] for q in bank}=={'choice','multi','gap','matching','order','formula_blocks'}
ids=[q['id'] for q in bank];assert len(set(ids))==1200
for q in bank:
 assert q['section']=='Midterm 1'
 if q['origin']['kind']=='exam':
  assert all(q['origin'].get(k) for k in ['date','number','title','url','source_excerpt','answer_basis'])
 if q['type'] in ['choice','multi']:assert len(q['options'])==4
 if q['type']=='formula_blocks':
  assert q['answer_blocks'] and len(q['blocks'])==len(set(q['blocks']))
  assert all(term in q['blocks'] for term in q['answer_blocks'])
  assert q['origin']['kind']=='practice' and q['origin']['page']>0
  assert q['formula_latex']
assert sum(q['topic']=='2.6' for q in bank)==24
assigned=[]
by_id={q['id']:q for q in bank}
seen={}
formula_prerequisites=set()
for node in nodes:
 assert 1<=len(node['lessons'])<=3
 for lesson in node['lessons']:
  # One source question can expand into several reviewed native exercises.
  assert 1<=len(lesson['ids'])<=20
  expanded=lesson_questions([by_id[qid] for qid in lesson['ids']])
  native_expanded=lesson_questions([by_id[qid] for qid in lesson['ids']],teach_words=True)
  assert len(native_expanded)>=10
  expanded_ids=[q['id'] for q in expanded]
  assert 10<=len(expanded)<=20 and len(expanded)==len(set(expanded_ids))
  for question in expanded:
   qid=question['id']
   assert qid not in seen, ('duplicate expanded id',qid)
   hint=question.get('formula_hint')
   if hint:
    assert question['type']=='choice' and isinstance(hint.get('latex'),str) and hint['latex'].strip()
    prerequisites=[hint.get('prerequisite')]+hint.get('additional_prerequisites',[])
    assert len(prerequisites)==len(set(prerequisites)), (qid,prerequisites)
    for prerequisite in prerequisites:
     assert prerequisite in formula_prerequisites, (qid,prerequisite)
   seen[qid]=question['type']
   if question['type']=='formula_blocks':formula_prerequisites.add(qid)
   elif question['type']=='formula_named' and question.get('symbol_prerequisite') is True:
    assert len(question['answer_blocks'])==1 and question.get('formula_latex')
    answer=question['answer_blocks'][0]
    assert answer in question['blocks'] and (len(answer)==1 or answer in {'Δh','ΔT'})
    formula_prerequisites.add(qid)
  assigned+=lesson['ids']
assert collections.Counter(assigned)==collections.Counter(ids)
print('PASS: 1200 questions, 400/level, 106 exams, 21 reflections, all sources and full path coverage')
