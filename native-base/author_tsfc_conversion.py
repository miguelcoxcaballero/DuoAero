"""Stage one reviewed TSFC conversion, preserving its original source ID."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'research'))
from tsfc_conversion_draft import draft
path=root/'app/assets/questions.json'
text=path.read_text(encoding='utf-8-sig')
decoder=json.JSONDecoder();pos=text.index('[')+1
while True:
    while text[pos] in ' \t\r\n,': pos+=1
    if text[pos]==']': raise ValueError('Source question missing')
    question,end=decoder.raw_decode(text,pos)
    if question['id']=='TA1-0173-F1': break
    pos=end
question['lesson_steps']=draft(question)
replacement=json.dumps(question,ensure_ascii=False,indent=2).replace('\n','\n  ')
path.write_text(text[:pos]+replacement+text[end:],encoding='utf-8')
plan_path=root/'app/assets/lesson_plan.json'
plan=json.loads(plan_path.read_text(encoding='utf-8-sig'))
node=next(n for n in plan if n['id']=='2.2-3-point-0')
old=next(l for l in node['lessons'] if l['id']=='2.2-3-point-0-lesson-0')
assert old['ids'].count(question['id'])==1
target=next(n for n in plan if n['id']=='2.2-3-point-1')
assert all(l['id']!='2.2-3-point-1-lesson-3' for l in target['lessons'])
old['ids'].remove(question['id']);node['ids'].remove(question['id']);target['ids'].append(question['id'])
target['lessons'].append({'id':'2.2-3-point-1-lesson-3','ids':[question['id']],
                          'name':target['name']+' · Lesson 4'})
plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Staged TSFC conversion and a new, uncredited lesson; device acceptance pending.')
