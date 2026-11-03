"""Check explicit wind formulas; no result claims a complete lesson."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from course_adapter import challenge
from formula_exercises import math_latex
from prerequisite_validation import multi_symbol_prerequisite,validate_hint_prerequisites
from wind_budget_prerequisites import prerequisites
from wind_budget_steps import draft,values
qs=prerequisites();assert len(qs)==24
seen=set()
for q in qs:
 challenge(q)
 if multi_symbol_prerequisite(q):seen.add(q['id'])
assert len(seen)==6 and math_latex('C_D0')==r'\textstyle C_{D0}'
bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
for source in bank:
 if values(source):
  for q in draft(source):
   if q['formula_hint']['prerequisite']=='WIND-BUDGET-WIND':
    try:validate_hint_prerequisites(q,seen)
    except AssertionError:pass
    else:raise AssertionError('Untaught wind relation must not be accepted')
   else:validate_hint_prerequisites(q,seen)
print('PASS: six formula prerequisites; missing wind relation remains blocked from integration.')
