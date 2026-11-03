"""Formula teaching drafts for the audited ideal-jet families.

These are not integrated or visually accepted. Full-name operator layouts,
including vertical product fractions, require real-device review.
"""
from jet_family_steps import FORMULAS
from speed_limits_lesson import introduce

# Each tuple is (id, sentence, missing word, full quantity names, symbols,
# fixed operators). All formula components are authored explicitly.
SPECS = [
 ('dry','Dry mass is operating empty mass plus ___.','payload', ['dry mass','operating empty mass','payload'],['m_d','m_o','m_p'],['___','=','___','+','___']),
 ('tank','Tank-limited takeoff mass is dry mass plus fuel ___.','capacity',['tank-limited takeoff mass','dry mass','fuel capacity'],['m_tt','m_d','m_f'],['___','=','___','+','___']),
 ('minimum','Takeoff mass is the smaller takeoff ___.','limit',['takeoff mass','maximum takeoff mass','tank-limited takeoff mass'],['m_t','m_tm','m_tt'],['___','=',r'\min','(','___',',','___',')']),
 ('burn','Initial cruise mass is takeoff mass minus the pre-cruise fuel ___.','burn',['initial cruise mass','takeoff mass','fuel burned before cruise'],['m_i','m_t','m_b'],['___','=','___','-','___']),
 ('reserve','Final cruise mass is dry mass plus reserve ___.','fuel',['final cruise mass','dry mass','reserve fuel'],['m_e','m_d','m_r'],['___','=','___','+','___']),
 ('ratio','Mass ratio is initial mass divided by final cruise ___.','mass',['mass ratio','initial cruise mass','final cruise mass'],['mu','m_i','m_e'],['___','=','___/___']),
 ('log','The logarithm is the natural logarithm of the mass ___.','ratio',['natural logarithm of mass ratio','mass ratio'],['L','mu'],['___','=',r'\ln','(','___',')']),
 ('range','Cruise range uses aerodynamic efficiency, speed, mass ratio logarithm, gravity and specific fuel ___.','consumption',['cruise range','cruise speed','aerodynamic efficiency','natural logarithm of mass ratio','gravitational acceleration','thrust specific fuel consumption'],['R','V','E','L','g','c_e'],['___','=','(', '___',r'\times','___',r'\times','___',')',r'\div','(', '___',r'\times','___',')']),
 ('k','The mass ratio factor is the exponential of a dimensionless ___.','exponent',['mass ratio factor','cruise range','gravitational acceleration','thrust specific fuel consumption','cruise speed','aerodynamic efficiency'],['k','R','g','c_e','V','E'],['___','=',r'\exp','(', '___',r'\times','___',r'\times','___',r'\div','(', '___',r'\times','___',')',')']),
 ('takeoff_limit','Takeoff-limited payload accounts for operating empty mass and fuel ___.','reserve',['takeoff payload limit','maximum takeoff mass','mass ratio factor','operating empty mass','reserve fuel'],['p_t','m_tm','k','m_o','m_r'],['___','=','___/___','-','___','-','___']),
 ('landing_limit','Landing-limited payload is the maximum landing mass less operating empty mass and fuel ___.','reserve',['landing payload limit','maximum landing mass','operating empty mass','reserve fuel'],['p_l','m_lm','m_o','m_r'],['___','=','___','-','___','-','___']),
 ('fuel_limit','The fuel payload limit accounts for tank capacity and reserve ___.','fuel',['fuel payload limit','fuel capacity','mass ratio factor','reserve fuel','operating empty mass'],['p_f','m_fm','k','m_r','m_o'],['___','=','(', '___','-', '___',r'\times','___',')',r'\div','(', '___','-','1',')','-','___']),
 ('km','Kilometres equal metres divided by ___.','1000',['range in kilometres','range in metres'],['R_km','R_m'],['___','=','___',r'\div','1000']),
 ('payload_min','Allowed payload is the smallest of four payload ___.','limits',['allowed payload','structural payload limit','takeoff payload limit','landing payload limit','fuel payload limit'],['p','p_s','p_t','p_l','p_f'],['___','=',r'\min','(','___',',','___',',','___',',','___',')']),
]

def prerequisites():
    output=[]
    for key,sentence,word,names,symbols,parts in SPECS:
        # k appears twice in fuel_limit: a bank token needs two selectable
        # instances, supported by the original adapter's duplicate count.
        if key=='fuel_limit':
            names=[names[0],names[1],names[2],names[3],names[2],names[4]]
            symbols=[symbols[0],symbols[1],symbols[2],symbols[3],symbols[2],symbols[4]]
        distractors=[x for x in ('temperature','pressure','altitude','velocity') if x not in names][:3]
        latex=FORMULAS[key][0]
        # Single-name exercise has a fixed RHS and a single input slot.
        rhs=latex.split('=',1)[1]
        # introduce expects distinct blocks; duplicate answers are represented
        # once in the bank and materialized by formula_challenge as needed.
        generated=introduce('JET-'+key.upper().replace('_','-'), sentence, word,
            [x for x in ['temperature','velocity','altitude','1000'] if x != word][:3], latex, names, distractors,
            parts, symbols, parts, '='+rhs)
        for q in generated:
            if key=='fuel_limit' and q.get('mathematical_blocks'):
                q['allow_repeated_symbols']=True
            if q['type']=='formula_named':
                q['blocks']=list(dict.fromkeys(q['blocks']))
        output.extend(generated)
    return output
