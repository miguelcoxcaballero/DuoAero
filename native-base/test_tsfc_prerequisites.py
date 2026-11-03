"""Require word, quantity and symbolic teaching before each TSFC hint."""
import copy,json
from pathlib import Path
from prerequisite_validation import multi_symbol_prerequisite, validate_hint_prerequisites

root=Path(__file__).resolve().parents[1]
source=next(q for q in json.loads((root/'app/assets/questions.json').read_text()) if q['id']=='TA1-0173-F1')
steps=source['lesson_steps'];seen=set()
for i,prefix in enumerate(('TSFC-GRAM','TSFC-THRUST','TSFC-PER-NEWTON')):
    group=steps[i*4:i*4+4]
    assert [q['id'] for q in group]==[prefix+'-WORDS',prefix+'-NAMED-ALL',prefix+'-NAMED',prefix]
    assert not multi_symbol_prerequisite(group[1]) and not multi_symbol_prerequisite(group[2])
    assert multi_symbol_prerequisite(group[3]);seen.add(prefix)
for q in steps[12:]:
    validate_hint_prerequisites(q,seen)
    for unavailable in (set(),seen-{q['formula_hint']['prerequisite']}):
        try:validate_hint_prerequisites(q,unavailable)
        except AssertionError:pass
        else:raise AssertionError('Missing or future formula accepted')
invalid=copy.deepcopy(steps[3]);invalid['answer_blocks'][0]='pressure';invalid['blocks'][0]='pressure'
try:multi_symbol_prerequisite(invalid)
except ValueError:pass
else:raise AssertionError('Quantity word accepted as symbolic formula')
invalid=copy.deepcopy(steps[3]);invalid['inline_latex'].pop()
try:multi_symbol_prerequisite(invalid)
except ValueError:pass
else:raise AssertionError('Invalid symbolic slot structure accepted')
print('PASS: explicit multi-symbol TSFC prerequisites precede hints; named, malformed and unavailable prerequisites are rejected.')
