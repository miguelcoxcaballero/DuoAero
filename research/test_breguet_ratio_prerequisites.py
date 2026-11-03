"""Check the partial draft without asserting course or Android acceptance."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from breguet_ratio_prerequisites import prerequisites
from course_adapter import session
qs=prerequisites()
assert len(qs)==12 and len({q['id'] for q in qs})==12
assert [q['type'] for q in qs]==['gap','formula_named','formula_named','formula_named']*3
fuel=next(q for q in qs if q['id']=='BREGUET-FUEL-RATIO-NAMED-ALL')
assert 'initial thrust-specific fuel consumption' in fuel['answer_blocks']
assert 'final thrust-specific fuel consumption' in fuel['answer_blocks']
single=next(q for q in qs if q['id']=='BREGUET-RANGE-RATIO-NAMED')
assert single['missing_latex']==r'r_V' and single['answer_blocks']==['speed ratio']
assert 'BREGUET-SPEED-RATIO' not in {q['id'] for q in qs}
assert [m['id'] for m in session(qs,'partial-range-draft')['challenges']]==[q['id'] for q in qs]
print('PASS: three partial Breguet formula sequences; the named radical, ordering and Android remain pending.')
