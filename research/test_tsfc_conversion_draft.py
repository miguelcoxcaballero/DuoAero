"""Arithmetic and native-model checks; Android and course placement remain open."""
import json, sys
from decimal import Decimal
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'native-base'))
from course_adapter import session
from formula_exercises import math_latex
from tsfc_conversion_draft import draft
source=next(q for q in json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig')) if q['id']=='TA1-0173-F1')
assert math_latex('m_kg')==r'\textstyle m_{\mathrm{kg}}'
assert math_latex('F_kN')==r'\textstyle F_{\mathrm{kN}}'
questions=draft(source)
assert len(questions)==10 and len({q['id'] for q in questions})==10
assert [q['type'] for q in questions[:8]]==['gap','formula_named','formula_named','formula_named']*2
assert Decimal('20')*Decimal('.001')==Decimal('.02')
assert Decimal('.02')/Decimal('1000')==Decimal('2e-5')
assert [q['id'] for q in session(questions,'isolated-tsfc-draft')['challenges']]==[q['id'] for q in questions]
print('PASS: split TSFC conversion arithmetic and native models; no Android or course migration claimed.')
