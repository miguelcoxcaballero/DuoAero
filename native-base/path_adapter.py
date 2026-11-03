"""Describe the existing Aerospace plan with original Math path data types.

This supplies data only. Native decoding and original home/path rendering
must be verified separately; generated JSON is not proof of a working path.
"""
import hashlib
import os
import sys
import json
from pathlib import Path
from course_adapter import lesson_questions

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
    topic_names = {'1':'1 · Aerospace industry', '2.1':'2.1 · Atmosphere',
                   '2.2':'2.2 · Aircraft design', '2.3':'2.3 · Structures',
                   '2.4':'2.4 · Aerodynamics', '2.5':'2.5 · Propulsion',
                   '2.6':'2.6 · Aircraft systems'}
    seen_topics = set()
    absolute_index = 0
    for index, node in enumerate(plan):
        topic = node['topic']
        if not units or units[-1]['topic'] != topic:
            if topic in seen_topics:
                raise ValueError('Topic nodes must be contiguous: ' + topic)
            seen_topics.add(topic)
            units.append({'unitIndex': len(units), 'topic': topic, 'levels': [],
                          'teachingObjective': topic_names.get(topic, topic)})
        unit_index = len(units) - 1
        node_lessons = node['lessons']
        if not 1 <= len(node_lessons) <= 4:
            raise ValueError(f"Invalid lesson count for {node['id']}")
        skill_id = stable_id('skill', node['id'])
        level_id = stable_id('level', node['id'])
        metadata = []
        for lesson in node_lessons:
            ids = lesson['ids']
            if not 1 <= len(ids) <= 20 or any(qid not in by_id for qid in ids):
                raise ValueError(f"Invalid lesson questions: {lesson['id']}")
            # A single source item can expand into several native exercises.
            # Count what the learner sees when enforcing the minimum, while
            # still requiring real source questions and preserving their IDs.
            if len(lesson_questions([by_id[qid] for qid in ids], teach_words=True)) < 10:
                raise ValueError(f"Lesson has fewer than 10 exercises: {lesson['id']}")
            if sum(len(by_id[qid].get('lesson_steps') or [None]) for qid in ids)>20:
                raise ValueError(f"Expanded lesson exceeds 20 questions: {lesson['id']}")
            if lesson['id'] in lessons:
                raise ValueError('Duplicate lesson ID')
            used.extend(ids)
            lesson_metadata = {'id': lesson['id'], 'type': 'math_lesson'}
            metadata.append(lesson_metadata)
            lessons[lesson['id']] = {
                'name': lesson['name'], 'questionIds': list(ids),
                'nodeId': node['id'], 'nativeLevelId': level_id,
                'nativeSkillId': skill_id, 'unitIndex': unit_index,
            }
        level = {
            'id': level_id, 'state': 'active' if index == 0 else 'locked',
            'finishedSessions': 0, 'totalSessions': len(node_lessons),
            'pathLevelClientData': {
                'title': node['name'], 'skillId': skill_id,
                'sessionMetadatas': metadata,
                'practiceSessionMetadatas': metadata,
            },
            'pathLevelMetadata': {'unitIndex': unit_index, 'skillId': skill_id},
            'pathLevelSessionMetadata': {}, 'hasLevelReview': True,
            'debugName': node['name'], 'isInProgressSequence': True,
            'type': 'math_skill', 'subtype': 'regular',
            'absoluteNodeIndex': absolute_index,
        }
        units[-1]['levels'].append(level)
        absolute_index += 1
        # One chest at the end of each large topic. Reuse the old last-node
        # chest ID so previously claimed rewards remain claimed.
        if index + 1 == len(plan) or plan[index + 1]['topic'] != topic:
            chest = {
                'id': stable_id('chest', node['id']), 'state': 'locked',
                'finishedSessions': 0, 'totalSessions': 1,
                'pathLevelClientData': {},
                'pathLevelMetadata': {'unitIndex': unit_index, 'anchorSkillId': skill_id, 'indexSinceAnchorSkill': 0},
                'pathLevelSessionMetadata': {}, 'hasLevelReview': False,
                'debugName': 'Aerospace gems', 'isInProgressSequence': True,
                'type': 'chest', 'subtype': 'chest', 'absoluteNodeIndex': absolute_index,
            }
            units[-1]['levels'].append(chest)
            absolute_index += 1
    for unit in units:
        del unit['topic']
    if len(used) != len(set(used)) or set(used) != set(by_id):
        raise ValueError('The path must cover every bank question exactly once')
    summary = {
        'id': SECTION_ID, 'index': 0, 'type': 'learning',
        'title': 'Midterm 1', 'subtitle': 'Aerospace Technology',
        'debugName': 'Aerospace Technology - Midterm 1',
        'completedUnits': 0, 'totalUnits': len(units),
        'totalLevelsPerUnit': [len(unit['levels']) for unit in units],
        'completedLevelsPerUnit': [0] * len(units),
    }
    course = {
        'id': COURSE_ID, 'subject': 'math', 'topic': 'math',
        'fromLanguage': 'en', 'xp': 0, 'activePathSectionId': SECTION_ID,
        'pathSectionsSummary': [summary],
        # The original Math section picker renders path tabs/groups. Without
        # these, the course has a section but the picker receives no rows.
        'pathTabsSummary': [{'id': 'DUOAERO_MIDTERMS',
            'debugName': 'Aerospace Technology', 'title': 'Aerospace Technology',
            'pathSectionGroups': [{'id': 'DUOAERO_FIRST_MIDTERM',
                'debugName': 'Midterm 1', 'title': 'Midterm 1',
                'subtitle': 'Aerospace Technology', 'state': 'unlocked', 'iconText': '1',
                'completedUnits': 0, 'totalUnits': len(units),
                'sectionIds': [SECTION_ID], 'type': 'learning'}]}],
        'globalPracticeMetadata': {'id': 'duoaero_review', 'type': 'global_practice'},
    }
    section = {'id': SECTION_ID, 'index': 0, 'units': units}
    return course, section, lessons


if __name__ == '__main__':
    bank = json.loads((ROOT / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))
    plan = json.loads((ROOT / 'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
    if os.environ.get('DUOAERO_JET_RANGE_PATH_DIAGNOSTIC')=='1':
        if os.environ.get('DUOAERO_PACKAGE','com.duoaero.nativebase')!='com.duoaero.nativebase':
            raise ValueError('Jet range path is an isolated diagnostic only')
        sys.path.insert(0,str(ROOT/'research'))
        from jet_range_path_draft import candidate
        bank,plan=candidate(bank,plan)
    course, section, lessons = build_path(plan, bank)
    destination = ROOT / 'native-base/tests/fixtures'
    destination.mkdir(exist_ok=True, parents=True)
    for name, value in [('native_course_path_info', course),
                        ('native_course_section', section),
                        ('native_lesson_index', lessons)]:
        (destination / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
    print(f'Native path data: {len(section["units"])} nodes, {len(lessons)} lessons, {len(bank)} questions. Runtime acceptance pending.')
