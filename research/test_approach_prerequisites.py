"""Validate the partial draft; the interactive stall radical is still absent."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'native-base'))
from approach_prerequisites import prerequisites
from course_adapter import session
from formula_exercises import math_latex
assert math_latex("V_app") == r"\textstyle V_{\mathrm{app}}"
assert math_latex("V_kmh") == r"\textstyle V_{\mathrm{km/h}}"
questions=prerequisites()
assert len(questions)==12 and len({q['id'] for q in questions})==12
assert [q['type'] for q in questions]==['gap','formula_named','formula_named','formula_named']*3
assert 'APPROACH-STALL' not in {q['id'] for q in questions}
assert [q['id'] for q in session(questions,'partial-approach-draft')['challenges']]==[q['id'] for q in questions]
print('PASS: three partial word/named/symbol prerequisites; interactive stall formula, ordering and Android remain pending.')
