"""Translate supported question data into the original APK's native session models.

This is a model adapter, not a replacement UI. Text-entry and ordering need the
original grading contract before they can be enabled. Never silently downgrade them.
"""
import html
import json
from pathlib import Path
from rich_question import choice_blob

ROOT = Path(__file__).resolve().parents[1]

def figure(text):
    return {'underlyingEntity': {'noEntity': {}}, 'taggedTextElement': {'text': html.escape(text)}}

def challenge(question):
    result = {'id': question['id']}
    kind = question['type']
    if kind == 'choice' and question.get('rich_text'):
        return choice_blob(question)
    if kind == 'choice':
        result.update(type='assist', prompt=question['stem'], correctIndex=question['answer'],
                      options=[{'text': value} for value in question['options']])
    elif kind == 'multi':
        result.update(type='mathMultiSelect', noHint={}, promptInputChallenge={
            'prompt': {'instruction': {'text': 'Select all correct answers'},
                       'body': figure(question['stem']),
                       'gradingFeedbackSpecification': {'staticFeedback': {'gradingFeedback': figure(question['explanation'])}}},
            'input': {'productSelectInput': {
                'correctIndices': question['answer'],
                'answerOptions': [{'choice': figure(value), 'choiceFeedbackRepresentation': {'gradingFeedback': figure(value)}} for value in question['options']]
            }}
        })
    elif kind == 'matching':
        result.update(type='mathMatch', noHint={}, matchChallenge={
            'instruction': {'text': html.escape(question['stem'])},
            'pairs': [{'left': figure(left), 'right': figure(right)} for left, right in question['pairs']]
        })
    else:
        raise NotImplementedError(f"{question['id']}: native grading adapter for {kind} is not implemented")
    return result

def session(questions, identifier):
    return {'id': identifier, 'type': 'GLOBAL_PRACTICE', 'fromLanguage': 'en',
            'learningLanguage': 'en', 'challenges': [challenge(q) for q in questions]}

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
