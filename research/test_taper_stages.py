"""Arithmetic only; no claim of native UI, hints or course integration."""
import json, math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'native-base'))
from course_adapter import challenge
from taper_domain import bounds
from taper_stages import draft
from taper_prerequisites import prerequisites

bank = json.loads((Path(__file__).resolve().parents[1]/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
family = [q for q in bank if bounds(q) is not None]
symbol_ids={q['id'] for q in prerequisites() if q.get('mathematical_blocks')}
assert len(family) == 10
for source in family:
    steps, lower, upper = draft(source)
    expected_lower, expected_upper = bounds(source)
    assert len(steps) == (28 if upper >= max(0, lower) else 27)
    assert len({q['id'] for q in steps}) == len(steps)
    assert steps[-1]['id'] == source['id'] and steps[-1]['answer'] == source['answer']
    assert all(q['id'].startswith(source['id']+'-') and 'formula_hint' not in q for q in steps[:-1])
    assert all(len(q['options'])==len(set(q['options'])) and 0 <= q['answer'] < len(q['options']) for q in steps)
    for q in steps:challenge(q)
    for step in steps[:24]:
        assert math.isfinite(step['expected'])
        assert step['draft_formula_prerequisite'] in symbol_ids
        distances=[abs(float(x)-step['expected']) for x in step['options']]
        assert distances.index(min(distances)) == step['answer']
        assert distances.count(min(distances)) == 1
    domain=steps[25]
    assert domain['answer'] == (0 if upper >= max(0, lower) else 1)
    assert math.isclose(lower, expected_lower, abs_tol=1e-7)
    assert math.isclose(upper, expected_upper, abs_tol=1e-7)
print('PASS: staged arithmetic and domain drafts for 10 taper variants; prerequisites, hints, migration and Android remain pending.')
