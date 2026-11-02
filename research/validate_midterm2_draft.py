"""Validate the isolated conceptual draft; this does not test Android UI."""
import json
from pathlib import Path

data = json.loads(Path(__file__).with_name('midterm2_concepts.json').read_text())
assert data['status'] == 'draft_not_connected_to_course'
questions = data['questions']
topics = ('3.1', '3.2', '3.3', '5.1', '5.2')
assert len(questions) == 10 * len(topics)
assert {q['topic'] for q in questions} == set(topics)
assert all(sum(q['topic']==topic for q in questions)==10 for topic in topics)
assert len({q['id'] for q in questions}) == len(questions)
assert len({q['answer'] for q in questions}) == 4
for q in questions:
    assert q['type'] == 'choice' and q['stem'].endswith('?')
    assert len(q['options']) == len(set(q['options'])) == 4
    assert type(q['answer']) is int and 0 <= q['answer'] < 4
    assert q['explanation'].strip()
    assert not any(key in q for key in ('url', 'source_excerpt', 'drive_id'))
print('PASS: 50 isolated conceptual draft items; no Android or full-course acceptance asserted.')
