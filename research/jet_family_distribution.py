"""Draft distribution of authored controls, not a course migration.

The full named formula layouts still require native visual acceptance. The
returned IDs are stable research identifiers, not completion credits.
"""
from audit_jet_families import audit
from jet_family_prerequisites import prerequisites
from jet_family_steps import draft


def distribution(bank):
    teaching = prerequisites()
    assert len(teaching)==56
    lessons=[]
    # Keep the four successive versions of every formula together and teach
    # all prerequisites before any calculation that may expose its hint.
    for index,(start,end) in enumerate(((0,12),(12,24),(24,40),(40,56)),1):
        lessons.append({'id':f'jet-formulas-{index}', 'questions':teaching[start:end]})
    cases=[q for q in bank if audit(q)]
    assert len(cases)==20
    for source in cases:
        lessons.append({'id':'jet-practice-'+source['id'], 'questions':draft(source)})
    assert all(10<=len(lesson['questions'])<=20 for lesson in lessons)
    return [lessons[i:i+4] for i in range(0,len(lessons),4)]
