"""Check source answers and displayed rounding in the isolated draft."""
import json
from pathlib import Path
from approach_speed_steps import PREFIX,draft,fmt
from decimal import Decimal
assert fmt(Decimal("383968")) == "383968" and fmt(Decimal("0.000001")) == "0.000001"
bank=json.loads((Path(__file__).resolve().parents[1]/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
family=[q for q in bank if q['stem'].startswith(PREFIX)]
assert len(family)==10
for source in family:
    steps=draft(source)
    assert len(steps)==9 and len({q['id'] for q in steps})==9
    assert steps[-1]['id']==source['id'] and steps[-1]['options']==source['options'] and steps[-1]['answer']==source['answer']
    assert all(len(q['options'])==len(set(q['options']))==4 for q in steps)
    assert all(q.get('formula_hint',{}).get('prerequisite') for q in steps)
print('PASS: ten source options checked with displayed rounding; formula introductions, path migration and Android remain pending.')
