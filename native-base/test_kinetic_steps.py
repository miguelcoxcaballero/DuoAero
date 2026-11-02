"""Independently check rounded values, original answers and hint order."""
import json
import math
import re
from pathlib import Path
from course_adapter import lesson_questions

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root/'app/assets/questions.json').read_text())}
ids = ['TA1-0156-D2','TA1-0164-D2','TA1-0195-D2','TA1-0327-D2',
       'TA1-0348-D2','TA1-0371-D2','TA1-0456-D2']
for identifier in ids:
    q = bank[identifier]
    total, speed = map(int, re.search(r'Tt=(\d+) K at flow speed V=(\d+) m/s', q['stem']).groups())
    rise = speed**2/(2*1004.5)
    static = total - rise
    sound = math.sqrt(1.4*287*static)
    steps = q['lesson_steps']
    assert len(steps) == 4 and steps[-1]['id'] == identifier
    assert [s['formula_hint']['prerequisite'] for s in steps] == [f'TA1-0107-D2-F{i}' for i in range(1,5)]
    for s, expected in zip(steps[:3], [rise, static, sound]):
        assert abs(float(s['options'][s['answer']].split()[0])-expected) <= .0051
    # The displayed rounded intermediates must still select the original answer.
    displayed_mach = speed / round(sound,2)
    options = list(map(float, steps[-1]['options']))
    assert min(range(len(options)), key=lambda i:abs(options[i]-displayed_mach)) == q['answer']
    assert steps[-1]['options'] == q['options']
    assert len(lesson_questions([q], teach_words=True)) == 4
print('PASS: seven probe problems split into four numerically checked steps; Android remains to be reviewed.')
