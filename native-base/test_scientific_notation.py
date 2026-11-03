"""Preserve explicit scientific notation as a single mathematical expression."""
import json,re
from pathlib import Path
from math_notation import parts
pattern=re.compile(r'(\d+(?:\.\d+)?|\.\d+)\s*×\s*10\s*\^([+-]?\d+)')
bank=json.loads((Path(__file__).resolve().parents[1]/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
found=0
for q in bank:
 for value in [q.get('stem',''),*q.get('options',[]),q.get('explanation','')]:
  value=str(value)
  for match in pattern.finditer(value):
   expected=match.group(1)+r'\times 10^{'+str(int(match.group(2)))+'}'
   assert any(expected in part.get('latex','') for part in parts(value)),(q['id'],value,expected)
   found+=1
assert found>=40
assert parts('A letter x and 10 cats.')==[{'text':'A letter x and 10 cats.'}]
assert parts('2 × 10^-5 kg/(N s)')==[{'latex':r'2\times 10^{-5}'},{'text':' kg/(N s)'}]
print(f'PASS: {found} explicit scientific-notation fields emit mathematical powers; native rendering remains unverified.')
