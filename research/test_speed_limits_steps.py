"""Cross-check seven source answers in an isolated, not-yet-taught draft."""
import json
from pathlib import Path
from speed_limits_steps import PREFIX,draft,fmt
from decimal import Decimal
assert fmt(Decimal("383968")) == "383968" and fmt(Decimal("0.000001")) == "0.000001"

bank=json.loads((Path(__file__).resolve().parents[1]/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
family=[q for q in bank if q['stem'].startswith(PREFIX)]
assert len(family)==7
for source in family:
    steps=draft(source)
    assert len(steps)==8 and len({q['id'] for q in steps})==8
    assert steps[-1]['id']==source['id'] and steps[-1]['answer']==source['answer']
    assert steps[-1]['options']==source['options']
    assert all(len(q['options'])==len(set(q['options']))==4 for q in steps)
    assert all(q.get('formula_hint',{}).get('prerequisite') for q in steps)
print('PASS: seven source answers checked with eight isolated steps each; prerequisite lessons, migration and Android remain unimplemented.')
