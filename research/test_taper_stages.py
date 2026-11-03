"""Arithmetic only; no claim of native UI, hints or course integration."""
import json, math
from pathlib import Path
from taper_domain import bounds
from taper_stages import draft

bank = json.loads((Path(__file__).resolve().parents[1]/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
family = [q for q in bank if bounds(q) is not None]
assert len(family) == 10
for source in family:
    steps, lower, upper = draft(source)
    expected_lower, expected_upper = bounds(source)
    assert len(steps) == 24
    assert len({q['id'] for q in steps}) == len(steps)
    assert all(q['id'].startswith(source['id']+'-') and 'formula_hint' not in q for q in steps)
    assert math.isclose(lower, expected_lower, abs_tol=1e-7)
    assert math.isclose(upper, expected_upper, abs_tol=1e-7)
print('PASS: arithmetic scaffolds for 10 taper variants; options, prerequisites, domain choices, migration and Android remain pending.')
