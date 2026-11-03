"""Draft ordering and historical-ID isolation, not migration or UI proof."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'native-base'))
from prerequisite_validation import multi_symbol_prerequisite
from taper_distribution import distribution

bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
lessons=distribution(bank)
assert len(lessons)==22
seen=set();ids=set();sources=[]
for lesson in lessons:
    assert 10<=len(lesson['questions'])<=20
    for q in lesson['questions']:
        assert q['id'] not in ids,q['id']
        ids.add(q['id'])
        prerequisite=q.get('draft_formula_prerequisite')
        if prerequisite:assert prerequisite in seen,(q['id'],prerequisite)
        if multi_symbol_prerequisite(q):seen.add(q['id'])
    if lesson['id'].startswith('taper-practice-') and lesson['id'].endswith('-2'):
        sources.append(lesson['questions'][-1]['id'])
assert len(sources)==len(set(sources))==10
session_ids={lesson['id'] for lesson in lessons}
for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
    history=json.loads((root/'native-base/session-history'/f'{version}.json').read_text())
    assert not session_ids.intersection(history)
    historical_ids={q['id'] for old in history.values() for q in old['challenges']}
    assert set(sources)<=historical_ids
print('PASS: 22 taper draft sessions, formulas precede calculation metadata and IDs are absent from published history; no migration or UI claim.')
