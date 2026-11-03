"""Build an isolated candidate plan for the ten range problems in memory.

This is not connected to production. No historical credit or reward is
created; a caller must still validate historic sessions and Android rendering.
"""
import copy
from audit_jet_families import audit
from jet_family_prerequisites import prerequisites
from jet_family_steps import draft

TEACH_KEYS=('DRY','TANK','MINIMUM','BURN','RESERVE','RATIO','LOG','RANGE','KM')


def candidate(bank, plan):
    bank=copy.deepcopy(bank);plan=copy.deepcopy(plan)
    cases=[q for q in bank if audit(q) and audit(q)[0]=='range']
    assert len(cases)==10
    case_ids={q['id'] for q in cases}
    by_id={q['id']:q for q in bank}
    all_prereqs=prerequisites()
    teaching=[]
    for key in TEACH_KEYS:
        items=[q for q in all_prereqs if q['id'] in
               ('JET-'+key+'-WORDS','JET-'+key+'-NAMED-ALL',
                'JET-'+key+'-NAMED','JET-'+key)]
        assert len(items)==4,key
        wrapper=copy.deepcopy(cases[0]);wrapper['id']='JET-'+key
        wrapper['lesson_steps']=items
        teaching.append(wrapper)
    bank.extend(teaching)
    for q in cases:
        q['lesson_steps']=draft(q)
    for node in plan:
        for lesson in node['lessons']:
            lesson['ids']=[q for q in lesson['ids'] if q not in case_ids]
        node['ids']=[q for q in node['ids'] if q not in case_ids]
    prefix='2.2-range-draft'
    teacher_lessons=[{'id':prefix+'-formula-lesson-'+str(i),
                      'name':'Range formulas · Lesson '+str(i+1),
                      'ids':[q['id'] for q in teaching[i*3:i*3+3]]} for i in range(3)]
    nodes=[{'id':prefix+'-formulas','topic':'2.2','name':'Range formulas',
            'ids':[q['id'] for q in teaching],'lessons':teacher_lessons}]
    for group in range(3):
        chunk=cases[group*4:(group+1)*4]
        lessons=[{'id':prefix+'-case-'+q['id'],
                  'name':'Range practice · '+str(group*4+i+1), 'ids':[q['id']]}
                 for i,q in enumerate(chunk)]
        nodes.append({'id':prefix+'-practice-'+str(group),'topic':'2.2',
                      'name':'Range practice', 'ids':[q['id'] for q in chunk], 'lessons':lessons})
    insert=next(i for i,n in enumerate(plan) if n['id']=='2.2-2-point-1')
    plan[insert:insert]=nodes
    return bank,plan
