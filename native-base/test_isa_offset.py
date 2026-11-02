"""Verify the word-first ISA offset and its single arithmetic step."""
import json
from pathlib import Path
from course_adapter import lesson_questions, session

root=Path(__file__).resolve().parents[1]
bank={q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
plan=json.loads((root/'app/assets/lesson_plan.json').read_text())
q=bank['TA1-0049-F1']
parts=lesson_questions([q],teach_words=True)
assert [x['id'] for x in parts]==['ISA-OFFSET-WORDS','ISA-OFFSET-NAMED','ISA-OFFSET-FORMULA','TA1-0049-F1']
assert len(parts[1]['answer_blocks'])==3 and parts[2]['answer_blocks']==['ΔT']
assert parts[3]['formula_hint']['prerequisite']=='ISA-OFFSET-FORMULA'
assert parts[3]['options'][parts[3]['answer']]=='280 K' and 270+10==280
assert len(session([q],'offset-diagnostic',teach_words=True)['challenges'])==4
first=next(n for n in plan if n['id']=='2.1-5-point-0')['lessons'][0]
all_parts=lesson_questions([bank[id] for id in first['ids']],teach_words=True)
ids=[x['id'] for x in all_parts]
assert len(ids)==20 and ids.index('ISA-OFFSET-FORMULA')<ids.index('TA1-0049-F1')
print('PASS: ISA offset words and symbols precede the one-step calculation; Android UI remains unverified.')
