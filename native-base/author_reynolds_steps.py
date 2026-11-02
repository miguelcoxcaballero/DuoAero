"""Split reviewed wind-tunnel scaling questions into small calculations."""
import json
import re
from decimal import Decimal
from pathlib import Path

root=Path(__file__).resolve().parents[1];path=root/'app/assets/questions.json'
text=path.read_text(encoding='utf-8-sig');bank=json.loads(text)
family=[q for q in bank if q.get('stem','').startswith('A wind-tunnel model must match the Reynolds number')]
assert len(family)==7
reynolds=r'\mathrm{Re}=\frac{\rho Vc}{\mu}'
scale=r'k=\frac{\mu_r}{\rho_r V_r}'
chord=r'c_2=c_1 k'
intro=[
 dict(id='REYNOLDS-FORMULA',type='formula_blocks',difficulty=1,stem='Complete the Reynolds number formula',prefix='',
      blocks=['ρ','V','c','μ','p','T'],answer_blocks=['ρ','V','c','μ'],
      inline_latex=[r'\mathrm{Re}','=', '(', '___',r'\times','___',r'\times','___',')',r'\div','___'],
      formula_latex=reynolds,explanation=reynolds),
 dict(id='REYNOLDS-SCALE-FORMULA',type='formula_blocks',difficulty=1,stem='Complete the chord scale formula',prefix='',
      blocks=['μ_r','ρ_r','V_r','T','p'],answer_blocks=['μ_r','ρ_r','V_r'],
      inline_latex=['k','=','___',r'\div','(', '___',r'\times','___',')'],formula_latex=scale,explanation=scale),
 dict(id='REYNOLDS-CHORD-FORMULA',type='formula_blocks',difficulty=1,stem='Complete the model chord formula',prefix=r'c_2=c_1',
      blocks=['k','p','T','V'],answer_blocks=['k'],formula_latex=chord,explanation=chord),
]
pattern=re.compile(r'chord ([0-9.]+) m.*?rho2/rho1=([0-9.]+), V2/V1=([0-9.]+), mu2/mu1=([0-9.]+)\.')
updates={}
for index,q in enumerate(family):
    match=pattern.search(q['stem']);assert match,q['id']
    reference,rho_ratio,speed_ratio,visc_ratio=map(Decimal,match.groups())
    product=rho_ratio*speed_ratio;factor=visc_ratio/product;answer=reference*factor
    assert abs(answer-Decimal(q['options'][q['answer']].split()[0]))<Decimal('.000051'),q['id']
    def step(suffix,stem,value):
        options=[f'{n:.6f}' for n in (value,value+Decimal('.1'),value-Decimal('.1'),value+Decimal('.2'))]
        assert len(set(options))==4
        return dict(id=q['id']+suffix,stem=stem,options=options,answer=0,
                    explanation=options[0],formula_hint={'latex':scale,'prerequisite':'REYNOLDS-SCALE-FORMULA'})
    q['lesson_steps']=(list(intro) if index==0 else [])+[
      step('-S1',f'The density ratio is {rho_ratio} and the speed ratio is {speed_ratio}. What is their product?',product),
      step('-S2',f'The viscosity ratio is {visc_ratio} and the density-speed ratio product is {product:.6f}. What is the chord scale factor?',factor),
      dict(id=q['id'],stem=f'The reference chord is {reference} m and the model scale factor is {factor:.6f}. What is the model chord?',
           options=list(q['options']),answer=q['answer'],explanation=f'{reference} × {factor:.6f} ≈ {q["options"][q["answer"]]}.',
           formula_hint={'latex':chord,'prerequisite':'REYNOLDS-CHORD-FORMULA'})]
    updates[q['id']]=q
decoder=json.JSONDecoder();offset=text.index('[')+1;edits=[]
while True:
    while text[offset] in ' \t\r\n,':offset+=1
    if text[offset]==']':break
    old,end=decoder.raw_decode(text,offset)
    if old['id'] in updates:edits.append((offset,end,json.dumps(updates[old['id']],ensure_ascii=False,indent=2).replace('\n','\n  ')))
    offset=end
assert len(edits)==7
for start,end,replacement in reversed(edits):text=text[:start]+replacement+text[end:]
path.write_text(text,encoding='utf-8')
print('Authored three short steps for seven checked Reynolds scaling questions.')
