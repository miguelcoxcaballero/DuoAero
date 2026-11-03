"""Research-only session partition; does not modify course or award credit."""
from taper_domain import bounds
from taper_prerequisites import prerequisites
from taper_stages import draft


def distribution(bank):
    formulas=prerequisites()
    assert len(formulas)==28
    lessons=[{'id':f'taper-formulas-{i+1}', 'questions':formulas[start:end]}
             for i,(start,end) in enumerate(((0,12),(12,28)))]
    cases=[source for source in bank if bounds(source) is not None]
    assert len(cases)==10
    for source in cases:
        questions,_,_=draft(source)
        assert len(questions) in (27,28)
        for part,segment in enumerate((questions[:14],questions[14:]),1):
            lessons.append({'id':f'taper-practice-{source["id"]}-{part}', 'questions':segment})
    assert all(10<=len(lesson['questions'])<=20 for lesson in lessons)
    return lessons
