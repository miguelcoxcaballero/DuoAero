"""Translate supported question data into the original APK's native session models.

This is a model adapter, not a replacement UI. Gap exercises use a native word
bank; ordering uses the original expression-build slots with strict sequence
grading. Their runtime acceptance is separate from successful decoding.
"""
import html
import json
from pathlib import Path
from rich_question import choice_blob, difficulty_stars, content
from math_notation import parts as notation_parts
from formula_exercises import formula_challenge

ROOT = Path(__file__).resolve().parents[1]

def figure(text):
    symbolic = any('latex' in part for part in notation_parts(text))
    value = 'duoaero-latex:' + content(None, text) if symbolic else html.escape(text)
    return {'underlyingEntity': {'noEntity': {}}, 'taggedTextElement': {'text': value}}

def challenge(question):
    result = {'id': question['id']}
    kind = question['type']
    if kind == 'choice':
        return choice_blob(question)
    if kind == 'formula_blocks':
        return formula_challenge(question)
    if kind == 'gap':
        distractors = {
            'INTERACTIVE-1': ['increases', 'stabilizes', 'doubles'],
            'INTERACTIVE-2': ['density', 'material', 'temperature'],
        }
        if question['id'] not in distractors:
            raise ValueError('Gap word bank needs reviewed distractors: ' + question['id'])
        adapter = dict(question, prefix='Missing word:',
                       blocks=[question['answer'][0], *distractors[question['id']]],
                       answer_blocks=[question['answer'][0]])
        return formula_challenge(adapter, mathematical=False)
    if kind == 'order':
        adapter = dict(question, prefix='Sequence:', blocks=question['items'],
                       answer_blocks=[question['items'][i] for i in question['answer']])
        return formula_challenge(adapter, mathematical=False)
    if kind == 'multi':
        result.update(type='mathMultiSelect', noHint={}, promptInputChallenge={
            'prompt': {'instruction': {'text': difficulty_stars(question) + ' Select all correct answers'},
                       'body': figure(question['stem']),
                       'gradingFeedbackSpecification': {'staticFeedback': {'gradingFeedback': figure(question['explanation'])}}},
            'input': {'productSelectInput': {
                'correctIndices': question['answer'],
                'answerOptions': [{'choice': figure(value), 'choiceFeedbackRepresentation': {'gradingFeedback': figure(value)}} for value in question['options']]
            }}
        })
    elif kind == 'matching':
        result.update(type='mathMatch', noHint={}, matchChallenge={
            'instruction': {'text': difficulty_stars(question) + ' ' + html.escape(question['stem'])},
            'pairs': [{'left': figure(left), 'right': figure(right)} for left, right in question['pairs']]
        })
    else:
        raise NotImplementedError(f"{question['id']}: native grading adapter for {kind} is not implemented")
    return result

def session(questions, identifier, skill_id='duoaero_aerospace_diagnostic'):
    # Original MathSessionCoordinator requires a Math skill ID to start the
    # original JS grader. GLOBAL_PRACTICE can display blobs but cannot grade them.
    return {'id': identifier, 'type': 'MATH_LESSON', 'fromLanguage': 'en',
            'skillId': skill_id, 'levelIndex': 0, 'levelSessionIndex': 0,
            'metadata': {'id': identifier, 'type': 'math_lesson'},
            'challenges': [challenge(q) for q in questions]}

if __name__ == '__main__':
    bank = json.loads((ROOT/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
    fixtures = []
    unsupported = []
    for question in bank:
        try:
            fixtures.append(session([question], question['id']))
        except NotImplementedError as error:
            unsupported.append(str(error))
    destination = ROOT/'native-base/tests/fixtures'
    destination.mkdir(exist_ok=True)
    (destination/'native_sessions.json').write_text(json.dumps(fixtures, ensure_ascii=False), encoding='utf-8')
    print(f'{len(fixtures)} native model fixtures; {len(unsupported)} explicitly unsupported:')
    print('\n'.join(unsupported))
