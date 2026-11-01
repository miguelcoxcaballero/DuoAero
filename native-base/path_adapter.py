"""Describe the existing Aerospace plan with original Math path data types.

This supplies data only. Native decoding and original home/path rendering
must be verified separately; generated JSON is not proof of a working path.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COURSE_ID = 'MATH_BT'  # Internal original catalog entry; content is Aerospace.
SECTION_ID = 'DUOAERO_MIDTERM1'


def stable_id(kind, identifier):
    return hashlib.sha256(f'duoaero:{kind}:{identifier}'.encode()).hexdigest()[:32]


def build_path(plan, bank):
    by_id = {q['id']: q for q in bank}
    if len(by_id) != len(bank):
        raise ValueError('Duplicate source question IDs')
    units, lessons, used = [], {}, []
    for index, node in enumerate(plan):
        node_lessons = node['lessons']
        if not 1 <= len(node_lessons) <= 3:
            raise ValueError(f"Invalid lesson count for {node['id']}")
        skill_id = stable_id('skill', node['id'])
        level_id = stable_id('level', node['id'])
        metadata = []
        for lesson in node_lessons:
            ids = lesson['ids']
            if not 10 <= len(ids) <= 20 or any(qid not in by_id for qid in ids):
                raise ValueError(f"Invalid lesson questions: {lesson['id']}")
            if lesson['id'] in lessons:
                raise ValueError('Duplicate lesson ID')
            used.extend(ids)
            lesson_metadata = {'id': lesson['id'], 'type': 'math_lesson'}
            metadata.append(lesson_metadata)
            lessons[lesson['id']] = {
                'name': lesson['name'], 'questionIds': list(ids),
                'nodeId': node['id'], 'nativeLevelId': level_id,
                'nativeSkillId': skill_id, 'unitIndex': index,
            }
        level = {
            'id': level_id, 'state': 'active' if index == 0 else 'locked',
            'finishedSessions': 0, 'totalSessions': len(node_lessons),
            'pathLevelClientData': {
                'title': node['name'], 'skillId': skill_id,
                'sessionMetadatas': metadata,
                'practiceSessionMetadatas': metadata,
            },
            'pathLevelMetadata': {'unitIndex': index, 'skillId': skill_id},
            'pathLevelSessionMetadata': {}, 'hasLevelReview': True,
            'debugName': node['name'], 'isInProgressSequence': True,
            'type': 'math_skill', 'subtype': 'regular',
            'absoluteNodeIndex': index,
        }
        units.append({'unitIndex': index, 'levels': [level],
                      'teachingObjective': node['name']})
    if len(used) != len(set(used)) or set(used) != set(by_id):
        raise ValueError('The path must cover every bank question exactly once')
    summary = {
        'id': SECTION_ID, 'index': 0, 'type': 'learning',
        'title': 'Midterm 1', 'subtitle': 'Aerospace Technology',
        'debugName': 'Aerospace Technology - Midterm 1',
        'completedUnits': 0, 'totalUnits': len(units),
        'totalLevelsPerUnit': [1] * len(units),
        'completedLevelsPerUnit': [0] * len(units),
    }
    course = {
        'id': COURSE_ID, 'subject': 'math', 'topic': 'math',
        'fromLanguage': 'en', 'xp': 0, 'activePathSectionId': SECTION_ID,
        'pathSectionsSummary': [summary],
        'globalPracticeMetadata': {'id': 'duoaero_review', 'type': 'global_practice'},
    }
    section = {'id': SECTION_ID, 'index': 0, 'units': units}
    return course, section, lessons


if __name__ == '__main__':
    bank = json.loads((ROOT / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))
    plan = json.loads((ROOT / 'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
    course, section, lessons = build_path(plan, bank)
    destination = ROOT / 'native-base/tests/fixtures'
    destination.mkdir(exist_ok=True, parents=True)
    for name, value in [('native_course_path_info', course),
                        ('native_course_section', section),
                        ('native_lesson_index', lessons)]:
        (destination / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
    print(f'Native path data: {len(section["units"])} nodes, {len(lessons)} lessons, {len(bank)} questions. Runtime acceptance pending.')
