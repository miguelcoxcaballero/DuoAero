"""Model-level checks only; Android grading and readability remain pending."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'native-base'))
from course_adapter import challenge
from formula_exercises import math_latex
from prerequisite_validation import multi_symbol_prerequisite
from jet_family_prerequisites import prerequisites
from jet_family_steps import draft,FORMULAS
from audit_jet_families import audit

items=prerequisites()
assert len(items)==4*len(FORMULAS)==52
for item in items: challenge(item)
symbolic={q['id']:q for q in items if q.get('mathematical_blocks')}
assert set(symbolic)=={'JET-'+key.upper().replace('_','-') for key in FORMULAS}
assert all(multi_symbol_prerequisite(q) for q in symbolic.values())
fuel=challenge(symbolic['JET-FUEL-LIMIT'])['promptInputChallenge']['input']['expressionBuildInput']
assert fuel['slotCount']==6 and len(fuel['dragChoices'])>=6
assert sum(c['underlyingEntity']['entity'].get('variable',{}).get('algebraic',{}).get('name')=='duoaero:k' for c in fuel['dragChoices'])==2
repeated=dict(symbolic['JET-FUEL-LIMIT']); repeated.pop('allow_repeated_symbols')
try: multi_symbol_prerequisite(repeated)
except ValueError: pass
else: raise AssertionError('Unmarked repeated symbols must be rejected')
assert math_latex('mu')==r'\textstyle \mu'
for source in json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig')):
 if audit(source):
  for q in draft(source):
   assert q['formula_hint']['prerequisite'] in symbolic
   challenge(q)
print('PASS: 52 prerequisite models and all 20 calculation drafts decode; placement, grading and display remain unverified.')
