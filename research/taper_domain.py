"""Physics checks and repair for practice wings with a nonnegative tip chord."""
import math,re
N=r'([0-9]+(?:\.[0-9]+)?)'
PATTERN=re.compile(r'An untwisted trapezoidal wing has fixed b='+N+r' m and root chord='+N+
 r' m\. It must carry '+N+r' N at rho='+N+r', achieve Vs<='+N+r' m/s with CLmax='+N+
 r', and require D<='+N+r' N at Vcr='+N+r' m/s\. Use e='+N+r', CD0='+N)

def bounds(question):
    m=PATTERN.match(question.get('stem',''))
    if not m:return None
    b,root,weight,rho,vs,cl,drag,speed,e,cd=map(float,m.groups())
    q=0.5*rho*speed*speed
    min_area=2*weight/(rho*vs*vs*cl)
    induced=weight*weight/(q*math.pi*e*b*b)
    max_area=(drag-induced)/(q*cd)
    return 2*min_area/(b*root)-1,2*max_area/(b*root)-1

def repair(question):
    limits=bounds(question)
    if limits is None:raise ValueError('Not the reviewed taper family')
    lower,upper=limits
    if lower>=0:return None
    q=dict(question)
    q['stem']=q['stem'].replace('Ignoring any additional geometric cap,',
      'Require a nonnegative tip chord (lambda >= 0), with no additional geometric cap;')
    q['steps']=list(question.get('steps',[]))
    if 'Intersect the taper bounds with a nonnegative tip chord' not in q['steps']:
        q['steps'].append('Intersect the taper bounds with a nonnegative tip chord')
    # Keep the complete source stem for audit; the compact rich prompt puts
    # the question and physical domain first, followed by the stated inputs.
    b,root,weight,rho,vs,cl,drag,speed,e,cd=PATTERN.match(question['stem']).groups()
    q['rich_text']={'stem':[
      {'text':'Find the feasible taper-width with '}, {'latex':r'\lambda\geq 0'}, {'text':'. '},
      {'latex':r'b='+b+r'\,\mathrm m,\ c_r='+root+r'\,\mathrm m,\ W='+weight+r'\,\mathrm N,\ \rho='+rho}, {'text':'. '},
      {'latex':r'V_s\le '+vs+r'\,\mathrm{m/s},\ C_{L,\max}='+cl}, {'text':'. '},
      {'latex':r'D\le '+drag+r'\,\mathrm N,\ V_{cr}='+speed+r'\,\mathrm{m/s},\ e='+e+r',\ C_{D0}='+cd}, {'text':'. '},
      {'latex':r'S=\frac{bc_r(1+\lambda)}{2},\ q=\frac12\rho V_{cr}^{2},\ D_i=\frac{W^2}{q\pi e b^2}'}, {'text':'.'}]}
    q['content_revision']=2
    # Earlier residual checks validated the unphysical algebra only.
    q['checks']=[]
    old_width=upper-lower
    if upper>=0:
        correct=f'{upper:.5f}'
        options=[correct,f'{old_width:.5f}',f'{upper/2:.5f}','No feasible taper ratio']
        explanation=(f'The stall and drag bounds are {lower:.6f} and {upper:.6f}. '
                     f'The physical lower bound is 0, so the feasible interval is '
                     f'0 to {upper:.6f} and its width is {upper:.5f}.')
        explanations={options[1]:'Uses the negative algebraic lower bound as a physical taper ratio.',
          options[2]:'Halves the physical interval width.',options[3]:'A nonnegative interval exists.'}
    else:
        correct='No feasible taper ratio'
        options=[correct,f'{old_width:.5f}',f'{abs(upper):.5f}',f'{old_width/2:.5f}']
        explanation=(f'The drag constraint requires lambda <= {upper:.6f}, '
                     'but a nonnegative tip chord requires lambda >= 0. '
                     'No taper ratio satisfies both constraints.')
        explanations={options[1]:'Subtracts two negative limits without enforcing a nonnegative tip chord.',
          options[2]:'The magnitude of a negative upper bound is not a feasible taper ratio.',
          options[3]:'A positive width between negative bounds is not a physical interval.'}
    assert len(set(options))==4
    # Preserve the original correct-position index while changing the content.
    index=question['answer'];options[0],options[index]=options[index],options[0]
    q['options']=options;q['answer']=index;q['explanation']=explanation
    explanations[correct]='Correct. '+explanation;q['option_explanations']=explanations
    return q
