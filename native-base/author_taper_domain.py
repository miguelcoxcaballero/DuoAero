"""Repair eight invalid practice problems without touching exam extracts."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'research'))
from taper_domain import bounds,repair
path=root/'app/assets/questions.json';text=path.read_text(encoding='utf-8-sig')
decoder=json.JSONDecoder();pos=text.index('[')+1;changes=[]
while True:
 while text[pos] in ' \t\r\n,':pos+=1
 if text[pos]==']':break
 q,end=decoder.raw_decode(text,pos)
 if bounds(q) and bounds(q)[0]<0:
  assert q['origin']['kind']=='practice' and q['id'].startswith('TA1-')
  fixed=repair(q);changes.append((pos,end,json.dumps(fixed,ensure_ascii=False,indent=2).replace('\n','\n  ')))
 pos=end
assert len(changes)==8,len(changes)
for start,end,replacement in reversed(changes):text=text[:start]+replacement+text[end:]
path.write_text(text,encoding='utf-8')
print('Revised eight practice questions with the physical taper domain.')
