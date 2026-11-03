"""One-operation draft for ten round-trip fuel-budget practice cases.

No authored prerequisite lessons, course migration or Android acceptance yet.
"""
import hashlib,math,re
from jet_family_steps import number_latex
N=r'([0-9.eE+-]+)'
PATTERN=re.compile(r'A round trip has two legs of '+N+r' m each at true airspeed '+N+
 r' m/s\. Estimate cruise at constant mean weight '+N+r' N, rho='+N+r' kg/m³, area '+N+
 r' m², polar CD='+N+r'\+'+N+r' CL² and ce='+N+r' kg/\(N s\)\. Available fuel for these two legs is '+N+r' kg')
FORMULAS={
 'q':r'q=\frac{1}{2}\rho V^2',
 'lift':r'C_L=\frac{W}{qS}',
 'polar':r'C_D=C_{D0}+k C_L^2',
 'drag':r'D=qSC_D',
 'flow':r'\dot m_f=c_eD',
 'time':r't=\frac{m_f}{\dot m_f}',
 'wind':r'w=\sqrt{V^2-\frac{2LV}{t}}',
}

def values(question):
 m=PATTERN.match(question.get('stem',''))
 return tuple(map(float,m.groups())) if m else None

def draft(source):
 values_=values(source)
 if values_ is None:raise ValueError('Not a round-trip fuel-budget case')
 length,speed,weight,rho,area,cd0,k,ce,fuel=values_
 items=[]
 def op(suffix,label,a,sign,b,key):
  a,b=float(f'{a:.10g}'),float(f'{b:.10g}')
  n={'+':lambda:a+b,'-':lambda:a-b,'×':lambda:a*b,'÷':lambda:a/b}[sign]()
  step=max(abs(n)*0.1,1e-12);xs=[n,n+step,n-step,n+2*step]
  values=[f'{x:.10g}' for x in xs];assert len(set(values))==4
  index=int.from_bytes(hashlib.sha256((source['id']+suffix).encode()).digest()[:2],'big')%4
  options=values[-index:]+values[:-index] if index else values
  operator={'×':r'\times','÷':r'\div','+':'+','-':'-'}[sign]
  items.append({'id':source['id']+'-'+suffix,'type':'choice','difficulty':1,
    'stem':f'{label} Calculate {a:.10g} {sign} {b:.10g}.',
    'rich_text':{'stem':[{'text':label+' Calculate '},{'latex':number_latex(a)+operator+number_latex(b)},{'text':'.'}]},
    'options':options,'answer':index,'explanation':f'{n:.10g}',
    'formula_hint':{'latex':FORMULAS[key],'prerequisite':'WIND-BUDGET-'+key.upper()},'expected':n})
  return n
 half=op('HALF-RHO','Half the air density:',rho,'÷',2,'q')
 speed2=op('SPEED-SQUARED','Airspeed squared:',speed,'×',speed,'q')
 q=op('Q','Multiply half-density by airspeed squared:',half,'×',speed2,'q')
 qs=op('QS','Dynamic pressure times wing area:',q,'×',area,'lift')
 cl=op('CL','Weight divided by pressure-area product:',weight,'÷',qs,'lift')
 cl2=op('CL-SQUARED','Lift coefficient squared:',cl,'×',cl,'polar')
 induced=op('INDUCED-COEFFICIENT','Polar factor times lift coefficient squared:',k,'×',cl2,'polar')
 cd=op('CD','Add zero-lift and induced drag coefficients:',cd0,'+',induced,'polar')
 drag=op('DRAG','Pressure-area product times drag coefficient:',qs,'×',cd,'drag')
 flow=op('FLOW','Specific fuel consumption times drag:',ce,'×',drag,'flow')
 time=op('TIME','Available fuel divided by fuel flow:',fuel,'÷',flow,'time')
 two_l=op('DISTANCE','Two equal legs:',2,'×',length,'wind')
 numerator=op('DISTANCE-SPEED','Twice the leg distance times airspeed:',two_l,'×',speed,'wind')
 term=op('TIME-TERM','Divide by available cruise time:',numerator,'÷',time,'wind')
 square=op('WIND-SQUARED','Subtract the time term from airspeed squared:',speed2,'-',term,'wind')
 assert 0<square<speed2,source['id']
 wind=math.sqrt(float(f'{square:.10g}'))
 options=[float(x.split()[0]) for x in source['options']]
 assert min(range(4),key=lambda i:abs(options[i]-wind))==source['answer'],source['id']
 items.append({'id':source['id'],'type':'choice','difficulty':source.get('difficulty',3),
  'stem':f'What is the square root of {square:.10g}? Choose the closest speed in m/s.',
  'rich_text':{'stem':[{'text':'Choose the closest speed in m/s: '},{'latex':r'\sqrt{'+number_latex(square)+'}'},{'text':'.'}]},
  'options':list(source['options']),'answer':source['answer'],
  'explanation':f'The closest original option is {source["options"][source["answer"]]}.',
  'formula_hint':{'latex':FORMULAS['wind'],'prerequisite':'WIND-BUDGET-WIND'},'expected':wind})
 return items
