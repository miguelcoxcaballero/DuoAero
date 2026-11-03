"""Validate explicit multi-block symbolic prerequisites without treating words as symbols."""
import re
from course_adapter import challenge

_SYMBOL=re.compile(r'^[A-Za-zα-ωΑ-ΩΔρμγ](?:_[A-Za-z0-9]+)?$')

def multi_symbol_prerequisite(question):
    if question.get('type')!='formula_named' or question.get('mathematical_blocks') is not True:
        return False
    answers=question.get('answer_blocks',[]);blocks=question.get('blocks',[])
    if (len(answers)<2 or len(blocks)!=len(set(blocks)) or
        (len(answers)!=len(set(answers)) and question.get('allow_repeated_symbols') is not True)):
        raise ValueError('Invalid multi-symbol formula blocks: '+question.get('id',''))
    if not question.get('formula_latex') or not all(x in blocks and (x == 'mu' or _SYMBOL.fullmatch(x)) for x in answers):
        raise ValueError('Invalid multi-symbol formula: '+question.get('id',''))
    # The original adapter checks the exact number of slots and converts every
    # operand into a real native challenge. This does not prove the physics.
    challenge(question)
    return True

def validate_hint_prerequisites(question, seen_formulas):
    hint=question.get('formula_hint')
    if not hint:
        return
    assert question.get('type')=='choice' and isinstance(hint.get('latex'),str) and hint['latex'].strip()
    prerequisites=[hint.get('prerequisite')]+hint.get('additional_prerequisites',[])
    assert len(prerequisites)==len(set(prerequisites)), (question['id'],prerequisites)
    for prerequisite in prerequisites:
        assert prerequisite in seen_formulas, (question['id'],prerequisite)
