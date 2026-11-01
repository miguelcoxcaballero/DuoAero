"""Check introductory formula practice and arithmetic; Android UI is separate."""
import json
from pathlib import Path
from course_adapter import lesson_questions
from formula_exercises import formula_challenge

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))}
plan = json.loads((root/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
expected = {
    'TA1-0041-F1': ('INTRO-AXIAL-STIFFNESS', '4 MN/m'),
    'TA1-0068-F1': ('INTRO-CANTILEVER-STIFFNESS', '30 kN/m'),
    'TA1-0055-F1': ('INTRO-ASPECT-RATIO', '10'),
    'TA1-0180-F1': ('INTRO-TAPER-RATIO', '0.25'),
}
assert 12/3 == 4 and (3*80000/8)/1000 == 30
assert 20**2/40 == 10 and 1/4 == .25
for qid, (formula_id, answer) in expected.items():
    formula, question = lesson_questions([bank[qid]])
    assert (formula['id'], question['id']) == (formula_id, qid)
    assert question['formula_hint']['prerequisite'] == formula_id
    assert question['formula_hint']['latex'] == formula['formula_latex']
    assert question['options'][question['answer']] == answer
    assert formula['answer_blocks'][0] in formula['blocks']
    assert r'\frac' in formula['answer_blocks'][0]
    native = formula_challenge(formula)['promptInputChallenge']
    feedback = native['prompt']['gradingFeedbackSpecification']['staticFeedback']['gradingFeedback']
    assert feedback['taggedTextElement']['text'] == 'duoaero-latex:' + r'\textstyle ' + formula['formula_latex']
    assert native['input']['expressionBuildInput']['slotCount'] == 1
for node in plan:
    for lesson in node['lessons']:
        assert len(lesson_questions([bank[qid] for qid in lesson['ids']])) <= 20, lesson['id']
print('PASS: four introductory formula prerequisites and numerical answers; Android UI remains unverified.')
