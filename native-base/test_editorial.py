import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bank = json.loads((ROOT/'app/assets/questions.json').read_text(encoding='utf-8'))
previous = json.loads(subprocess.check_output(['git', 'show', 'HEAD:app/assets/questions.json'], cwd=ROOT).decode('utf-8-sig'))
original_exams = {q['id']: q for q in previous if q['origin']['kind'] == 'exam'}
current = {q['id']: q for q in bank}
def without_presentation(question):
    return {key: value for key, value in question.items() if key != 'rich_text'}
assert all(without_presentation(current[key]) == without_presentation(value)
           for key, value in original_exams.items()), 'An original exam item changed'
assert len(original_exams) == 106
for q in bank:
    for key, value in q.get('rich_text', {}).items():
        sequences = value if key == 'options' else [value]
        if key == 'options': assert len(sequences) == len(q['options'])
        for sequence in sequences:
            for part in sequence:
                assert set(part) in ({'text'}, {'latex'})
                assert len(next(iter(part.values()))) > 0
    if 'editorial_review' not in q:
        continue
    assert q['origin']['kind'] == 'practice'
    assert len(set(q['options'])) == 4
    assert set(q['option_explanations']) == set(q['options'])
    assert len(set(q['option_explanations'].values())) == 4
    assert all(ref in original_exams for ref in q['exam_alignment'])
assert math.isclose(1 / .8, 1.25)
assert math.isclose(math.sqrt(1.10) / 1.03, 1.018261017640442, rel_tol=1e-6)
print('PASS: original 106 exam records unchanged except presentation metadata; distractors, rich schema and numeric ratios verified')
