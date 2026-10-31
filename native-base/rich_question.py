"""Content adapter for the original mathChallengeBlob selectOne screen.

No layout implementation is supplied: selectOne and text are native schema types
present in the reference APK's math_l0_lessons.json. End-to-end rendering remains
subject to the native session integration check.
"""
import json


def text_latex(value):
    escapes = {'\\': r'\backslash{}', '{': r'\{', '}': r'\}',
               '%': r'\%', '&': r'\&', '#': r'\#', '_': r'\_',
               '$': r'\$'}
    return r'\text{' + ''.join(escapes.get(c, c) for c in value) + '}'


def content(parts, fallback):
    if parts is None:
        return text_latex(fallback)
    result = []
    for part in parts:
        if set(part) == {'latex'}:
            result.append(part['latex'])
        elif set(part) == {'text'}:
            result.append(text_latex(part['text']))
        else:
            raise ValueError('Expected exactly one text or latex field')
    return ''.join(result)


def choice_blob(question):
    rich = question.get('rich_text', {})
    options = rich.get('options', [None] * len(question['options']))
    if len(options) != len(question['options']):
        raise ValueError('Rich options must align with plain options')
    correct = question['answer']
    if type(correct) is not int or not 0 <= correct < len(options):
        raise ValueError('Invalid correct answer index')
    answer = {'type': 'text', 'value': content(options[correct], question['options'][correct])}
    feedback = {'type': 'text', 'value': content(rich.get('explanation'), question['explanation'])}
    # All content is encoded as JSON literals, never interpolated as JS source.
    grading = ('function grade(variables) { const expected = ' + str(correct) + '; '
               'const count = ' + str(len(options)) + '; let isCorrect = true; '
               'for (let i=0;i<count;i++) { '
               'const selected = !!(variables["answer_"+i] && variables["answer_"+i].selected); '
               'if (selected !== (i === expected)) isCorrect = false; } '
               'return {isCorrect:isCorrect, feedback:' + json.dumps(feedback) +
               ', displayAnswer:' + json.dumps(answer) + '}; }')
    blob = {
        'layout': 'selectOne',
        'instruction': {'type': 'text', 'value': text_latex('Select the correct answer')},
        'shirt': {'type': 'text', 'value': content(rich.get('stem'), question['stem'])},
        'pants': [{'type': 'button', 'id': 'answer_' + str(i), 'width': 'full',
                   'child': {'type': 'text', 'value': content(options[i], option)}}
                  for i, option in enumerate(question['options'])],
        'onesie': None, 'headband': None, 'grading_function': grading,
    }
    return {'id': question['id'], 'type': 'mathChallengeBlob',
            'challengeBlob': json.dumps(blob, ensure_ascii=False),
            'challengeSchemaVersion': {'major': 0, 'minor': 1, 'patch': 9},
            'trackingMetadata': {}, 'hintBlobOverride': '', 'gradingFeedbackBlobOverride': ''}
