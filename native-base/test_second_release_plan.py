"""Validate new second-midterm IDs and reject inherited historical credits.

This does not establish Android rendering, saved progress or complete coverage.
"""
import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(root/'native-base'),str(root/'research')]
from course_adapter import session
from rocket_lesson import lesson as rocket
from orbit_lesson import lesson as orbit

bank=json.loads((root/'research/midterm2_concepts.json').read_text())['questions']
base=lambda topic:[dict(q,difficulty=1) for q in bank if q['topic']==topic]
extra=lambda name:json.loads((root/'research'/name).read_text())['questions']
plans=[('3.1',[base('3.1'),rocket(),orbit()]),
       ('3.2',[base('3.2'),extra('midterm2_space_environment_extra.json')]),
       ('3.3',[base('3.3'),extra('midterm2_spacecraft_extra.json')])]
migrations=json.loads((root/'native-base/lesson-migrations.json').read_text())
history=[json.loads((root/'native-base/session-history'/f'{version}.json').read_text())
         for version in ('1.3.0','1.3.5','1.3.6','1.3.7')]
ids=[];question_ids=set()
for topic,lessons in plans:
    for index,questions in enumerate(lessons):
        identifier=f'second-partial-{topic}-lesson-{index}'
        challenges=session(questions,identifier,teach_words=True)['challenges']
        assert 10<=len(challenges)<=20,identifier
        assert identifier not in migrations and all(identifier not in snapshot for snapshot in history),identifier
        for challenge in challenges:
            assert challenge['id'] not in question_ids,challenge['id']
            question_ids.add(challenge['id'])
        ids.append(identifier)
assert len(ids)==7 and len(set(ids))==7
print('PASS: seven stable space lessons, valid sizes and no historical completion mappings; Android acceptance pending.')
