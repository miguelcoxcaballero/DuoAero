"""Verify the displayed lapse-rate arithmetic, prerequisites and path order."""
import json
import re
from decimal import Decimal
from pathlib import Path

from course_adapter import lesson_questions, session

root=Path(__file__).resolve().parents[1]
bank={q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
plan=json.loads((root/'app/assets/lesson_plan.json').read_text())
ids=('TA1-0646-D2','TA1-0178-D2','TA1-0200-D2','TA1-0212-D2')
expanded=[]
for qid in ids:
    question=bank[qid]
    m=re.search(r'A temperature of (\d+) K is measured at (\d+) m\..*?at (\d+) m\?',question['stem'])
    low,a,b=map(int,m.groups())
    drop=Decimal('0.0065')*(b-a)
    first,last=lesson_questions([question],teach_words=True)[-2:]
    assert Decimal(first['options'][first['answer']].split()[0])==drop
    assert Decimal(last['options'][last['answer']].split()[0])==Decimal(low)-drop
    assert Decimal(question['options'][question['answer']].split()[0])==Decimal(low)-drop
    assert first['formula_hint']['prerequisite']=='ISA-LAPSE-FORMULA'
    assert last['formula_hint']['prerequisite']=='ISA-ALT-TEMP-FORMULA'
    assert all(len(step['stem'])<130 and step.get('rich_text') for step in (first,last))
    expanded.extend(lesson_questions([question],teach_words=True))
assert len(expanded)==14
assert [q['id'] for q in expanded[:6]]==['ISA-LAPSE-WORDS','ISA-LAPSE-NAMED','ISA-LAPSE-FORMULA','ISA-ALT-TEMP-WORDS','ISA-ALT-TEMP-NAMED','ISA-ALT-TEMP-FORMULA']
assert len(expanded[1]['answer_blocks'])==len(expanded[4]['answer_blocks'])==3
assert len(session([bank[id] for id in ids],'lapse-diagnostic',teach_words=True)['challenges'])==14
ordered=[q['id'] for n in plan for l in n['lessons'] for q in lesson_questions([bank[id] for id in l['ids']],teach_words=True)]
assert ordered.index('ISA-LAPSE-FORMULA')<min(ordered.index(id+'-S1') for id in ids)
assert ordered.index('ISA-ALT-TEMP-FORMULA')<min(ordered.index(id) for id in ids)
print('PASS: four word-first, two-step lapse-rate problems match the original answers; Android UI remains unverified.')
