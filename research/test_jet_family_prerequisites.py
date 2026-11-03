"""Model-level checks only; Android grading and readability remain pending."""
import base64,json,sys
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
assert len(items)==4*len(FORMULAS)==56
for item in items:
 challenge(item)
 for piece in item.get('inline_latex',[]):
  assert not piece.startswith('\\\\'), (item['id'],piece)
assert 'JET-KM' in {q['id'] for q in items}
for item in items:
 if item['id'] in ('JET-RANGE-NAMED-ALL','JET-FUEL-LIMIT-NAMED-ALL'):
  encoded=challenge(item)['promptInputChallenge']['prompt']['body']['taggedTextElement']['text'].split('duoaero-gap:')[1]
  segments=json.loads(base64.b64decode(encoded))
  assert any(r'\times' in x for x in segments)
  assert not any(r'\\times' in x or r'\\div' in x for x in segments)

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
assert math_latex('m_zf')==r'\textstyle m_{\mathrm{zf}}'
assert 'zero-fuel mass' in next(q for q in items if q['id']=='JET-DRY-WORDS')['stem'].casefold()
for source in json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig')):
 if audit(source):
  for q in draft(source):
   assert q['formula_hint']['prerequisite'] in symbolic
   model=challenge(q)
   if 'rich_text' in q:
    assert json.loads(model['challengeBlob'])['shirt']['value']
print('PASS: 56 prerequisite models and all 20 calculation drafts decode; placement, grading and display remain unverified.')
