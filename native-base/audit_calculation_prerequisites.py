"""Inventory possible calculation prompts without guessing their formulas.

This is a review queue, not a classifier of physical correctness. A number in
a question may describe a model, date or answer rather than a calculation.
Only a reviewed author should attach a hint and prerequisite to an exercise.
"""
import collections
import json
import re
from pathlib import Path

from course_adapter import lesson_questions

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))}
plan = json.loads((root / 'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
seen, broken, candidates = set(), [], collections.defaultdict(list)
for node in plan:
    for lesson in node['lessons']:
        for q in lesson_questions([bank[qid] for qid in lesson['ids']], teach_words=True):
            hint = q.get('formula_hint')
            if hint and hint.get('prerequisite') not in seen:
                broken.append((q['id'], hint.get('prerequisite')))
            options = q.get('options', [])
            if (q.get('type') == 'choice' and not hint and re.search(r'\d', q.get('stem', ''))
                    and sum(bool(re.search(r'\d', str(option))) for option in options) >= 3):
                candidates[q.get('topic', node.get('topic', '?'))].append(q['id'])
            seen.add(q['id'])
if broken:
    raise SystemExit('Hints without a preceding formula: ' + repr(broken))
print('Review candidates (heuristic; may include conceptual questions):', sum(map(len, candidates.values())))
for topic in sorted(candidates):
    print(topic, len(candidates[topic]), ' '.join(candidates[topic]))
print('All authored hint prerequisites occur earlier in the path; no UI or mathematical accuracy asserted.')
