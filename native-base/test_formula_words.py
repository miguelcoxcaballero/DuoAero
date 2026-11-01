"""Verify authored word introductions and their actual catalog order.

This does not establish Android rendering or touchscreen behavior.
"""
import json
from pathlib import Path
from course_adapter import lesson_questions, session
from formula_words import KINDS

root = Path(__file__).resolve().parents[1]
bank = {q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
plan = json.loads((root/'app/assets/lesson_plan.json').read_text())
seen = set()
for node in plan:
    for lesson in node['lessons']:
        source = [bank[qid] for qid in lesson['ids']]
        expanded = lesson_questions(source, teach_words=True)
        assert len(expanded) <= 23, (lesson['id'], len(expanded))
        ids = [q['id'] for q in expanded]
        assert len(ids) == len(set(ids))
        for i, q in enumerate(expanded):
            if q['type'] != 'formula_blocks':
                continue
            assert i > 0 and expanded[i-1]['id'] == q['id']+'-WORDS'
            words = expanded[i-1]
            assert words['stem'].count('___') == 1
            assert len(set(words['answer']+words['distractors'])) == 4
            assert words['answer'][0] in words['explanation']
            seen.add(q['id'])
        actual = session(source, lesson['id'], teach_words=True)['challenges']
        assert [q['id'] for q in actual] == ids
assert seen == set(KINDS), (sorted(seen-set(KINDS)), sorted(set(KINDS)-seen))
print(f'PASS: {len(seen)} authored formula introductions precede symbolic exercises; Android UI and touch pending.')
