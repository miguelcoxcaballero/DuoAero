"""Check original answers and teaching assumptions for an isolated draft."""
import json
from decimal import Decimal
from pathlib import Path
from breguet_ratio_steps import draft, PREFIX

root = Path(__file__).resolve().parents[1]
bank = json.loads((root / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))
family = [q for q in bank if q['stem'].startswith(PREFIX)]
assert len(family) == 9
for source in family:
    steps = draft(source)
    assert len(steps) == 4 and len({q['id'] for q in steps}) == 4
    assert steps[-1]['id'] == source['id']
    assert steps[-1]['options'] == source['options'] and steps[-1]['answer'] == source['answer']
    assert all(q.get('formula_hint', {}).get('prerequisite') for q in steps)
    assert all(len(q['options']) == 4 and len(set(q['options'])) == 4 for q in steps)
    assert all(Decimal(q['options'][q['answer']]) > 0 for q in steps)
print('PASS: nine isolated Breguet cases preserve source answers and have four checked steps; prerequisites and Android remain unimplemented.')
