"""Check original answers and teaching assumptions for an isolated draft."""
import json
import math
import re
from decimal import Decimal
from pathlib import Path
from breguet_ratio_steps import draft, PREFIX

root = Path(__file__).resolve().parents[1]
bank = json.loads((root / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))
family = [q for q in bank if q['stem'].startswith(PREFIX)]
assert len(family) == 9
for source in family:
    steps = draft(source)
    # Independent physical check: equal p and Mach imply equal dynamic
    # pressure even when T changes. The common weight, S and polar then keep
    # CL and L/D unchanged, so only velocity and consumption ratios remain.
    m = re.search(r'pressure ([0-9.]+) Pa, Mach ([0-9.]+).*?Temperature changes from ([0-9.]+) to ([0-9.]+) K; ce1=([0-9.e+-]+) and ce2=([0-9.e+-]+)', source['stem'])
    assert m, source['id']
    p, mach, t1, t2, c1, c2 = map(float, m.groups())
    rho1, rho2 = p/(287*t1), p/(287*t2)
    v1, v2 = mach*math.sqrt(1.4*287*t1), mach*math.sqrt(1.4*287*t2)
    q1, q2 = 0.5*rho1*v1*v1, 0.5*rho2*v2*v2
    assert math.isclose(q1, q2, rel_tol=1e-12)
    independent_ratio = (v2/v1)*(c1/c2)
    assert abs(independent_ratio-float(steps[-1]['options'][steps[-1]['answer']])) < 0.0001
    assert len(steps) == 4 and len({q['id'] for q in steps}) == 4
    assert steps[-1]['id'] == source['id']
    assert steps[-1]['options'] == source['options'] and steps[-1]['answer'] == source['answer']
    assert all(q.get('formula_hint', {}).get('prerequisite') for q in steps)
    assert all(len(q['options']) == 4 and len(set(q['options'])) == 4 for q in steps)
    assert all(Decimal(q['options'][q['answer']]) > 0 for q in steps)
print('PASS: nine isolated Breguet cases preserve source answers and have four checked steps; prerequisites and Android remain unimplemented.')
