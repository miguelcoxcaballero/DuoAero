"""Check seven density/dynamic-pressure splits and their prerequisites."""
import json
import re
from pathlib import Path
from course_adapter import lesson_questions

root=Path(__file__).resolve().parents[1]
bank={q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
ids=('TA1-0144-D2','TA1-0224-D2','TA1-0310-D2','TA1-0473-D2','TA1-0474-D2','TA1-0581-D2','TA1-0593-D2')
for qid in ids:
    q=bank[qid]
    p,t,v=map(int,re.search(r'pressure is (\d+) Pa, temperature is (\d+) K and true airspeed is (\d+) m/s',q['stem']).groups())
    expected=.5*(p/(287*t))*v*v
    original=float(q['options'][q['answer']].split()[0])
    assert abs(original-expected)<=.051, qid
    expanded=lesson_questions([q],teach_words=True);first,second=expanded[-2:]
    assert [first['id'],second['id']]==[qid+'-S1',qid]
    rho=float(first['options'][first['answer']].split()[0]);answer=float(second['options'][second['answer']].split()[0])
    assert abs(rho-p/(287*t))<=.0000051 and abs(answer-rho*v*v/2)<=.051, qid
    assert abs(answer-original)<=.051, qid
    assert first['formula_hint']['prerequisite']=='ISA-DENSITY'
    assert second['formula_hint']['prerequisite']=='ISA-DYNAMIC'
    assert all(len(step['stem'])<160 and len(set(step['options']))==4 and step.get('rich_text') for step in (first,second))
intro=lesson_questions([bank[ids[0]]],teach_words=True)
assert [q['id'] for q in intro[:7]]==['ISA-DENSITY-WORDS','ISA-DENSITY-NAMED','ISA-DENSITY',
                                      'ISA-DYNAMIC-WORDS','ISA-DYNAMIC-NAMED-ALL','ISA-DYNAMIC-NAMED','ISA-DYNAMIC']
assert intro[2]['symbol_prerequisite'] and intro[2]['answer_blocks']==['ρ']
print('PASS: seven density and dynamic-pressure calculations checked; both formulas precede the first; Android UI remains unverified.')
