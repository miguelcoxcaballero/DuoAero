"""Isolated 3-over-2 fraction fixture; never enable in a release build."""
import copy
from jet_family_prerequisites import prerequisites


def fixture():
    questions=[copy.deepcopy(q) for q in prerequisites() if q['id'].startswith('JET-RANGE')]
    assert len(questions)==4
    for q in questions:
        if q['id'] in ('JET-RANGE-NAMED-ALL','JET-RANGE'):
            q['inline_latex']=['___','=','___*___*___/___*___']
            assert len(q['answer_blocks'])==6
    return questions
