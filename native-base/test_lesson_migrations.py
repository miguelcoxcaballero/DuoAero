"""Validate course splitting and evidence-backed historical path credit."""
import json
from pathlib import Path
from course_adapter import lesson_questions

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root/'app/assets/questions.json').read_text())}
plan = json.loads((root/'app/assets/lesson_plan.json').read_text())
lessons = {lesson['id']: lesson for node in plan for lesson in node['lessons']}
migrations = json.loads((root/'native-base/lesson-migrations.json').read_text())
assert len(lessons) == 82 and len(migrations) == 3
for target, migration in migrations.items():
    source = migration['sourceLesson']
    required = migration['requiredQuestions']
    assert target.endswith('-lesson-2') and source == target.replace('-lesson-2','-lesson-1')
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
print('PASS: 82 lessons have 10–20 native exercises; three path-only credits require exact historical coverage. Android UI and persistence remain unverified.')
