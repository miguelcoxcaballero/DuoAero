"""Check the reviewed payload calculation and its word-first teaching order."""
import json
from pathlib import Path
from course_adapter import lesson_questions
from formula_exercises import formula_challenge

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root/'app/assets/questions.json').read_text())}
parts = lesson_questions([bank['TA1-0024-F1']], teach_words=True)
assert [q['id'] for q in parts] == [
    'MASS-PAYLOAD-FORMULA-WORDS', 'MASS-PAYLOAD-FORMULA-NAMED-ALL',
    'MASS-PAYLOAD-FORMULA-NAMED', 'MASS-PAYLOAD-FORMULA',
    'TA1-0024-F1-S1', 'TA1-0024-F1']
named = parts[1]
assert named['answer_blocks'] == ['payload mass','takeoff mass','empty mass','fuel mass']
assert named['inline_latex'] == ['___','=','___','-','___','-','___']
symbolic = parts[3]
assert symbolic['formula_latex'] == r'm_p=m_{to}-m_{oem}-m_f'
assert symbolic['answer_blocks'] == ['m_{to}','−','m_{oem}','−','m_f']
input_data = formula_challenge(symbolic)['promptInputChallenge']['input']['expressionBuildInput']
assert len(input_data['dragChoices']) == len(symbolic['blocks']) + 1  # two minus cards
for part, expected in zip(parts[-2:], (50000-30000, 20000-8000)):
    assert int(part['options'][part['answer']].split()[0]) == expected
    assert part['formula_hint']['prerequisite'] == symbolic['id']
    assert len(set(part['options'])) == 4 and len(part['stem']) < 160
plan = json.loads((root/'app/assets/lesson_plan.json').read_text())
lesson = next(l for n in plan for l in n['lessons'] if 'TA1-0024-F1' in l['ids'])
assert len(lesson_questions([bank[i] for i in lesson['ids']], teach_words=True)) == 20
print('PASS: payload formula order, two subtractions and existing lesson length; Android UI unverified.')
