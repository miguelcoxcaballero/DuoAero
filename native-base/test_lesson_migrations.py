"""Validate course splitting and evidence-backed historical path credit."""
import json
from pathlib import Path
from course_adapter import lesson_questions

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root/'app/assets/questions.json').read_text())}
plan = json.loads((root/'app/assets/lesson_plan.json').read_text())
lessons = {lesson['id']: lesson for node in plan for lesson in node['lessons']}
migrations = json.loads((root/'native-base/lesson-migrations.json').read_text())
assert len(lessons) == 100 and len(migrations) == 21
for target, migration in migrations.items():
    source = migration['sourceLesson']
    required = migration['requiredQuestions']
    target_node,_,target_index = target.rpartition('-lesson-')
    source_node,_,source_index = source.rpartition('-lesson-')
    assert ((target_node == source_node and int(target_index) >= 1 and int(source_index) < int(target_index)) or (target == '2.1-4-point-0-lesson-1' and source == '2.1-5-point-1-lesson-0'))
    assert required == lessons[target]['ids'] and len(required) == len(set(required))
    # A new 2.0 completion of the shorter source lesson must never award
    # completion of a new, not-yet-played lesson.
    current_ids = {q['id'] for q in lesson_questions([bank[qid] for qid in lessons[source]['ids']],teach_words=True)}
    assert not set(required) <= current_ids
    for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
        snapshot=json.loads((root/'native-base/session-history'/f'{version}.json').read_text())
        historical_ids={q['id'] for q in snapshot[source]['challenges']}
        assert set(required) <= historical_ids, (target, version)
for lesson in lessons.values():
    count=len(lesson_questions([bank[qid] for qid in lesson['ids']],teach_words=True))
    assert 10 <= count <= 20, (lesson['id'], count)
# These three conceptual questions moved only to the next existing lesson in
# the same topic to make room for complete named equations. No lesson ID or
# migration is added, so the move itself cannot award progress or rewards.
for source, target, moved in (
    ('2.1-3-point-0-lesson-0','2.1-3-point-0-lesson-1',['TA1-0886']),
    ('2.1-0-point-0-lesson-0','2.1-0-point-0-lesson-1',['TA1-0304','TA1-0497']),
    ('2.5-5-point-0-lesson-0','2.5-5-point-0-lesson-1',['TA1-0283-D2','TA1-0480-D2']),
    ('2.1-5-point-0-lesson-1','2.1-5-point-0-lesson-2',['TA1-0307']),
    ('2.3-6-point-0-lesson-0','2.3-6-point-0-lesson-1',['TA1-0809','TA1-0759','TA1-0738']),
):
    assert lessons[target]['ids'][:len(moved)] == moved
    assert not set(moved) & set(lessons[source]['ids'])
    for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
        snapshot=json.loads((root/'native-base/session-history'/f'{version}.json').read_text())
        assert set(moved) <= {q['id'] for q in snapshot[source]['challenges']}
assert 'TA1-0053-F1' not in lessons['2.1-0-point-0-lesson-0']['ids']
assert 'TA1-0053-F1' in lessons['2.1-0-point-0-lesson-1']['ids']
assert 'EX-2023-11-06-3' not in lessons['2.1-0-point-0-lesson-0']['ids']
assert 'EX-2023-11-06-3' in lessons['2.1-0-point-0-lesson-1']['ids']
assert 'TA1-0255-D2' not in lessons['2.3-5-point-0-lesson-0']['ids']
assert 'TA1-0255-D2' in lessons['2.3-5-point-0-lesson-1']['ids']
assert 'TA1-0444' not in lessons['2.1-5-point-0-lesson-0']['ids']
assert 'TA1-0444' in lessons['2.1-5-point-0-lesson-1']['ids']
for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
    snapshot=json.loads((root/'native-base/session-history'/f'{version}.json').read_text())
    assert 'TA1-0444' in {q['id'] for q in snapshot['2.1-5-point-0-lesson-0']['challenges']}
    assert 'TA1-0255-D2' in {q['id'] for q in snapshot['2.3-5-point-0-lesson-0']['challenges']}
    assert 'EX-2023-11-06-3' in {q['id'] for q in snapshot['2.1-0-point-0-lesson-0']['challenges']}
    assert 'TA1-0053-F1' in {q['id'] for q in snapshot['2.1-0-point-0-lesson-0']['challenges']}
    assert 'TA1-0150-F1' in {q['id'] for q in snapshot['2.5-5-point-0-lesson-0']['challenges']}
    assert 'TA1-0031-F1' in {q['id'] for q in snapshot['2.4-11-point-0-lesson-0']['challenges']}
assert 'TA1-0150-F1' not in lessons['2.5-5-point-0-lesson-0']['ids']
assert 'TA1-0150-F1' in lessons['2.5-5-point-0-lesson-1']['ids']
assert 'TA1-0031-F1' not in lessons['2.4-11-point-0-lesson-0']['ids']
assert 'TA1-0031-F1' in lessons['2.4-11-point-0-lesson-1']['ids']
print('PASS: 100 lessons have 10–20 native exercises; twenty-one path-only credits require exact historical coverage. Android UI and persistence remain unverified.')
