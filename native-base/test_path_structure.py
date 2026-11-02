"""Verify the topic/subtopic mapping without claiming native UI acceptance."""
import json
from pathlib import Path
from path_adapter import build_path, stable_id
root=Path(__file__).resolve().parents[1]
plan=json.loads((root/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
course, section, index=build_path(plan,bank)
units=section['units']
assert [unit['teachingObjective'].split(' · ')[0] for unit in units]==['1','2.1','2.2','2.3','2.4','2.5','2.6']
assert len(index)==89 and len({qid for lesson in index.values() for qid in lesson['questionIds']})==1200
for unit in units:
    levels=unit['levels']; assert levels[-1]['type']=='chest'
    assert sum(level['type']=='chest' for level in levels)==1
    assert all(level['pathLevelMetadata']['unitIndex']==unit['unitIndex'] for level in levels)
assert [level['id'] for unit in units for level in unit['levels'] if level['type']=='math_skill']==[stable_id('level',node['id']) for node in plan]
assert course['pathTabsSummary'][0]['pathSectionGroups'][0]['sectionIds']==[section['id']]
assert len(course['pathSectionsSummary'])==1 and course['pathSectionsSummary'][0]['title']=='Midterm 1'
assert course['pathSectionsSummary'][0]['totalLevelsPerUnit']==[len(u['levels']) for u in units]
assert [l['absoluteNodeIndex'] for u in units for l in u['levels']]==list(range(50))
print('PASS: 7 large topics, 43 stable subtopic nodes, 7 chests, 89 lessons and first-midterm section; native UI remains unverified.')
