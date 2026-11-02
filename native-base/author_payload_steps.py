"""Split eight payload-limit problems while preserving original source data."""
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[1]
path=root/'app/assets/questions.json'
text=path.read_text(encoding='utf-8-sig')
bank=json.loads(text)
family=[q for q in bank if q.get('stem','').startswith('An aircraft has OEM=')
        and 'maximum landing mass=' in q['stem'] and 'maximum payload=' in q['stem']]
assert len(family)==8
fuel_formula=r'm_{f,l}=m_{f,t}-m_b'
landing_formula=r'm_p=m_l-m_o-m_{f,l}'
takeoff_formula=r'm_p=m_{to}-m_{oem}-m_f'
minimum_formula=r'm_p=\min(m_{p,s},m_{p,t},m_{p,l})'
intro=[
 dict(id='MASS-FUEL-REMAINING',type='formula_blocks',difficulty=1,
      stem='Complete the landing fuel formula',prefix=r'm_{f,l}=m_{f,t}-',
      blocks=['m_b','m_l','m_p','m_o'],answer_blocks=['m_b'],
      formula_latex=fuel_formula,explanation=fuel_formula),
 dict(id='MASS-LANDING-PAYLOAD',type='formula_blocks',difficulty=1,
      stem='Complete the landing payload formula',prefix=r'm_p=m_l-m_o-',
      blocks=['m_{f,l}','m_b','m_l','m_o'],answer_blocks=['m_{f,l}'],
      formula_latex=landing_formula,explanation=landing_formula),
 dict(id='MASS-PAYLOAD-MINIMUM',type='formula_blocks',difficulty=1,
      stem='Complete the allowed payload formula',prefix='',
      blocks=['m_{p,s}','m_{p,t}','m_{p,l}','m_b','m_l'],answer_blocks=['m_{p,s}','m_{p,t}','m_{p,l}'],
      inline_latex=['m_p','=',r'\min','(', '___',',','___',',','___',')'],
      formula_latex=minimum_formula,explanation=minimum_formula),
]
pattern=re.compile(r'OEM=(\d+) kg, MTOM=(\d+) kg, maximum landing mass=(\d+) kg and maximum payload=(\d+) kg.*?with (\d+) kg of fuel and burns (\d+) kg')
updates={}
for index,q in enumerate(family):
    match=pattern.search(q['stem']);assert match,q['id']
    empty,takeoff_limit,landing_limit,structural,fuel,burned=map(int,match.groups())
    landing_fuel=fuel-burned
    takeoff_nonpayload=empty+fuel
    landing_nonpayload=empty+landing_fuel
    takeoff_payload=takeoff_limit-takeoff_nonpayload
    landing_payload=landing_limit-landing_nonpayload
    result=min(structural,takeoff_payload,landing_payload)
    assert int(q['options'][q['answer']].split()[0])==result,q['id']
    def step(suffix,stem,value,formula,prerequisite):
        options=[f'{n} kg' for n in (value,value+1000,value-1000,value+2000)]
        assert len(set(options))==4 and value>1000
        return dict(id=q['id']+suffix,stem=stem,options=options,answer=0,
                    explanation=options[0],formula_hint={'latex':formula,'prerequisite':prerequisite})
    q['lesson_steps']=(list(intro) if index==0 else [])+[
      step('-S1',f'Takeoff fuel is {fuel} kg and {burned} kg is burned. How much fuel remains at landing?',landing_fuel,fuel_formula,'MASS-FUEL-REMAINING'),
      step('-S2',f'Empty mass is {empty} kg and takeoff fuel is {fuel} kg. What is their combined mass?',takeoff_nonpayload,takeoff_formula,'MASS-PAYLOAD-FORMULA'),
      step('-S3',f'Takeoff mass limit is {takeoff_limit} kg and non-payload mass is {takeoff_nonpayload} kg. What payload fits?',takeoff_payload,takeoff_formula,'MASS-PAYLOAD-FORMULA'),
      step('-S4',f'Empty mass is {empty} kg and landing fuel is {landing_fuel} kg. What is their combined mass?',landing_nonpayload,landing_formula,'MASS-LANDING-PAYLOAD'),
      step('-S5',f'Landing mass limit is {landing_limit} kg and non-payload mass is {landing_nonpayload} kg. What payload fits?',landing_payload,landing_formula,'MASS-LANDING-PAYLOAD'),
      dict(id=q['id'],stem=f'Payload limits are {structural} kg structurally, {takeoff_payload} kg at takeoff and {landing_payload} kg at landing. What payload satisfies all three?',
           options=list(q['options']),answer=q['answer'],explanation=f'The smallest limit is {result} kg.',
           formula_hint={'latex':minimum_formula,'prerequisite':'MASS-PAYLOAD-MINIMUM'})]
    updates[q['id']]=q
decoder=json.JSONDecoder();offset=text.index('[')+1;edits=[]
while True:
    while text[offset] in ' \t\r\n,':offset+=1
    if text[offset]==']':break
    old,end=decoder.raw_decode(text,offset)
    if old['id'] in updates:edits.append((offset,end,json.dumps(updates[old['id']],ensure_ascii=False,indent=2).replace('\n','\n  ')))
    offset=end
assert len(edits)==8
for start,end,replacement in reversed(edits):text=text[:start]+replacement+text[end:]
path.write_text(text,encoding='utf-8')
print('Authored six short steps for eight payload-limit calculations with prior formulas.')
