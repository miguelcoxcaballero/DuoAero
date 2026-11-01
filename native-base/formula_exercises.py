"""Formula recall inputs for the original Math token and expression controllers.

These are native model inputs, not a replacement interface. The controller's
structural grader compares the selected symbolic expression. UI acceptance is
recorded separately from successful serialization.
"""
import html
import json
from pathlib import Path

SOURCE = {
    'kind': 'practice',
    'title': 'Tecnología Aeroespacial - Primer parcial - V6 desde la base paso a paso',
    'url': 'https://drive.google.com/file/d/1rFE-y4JTn__S0Rj52unvKb7LyW78_PfH/view',
    'sha256': 'd07019ff2d22d5969bf651d1435cc7c6f47ef588874cbeefd50eb13c3232d6ac',
    'edition': 'V6, November 2026',
}


def entity(value):
    operators = {'×': 'MULTIPLICATION', '+': 'ADDITION', '=': 'EQUALITY'}
    if value in operators:
        return {'symbol': operators[value]}
    return {'variable': {'algebraic': {'name': value}}}


def figure(value, symbolic=False):
    return {'underlyingEntity': {'entity': entity(value)} if symbolic else {'noEntity': {}},
            'taggedTextElement': {'text': html.escape(value)}}


def formula_challenge(question):
    tokens = question['blocks']
    answer = question['answer_blocks']
    if not answer or any(a not in tokens for a in answer):
        raise ValueError('Every required formula block must be available')
    if len(tokens) != len(set(tokens)):
        raise ValueError('Duplicate choice labels need explicit identities')
    many = len(answer) > 1
    expected = {'mathList': {'values': [entity(a) for a in answer]}} if many else entity(answer[0])
    grading = {'gradingRules': [{'gradingMethod': 'STRUCTURAL',
                                'exactGrading': [{'exactAnswer': expected}],
                                'intervalGrading': []}],
               'numCorrectAnswersRequired': 1, 'answersMustBeDistinct': False,
               'answersMustBeOrdered': True}
    body = {'underlyingEntity': {'noEntity': {}}, 'mathSequenceElement': {
        'orientation': 'HORIZONTAL', 'elements': [figure(question['prefix']),
            {'underlyingEntity': {'noEntity': {}}, 'blankElement': {
                'size': len(answer), 'text': {'text': ''},
                'accessibilityLabel': 'Missing formula components'}}]}}
    inputs = {'gradingSpecification': grading,
              'dragChoices': [figure(t, True) for t in tokens]}
    if many:
        inputs['slotCount'] = len(answer)
    else:
        inputs.update(placeholderText={'text': 'Drag the missing term here'},
                      alignment='ALIGNMENT_CENTER')
    return {'id': question['id'], 'type': 'mathExpressionBuild' if many else 'mathWordProblemTokenDrag',
            'noHint': {}, 'promptInputChallenge': {'prompt': {
                'instruction': {'text': '★' * question['difficulty'] + ' ' + question['stem']},
                'body': body,
                'gradingFeedbackSpecification': {'staticFeedback': {
                    'gradingFeedback': figure(question['explanation'])}}},
                'input': {'expressionBuildInput' if many else 'tokenDragInput': inputs}}}


def prototypes():
    return [
        {'id': 'BOOK-V6-FORMULA-Q', 'type': 'formula_blocks', 'difficulty': 1,
         'topic': '2.4', 'subtopic': 'Dynamic pressure',
         'stem': 'Complete the dynamic pressure formula', 'prefix': 'q = ½ ρ',
         'blocks': ['V', 'V²', 'S', 'C_L', 'V³', '1/V'], 'answer_blocks': ['V²'],
         'formula_latex': r'q=\frac{1}{2}\rho V^2',
         'explanation': 'q = ½ ρ V². Dynamic pressure is proportional to density and to the square of airspeed; wing area is not part of q.',
         'origin': dict(SOURCE, page=88, pdf_page=89)},
        {'id': 'BOOK-V6-FORMULA-GAS', 'type': 'formula_blocks', 'difficulty': 2,
         'topic': '2.1', 'subtopic': 'Atmosphere and ideal gas',
         'stem': 'Build the ideal-gas pressure expression', 'prefix': 'p =',
         'blocks': ['T', 'ρ', '×', 'R_a', 'V', 'S', '+'],
         'answer_blocks': ['ρ', '×', 'R_a', '×', 'T'],
         'formula_latex': r'p=\rho R_a T',
         'explanation': 'p = ρ R_a T. Use absolute temperature in kelvins. R_a is the specific gas constant for air, not the universal molar gas constant.',
         'origin': dict(SOURCE, page=14, pdf_page=15)},
    ]


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    questions = prototypes()
    session = {'id': 'duoaero_formula_blocks_diagnostic', 'type': 'MATH_LESSON',
               'fromLanguage': 'en', 'skillId': 'duoaero_aerospace_diagnostic',
               'levelIndex': 0, 'levelSessionIndex': 0,
               'metadata': {'id': 'duoaero_formula_blocks_diagnostic', 'type': 'math_lesson'},
               'challenges': [formula_challenge(q) for q in questions]}
    destination = root / 'native-base/tests/fixtures/aerospace_formula_lesson.json'
    destination.write_text(json.dumps(session, ensure_ascii=False), encoding='utf-8')
    print('Two textbook formula prototypes; runtime rendering and grading must be tested.')
