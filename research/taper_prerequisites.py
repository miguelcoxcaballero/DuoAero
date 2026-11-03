"""Unintegrated word/quantity/symbol introductions for taper calculations.

Compound quotients use the existing inline division draft. They are not a
replacement for the required verified vertical fraction layout. Hints and
lesson order must not be enabled until that layout and native behavior pass.
"""
from speed_limits_lesson import introduce


def prerequisites():
    specs = [
        ('Q', 'Dynamic pressure is half the density times cruise speed ___.', 'squared',
         r'q=\frac{\rho V_{cr}^{2}}{2}',
         ['dynamic pressure','air density','cruise speed'], ['q','ρ','V_cr'],
         ['___','=',r'\frac12',r'\times','___',r'\times','___^2'], r'=\frac{\rho V_{cr}^{2}}{2}'),
        ('SMIN', 'Minimum wing area is twice weight divided by density, stall speed squared and maximum lift ___.', 'coefficient',
         r'S_{\min}=\frac{2W}{\rho V_s^2 C_{L,\max}}',
         ['minimum wing area','weight','air density','stall speed','maximum lift coefficient'],
         ['S_min','W','ρ','V_s','C_Lmax'],
         ['___','=',r'2\times','___',r'\div','(','___',r'\times','___^2',r'\times','___',')'],
         r'=\frac{2W}{\rho V_s^2 C_{L,\max}}'),
        ('DI', 'Induced drag is weight squared divided by dynamic pressure, pi, efficiency and wingspan ___.', 'squared',
         r'D_i=\frac{W^2}{q\pi e b^2}',
         ['induced drag','weight','dynamic pressure','span efficiency','wingspan'],
         ['D_i','W','q','e','b'],
         ['___','=','___^2',r'\div','(','___',r'\times',r'\pi',r'\times','___',r'\times','___^2',')'],
         r'=\frac{W^2}{q\pi e b^2}'),
        ('SMAX', 'Maximum wing area is the drag limit less induced drag, divided by dynamic pressure times zero-lift drag ___.', 'coefficient',
         r'S_{\max}=\frac{D_{\max}-D_i}{qC_{D0}}',
         ['maximum wing area','drag limit','induced drag','dynamic pressure','zero-lift drag coefficient'],
         ['S_max','D_max','D_i','q','C_D0'],
         ['___','=','(','___','-','___',')',r'\div','(','___',r'\times','___',')'],
         r'=\frac{D_{\max}-D_i}{qC_{D0}}'),
        ('BOUND', 'A taper bound is twice wing area divided by wingspan times root chord, minus ___.', 'one',
         r'\lambda=\frac{2S}{bc_r}-1',
         ['taper ratio','wing area','wingspan','root chord'], ['λ','S','b','c_r'],
         ['___','=',r'2\times','___',r'\div','(','___',r'\times','___',')','-','1'],
         r'=\frac{2S}{bc_r}-1'),
        ('WIDTH', 'The feasible interval width is the upper taper bound minus the lower taper ___.', 'bound',
         r'w_t=\lambda_{\max}-\lambda_{\min}',
         ['taper interval width','upper taper bound','lower taper bound'],
         ['w_t','λ_max','λ_min'], ['___','=','___','-','___'],
         r'=\lambda_{\max}-\lambda_{\min}'),
    ]
    result=[]
    for key,sentence,word,latex,names,symbols,parts,after in specs:
        distractors={'squared':['cubed','halved','unchanged'],
                     'coefficient':['force','area','pressure'],
                     'one':['zero','two','three'],
                     'bound':['speed','area','pressure']}[word]
        result.extend(introduce('TAPER-'+key,sentence,word,distractors,latex,names,
                                ['temperature','altitude','mass'],parts,symbols,parts,after))
    return result
