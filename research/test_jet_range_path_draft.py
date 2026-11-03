"""Candidate path checks; not a migration or Android acceptance."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from audit_jet_families import audit
from jet_range_path_draft import candidate
from path_adapter import build_path
from course_adapter import lesson_questions
from prerequisite_validation import multi_symbol_prerequisite,validate_hint_prerequisites
original=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
plan=json.loads((root/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
bank, proposed=candidate(original,plan);by={q['id']:q for q in bank}
built=build_path(proposed,bank)
assert len(bank)==len(original)+9
assert len({q['id'] for q in bank})==len(bank)
seen=set();challenge_ids=set();new_ids=set();retained={}
for n in proposed:
 for lesson in n['lessons']:
  qs=lesson_questions([by[i] for i in lesson['ids']],teach_words=True)
  assert 10<=len(qs)<=20,(lesson['id'],len(qs))
  for q in qs:
   assert q['id'] not in challenge_ids,q['id'];challenge_ids.add(q['id'])
   validate_hint_prerequisites(q,seen)
   if q['type']=='formula_blocks' or multi_symbol_prerequisite(q):seen.add(q['id'])
   elif q['type']=='formula_named' and q.get('symbol_prerequisite'):seen.add(q['id'])
  if lesson['id'].startswith('2.2-range-draft'): new_ids.add(lesson['id'])
  retained[lesson['id']]=lesson
assert len(new_ids)==13
for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
 h=json.loads((root/'native-base/session-history'/f'{version}.json').read_text())
 assert not new_ids.intersection(h)
 assert all(any(q['id'] in {x['id'] for old in h.values() for x in old['challenges']} for q in [source]) for source in original if audit(source) and audit(source)[0]=='range')
print('PASS: isolated path preserves ten source IDs, 13 new session IDs and 10–20 controls; historical projection and Android are pending.')
