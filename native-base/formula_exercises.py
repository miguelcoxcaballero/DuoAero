"""Formula recall inputs for the original Math token and expression controllers.

These are native model inputs, not a replacement interface. A scoped extension
to the original numeric grader compares marked Aerospace symbolic expressions. UI acceptance is
recorded separately from successful serialization.
"""
from collections import Counter
import html
import json
from pathlib import Path

SOURCE = {
    'kind': 'practice',
    'title': 'Tecnología Aeroespacial - Primer parcial - V6 desde la base paso a paso',
    'url': '',  # Private source: user authorized title and cited pages only.
}


def entity(value):
    operators = {'×': 'MULTIPLICATION', '÷': 'DIVISION', '+': 'ADDITION', '=': 'EQUALITY'}
    if value in operators:
        return {'symbol': operators[value]}
    return {'variable': {'algebraic': {'name': 'duoaero:' + value}}}


def math_latex(value):
    # Formula components are mathematical terms, never arbitrary HTML/JS.
    symbols = {'ρ': r'\rho ', 'π': r'\pi ', 'Δ': r'\Delta ', 'ṁ': r'\dot{m}',
               '½': r'\frac{1}{2}', '²': '^2', '³': '^3', '×': r'\times ',
               '÷': r'\div ', '−': '-', 'α': r'\alpha ', 'η': r'\eta ', 'γ': r'\gamma '}
    return r'\textstyle ' + ''.join(symbols.get(c, c) for c in value)


def figure(value, symbolic=False, latex=False):
    return {'underlyingEntity': {'entity': entity(value)} if symbolic else {'noEntity': {}},
            'taggedTextElement': {'text': 'duoaero-latex:' + math_latex(value) if latex else html.escape(value)}}


def formula_challenge(question, mathematical=True):
    tokens = question['blocks']
    answer = question['answer_blocks']
    if not answer or any(a not in tokens for a in answer):
        raise ValueError('Every required formula block must be available')
    if len(tokens) != len(set(tokens)):
        raise ValueError('Duplicate choice labels need explicit identities')
    many = len(answer) > 1
    expected = {'list': {'values': [entity(a) for a in answer]}} if many else entity(answer[0])
    # The legacy factory rejects STRUCTURAL before creating the controller.
    # VALUE preserves its model conversion. The scoped symbolic comparison
    # extension handles only the explicit duoaero: algebraic identifiers.
    grading = {'gradingRules': [{'gradingMethod': 'VALUE',
                                'exactGrading': [{'exactAnswer': expected}],
                                'intervalGrading': []}],
               'numCorrectAnswersRequired': 1, 'answersMustBeDistinct': False,
               'answersMustBeOrdered': True}
    body = {'underlyingEntity': {'noEntity': {}}, 'mathSequenceElement': {
        'orientation': 'HORIZONTAL', 'elements': [figure(question['prefix'], latex=mathematical),
            {'underlyingEntity': {'noEntity': {}}, 'blankElement': {
                'size': len(answer), 'text': {'text': ''},
                'accessibilityLabel': 'Missing formula components'}}]}}
    if mathematical:
        # The original interactive slot row supplies the actual blanks.
        body = figure(question['prefix'], latex=True)
    inputs = {'gradingSpecification': grading,
              'dragChoices': [figure(t, True, latex=mathematical) for t in tokens for _ in range(max(1, Counter(answer)[t]))]}
    inputs['slotCount'] = len(answer)
    if mathematical:
        # Use the authored complete formula, not prose or a reconstruction from
        # choice labels. Keep TeX intact for the original LatexString renderer.
        solution = question.get('formula_latex')
        if not isinstance(solution, str) or not solution.strip():
            raise ValueError('Formula exercise requires a complete LaTeX solution: ' + question['id'])
        feedback = {'underlyingEntity': {'noEntity': {}},
                    'taggedTextElement': {'text': 'duoaero-latex:' + r'\textstyle ' + solution}}
    else:
        feedback = figure(question['explanation'])
    return {'id': question['id'], 'type': 'mathExpressionBuild',
            'noHint': {}, 'promptInputChallenge': {'prompt': {
                'instruction': {'text': '★' * question['difficulty'] + ' ' + question['stem']},
                'body': body,
                'gradingFeedbackSpecification': {'staticFeedback': {
                    'gradingFeedback': feedback}}},
                'input': {'expressionBuildInput': inputs}}}


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
    bank = json.loads((root / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))
    questions.extend(q for q in bank if q['type'] == 'formula_blocks')
    for question in bank:
        for step in question.get('lesson_steps',[]):
            if step.get('type') == 'formula_blocks':
                part = {k: v for k, v in question.items() if k not in ('lesson_steps', 'rich_text', 'formula_hint')}
                part.update(step)
                questions.append(part)
    session = {'id': 'duoaero_formula_blocks_diagnostic', 'type': 'MATH_LESSON',
               'fromLanguage': 'en', 'skillId': 'duoaero_aerospace_diagnostic',
               'levelIndex': 0, 'levelSessionIndex': 0,
               'metadata': {'id': 'duoaero_formula_blocks_diagnostic', 'type': 'math_lesson'},
               'challenges': [formula_challenge(q) for q in questions]}
    destination = root / 'native-base/tests/fixtures/aerospace_formula_lesson.json'
    destination.write_text(json.dumps(session, ensure_ascii=False), encoding='utf-8')
    print(f'{len(questions)} formula exercises including the complete textbook bank; runtime rendering and grading must be tested.')
