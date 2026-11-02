"""Check the displayed arithmetic and prerequisites of five ISA splits."""
import json
import math
import re
from pathlib import Path
from course_adapter import lesson_questions

root = Path(__file__).resolve().parents[1]
bank = {q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
ids = ('TA1-0445-D2','TA1-0449-D2','TA1-0592-D2','TA1-0668-D2','TA1-0708-D2')
for qid in ids:
    q=bank[qid]
    altitudes=re.search(r'h_A=(\d+) m and h_B=(\d+) m',q['stem'])
    a,b=map(int,altitudes.groups())
    base=101.325*(216.65/288.15)**(9.80665/(.0065*287))
    pressure_a=101.325*((288.15-.0065*a)/288.15)**(9.80665/(.0065*287))
    factor=math.exp(-9.80665*(b-11000)/(287*216.65))
    original=float(q['options'][q['answer']])
    assert abs(base*factor/pressure_a-original)<0.000011, qid
    first,second=lesson_questions([q])
    assert [first['id'],second['id']]==[qid+'-S1',qid]
    first_values=re.search(r'pressure is ([0-9.]+) kPa.*?it is ([0-9.]+) times',first['stem'])
    displayed_base,displayed_factor=map(float,first_values.groups())
    first_answer=float(first['options'][first['answer']].split()[0])
    assert abs(displayed_base*displayed_factor-first_answer)<=.0051, qid
    values=re.search(r'pressure is ([0-9.]+) kPa.*?pressure is ([0-9.]+) kPa',second['stem'])
    pa,pb=map(float,values.groups())
    assert pb==first_answer
    assert abs(pb/pa-float(second['options'][second['answer']]))<=.00051, qid
    assert abs(pb/pa-original)<.0006, qid
    assert first['formula_hint']['prerequisite']=='ISA-ISOTHERMAL-FORMULA'
    assert second['formula_hint']['prerequisite']=='ISA-PRESSURE-RATIO'
    assert all(len(x['stem'])<160 and len(set(x['options']))==4 and x.get('rich_text') for x in (first,second))
print('PASS: five ISA pressure calculations split and checked against both displayed and original values; Android UI remains unverified.')
