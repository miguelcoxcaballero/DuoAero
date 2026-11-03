"""Arithmetic check of draft wind steps, not a course or device test."""
import json,re,sys
from decimal import Decimal
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from wind_budget_steps import values,draft,FORMULAS
from course_adapter import challenge
bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
cases=[q for q in bank if values(q)];assert len(cases)==10
positions=set()
for source in cases:
 steps=draft(source);assert len(steps)==16 and steps[-1]['id']==source['id']
 assert steps[-1]['options']==source['options'] and steps[-1]['answer']==source['answer']
 for step in steps[:-1]:
  positions.add(step['answer']);assert len(set(step['options']))==4
  match=re.search(r'Calculate ([0-9.eE+-]+) ([+×÷-]) ([0-9.eE+-]+)\.',step['stem']);assert match
  a,b=Decimal(match[1]),Decimal(match[3])
  expected={'+':lambda:a+b,'-':lambda:a-b,'×':lambda:a*b,'÷':lambda:a/b}[match[2]]()
  actual=Decimal(step['options'][step['answer']])
  assert abs(actual-expected)<=max(Decimal('1e-9'),abs(expected)*Decimal('1e-9'))
  assert step['formula_hint']['latex'] in FORMULAS.values()
  challenge(step)
 challenge(steps[-1])
assert positions=={0,1,2,3}
print('PASS: ten wind-budget arithmetic drafts and native models; prerequisites, integration and Android remain pending.')
