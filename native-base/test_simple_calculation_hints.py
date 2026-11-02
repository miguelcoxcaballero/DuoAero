"""Check the formula prerequisites and arithmetic for two direct examples."""
import json
from decimal import Decimal
from pathlib import Path
from course_adapter import lesson_questions
from rich_question import choice_blob

root=Path(__file__).resolve().parents[1]
bank={q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
plan=json.loads((root/'app/assets/lesson_plan.json').read_text())
seen=set()
expected={
    'TA1-0069-F1':('BOOK-V6-07-D1',r'T=\dot m(V_e-V_0)','5 kN'),
    'TA1-0017-F1':('CABIN-WING-LOADING',r'\frac{W}{S}=qC_L','0.50'),
    'TA1-0106-F1':('BOOK-V6-04-D1',r'\Delta L=\frac{FL}{E_Y A}','1.0 mm'),
    'TA1-0016-F1':('LIFT-FORMULA',r'L=qSC_L','20 kN'),
    'TA1-0150-F1':('TOTAL-THRUST-FORMULA',r'T=T_m+T_p','15 kN'),
    'TA1-0031-F1':('MEAN-CHORD-FORMULA',r'\bar{c}=\frac{S}{b}','3 m'),
    'TA1-0234-F1':('BOOK-V6-05-D1',r'P_{cr}=\frac{\pi^2 E_Y I}{(KL)^2}','4'),
}
for node in plan:
    for lesson in node['lessons']:
        for q in lesson_questions([bank[i] for i in lesson['ids']],teach_words=True):
            if q['id'] in expected:
                prerequisite,latex,answer=expected[q['id']]
                assert prerequisite in seen
                assert q['formula_hint']=={'latex':latex,'prerequisite':prerequisite}
                assert q['options'][q['answer']]==answer
                blob=json.loads(choice_blob(q,include_formula_hint=True)['challengeBlob'])
                assert blob['hint']['explanation']['value']==latex
            seen.add(q['id'])
assert set(expected)<=seen
assert Decimal(50)*100/1000==5
assert Decimal(60000)/120000==Decimal('.50')
assert Decimal(12000)/12000000*1000==1
assert Decimal(2000)*20*Decimal('.5')==20000
assert Decimal(12)+3==15
assert Decimal(60)/20==3
assert 1/(Decimal('.5')**2)==4
print('PASS: seven direct calculations have prior formula hints and checked answers; Android hint/retry remains unverified.')
