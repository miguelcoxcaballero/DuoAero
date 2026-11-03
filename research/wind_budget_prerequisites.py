"""Six reviewed formula-model drafts; wind square-root layout remains open."""
from speed_limits_lesson import introduce
from wind_budget_steps import FORMULAS

SPECS=[
 ('q','Dynamic pressure is half the density times airspeed ___.','squared',
  ['dynamic pressure','air density','true airspeed'],['q','ρ','V'],['___','=',r'\frac12',r'\times','___',r'\times','___^2']),
 ('lift','Lift coefficient is weight divided by dynamic pressure times wing ___.','area',
  ['lift coefficient','weight','dynamic pressure','wing area'],['C_L','W','q','S'],['___','=','___',r'\div','(','___',r'\times','___',')']),
 ('polar','Drag coefficient equals zero-lift drag coefficient plus the polar factor times lift coefficient ___.','squared',
  ['drag coefficient','zero-lift drag coefficient','polar factor','lift coefficient'],['C_D','C_D0','k','C_L'],['___','=','___','+','___',r'\times','___^2']),
 ('drag','Drag is dynamic pressure times wing area times drag ___.','coefficient',
  ['drag force','dynamic pressure','wing area','drag coefficient'],['D','q','S','C_D'],['___','=','___',r'\times','___',r'\times','___']),
 ('flow','Fuel flow is thrust specific fuel consumption times ___.','drag',
  ['fuel mass flow rate','thrust specific fuel consumption','drag force'],['m_fd','c_e','D'],['___','=','___',r'\times','___']),
 ('time','Available cruise time is fuel mass divided by fuel mass flow ___.','rate',
  ['available cruise time','available fuel mass','fuel mass flow rate'],['t','m_f','m_fd'],['___','=','___/___']),
]

def prerequisites():
 out=[]
 for key,sentence,word,names,symbols,parts in SPECS:
  latex=FORMULAS[key]
  questions=introduce('WIND-BUDGET-'+key.upper(),sentence,word,
   [x for x in ('temperature','altitude','velocity','area') if x!=word][:3],latex,names,
   ['temperature','altitude','velocity'],parts,symbols,parts,'='+latex.split('=',1)[1])
  out.extend(questions)
 return out
