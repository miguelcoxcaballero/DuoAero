"""Check ordered draft distribution; historical projection is still pending."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from jet_family_distribution import distribution
from prerequisite_validation import multi_symbol_prerequisite,validate_hint_prerequisites
bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
nodes=distribution(bank)
assert len(nodes)==6 and all(len(node)==4 for node in nodes)
seen=set();ids=set();case_ids=[]
for node in nodes:
 for lesson in node:
  assert 10<=len(lesson['questions'])<=20
  for q in lesson['questions']:
   assert q['id'] not in ids,q['id'];ids.add(q['id'])
   validate_hint_prerequisites(q,seen)
   if multi_symbol_prerequisite(q):seen.add(q['id'])
  if lesson['id'].startswith('jet-practice-'):
   case_ids.append(lesson['questions'][-1]['id'])
assert len(case_ids)==len(set(case_ids))==20
new_session_ids={lesson['id'] for node in nodes for lesson in node}
for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
 history=json.loads((root/'native-base/session-history'/f'{version}.json').read_text())
 assert not new_session_ids.intersection(history)
 # Each source item already existed, but a completed old session is not
 # evidence of any of the new intermediate questions or new lesson IDs.
 old_challenges={q['id'] for old in history.values() for q in old['challenges']}
 assert set(case_ids)<=old_challenges
try:
 first_case=nodes[1][0]['questions'][0]
 validate_hint_prerequisites(first_case,set())
except AssertionError: pass
else: raise AssertionError('A calculation must not precede its formula')
print('PASS: six draft nodes, 24 ordered sessions, formulas before hints and unique IDs; no progress migration or UI claim.')
