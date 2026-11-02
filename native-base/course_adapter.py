"""Translate supported question data into the original APK's native session models.

This is a model adapter, not a replacement UI. Gap exercises use a native word
bank; ordering uses the original expression-build slots with strict sequence
grading. Their runtime acceptance is separate from successful decoding.
"""
import html
import json
import base64
import re
from pathlib import Path
from rich_question import choice_blob, difficulty_stars, content, text_latex
from math_notation import parts as notation_parts
from formula_exercises import formula_challenge
from formula_words import word_introduction, named_equation, named_equation_all, choices_in_stable_order, INLINE_SYMBOLS, KINDS, MULTI_NAMED

ROOT = Path(__file__).resolve().parents[1]

def figure(text):
    symbolic = any('latex' in part for part in notation_parts(text))
    value = 'duoaero-latex:' + content(None, text) if symbolic else html.escape(text)
    return {'underlyingEntity': {'noEntity': {}}, 'taggedTextElement': {'text': value}}

def challenge(question):
    result = {'id': question['id']}
    kind = question['type']
    if kind == 'choice':
        # Only explicitly reviewed questions carry a prerequisite-linked
        # formula. The authoring validator checks that it appears earlier.
        return choice_blob(question, include_formula_hint=bool(question.get('formula_hint')))
    if kind == 'formula_blocks':
        return formula_challenge(question)
    if kind == 'formula_named':
        adapter = dict(question, prefix='')
        result = formula_challenge(adapter, mathematical=bool(question.get('mathematical_blocks')))
        segments = []
        if 'inline_latex' in question:
            for part in question['inline_latex']:
                segments.append('___' if part == '___' else 'duoaero-negative-exponent' if part == 'e^-___' else 'duoaero-fraction-slots' if part == '___/___' else 'duoaero-squared-fraction-slots' if part == '___^2/___' else 'duoaero-squared-over-twice' if part == '___^2/2*___' else 'duoaero-product-fraction-21' if part == '___*___/___' else 'duoaero-product-fraction-22' if part == '___*___/___*___' else 'duoaero-power-slot:' + part[4:] if re.fullmatch(r'___\^\d{1,2}',part) else 'duoaero-math:formula:' + r'\textstyle ' + part)
            if segments.count('___') + segments.count('duoaero-negative-exponent') + 2*(segments.count('duoaero-fraction-slots')+segments.count('duoaero-squared-fraction-slots')+segments.count('duoaero-squared-over-twice')) + 3*segments.count('duoaero-product-fraction-21') + 4*segments.count('duoaero-product-fraction-22') + sum(p.startswith('duoaero-power-slot:') for p in segments) != len(question['answer_blocks']):
                raise ValueError('Named equation slots do not match answers: ' + question['id'])
        else:
            if question['before_latex']:
                segments.append('duoaero-math:formula:' + r'\textstyle ' + question['before_latex'])
            segments.append('___')
            if question['after_latex']:
                segments.append('duoaero-math:formula:' + r'\textstyle ' + question['after_latex'])
        payload = base64.b64encode(json.dumps(segments, ensure_ascii=False).encode('utf-8')).decode('ascii')
        prompt = result['promptInputChallenge']['prompt']
        prompt['body'] = {'underlyingEntity': {'noEntity': {}}, 'taggedTextElement': {
            'text': 'duoaero-latex:duoaero-gap:' + payload}}
        prompt['gradingFeedbackSpecification']['staticFeedback']['gradingFeedback'] = {
            'underlyingEntity': {'noEntity': {}}, 'taggedTextElement': {
                'text': 'duoaero-latex:' + r'\textstyle ' + question['formula_latex']}}
        return result
    if kind == 'gap':
        distractors = {
            'INTERACTIVE-1': ['increases', 'stabilizes', 'doubles'],
            'INTERACTIVE-2': ['density', 'material', 'temperature'],
        }
        choices = question.get('distractors', distractors.get(question['id']))
        if not choices:
            raise ValueError('Gap word bank needs reviewed distractors: ' + question['id'])
        blocks = [question['answer'][0], *choices]
        if question.get('formula_word_symbols'):
            blocks = choices_in_stable_order(question['id'], blocks)
        adapter = dict(question, prefix='',
                       blocks=blocks,
                       answer_blocks=[question['answer'][0]])
        result = formula_challenge(adapter, mathematical=False)
        instruction, separator, sentence = question['stem'].partition(':')
        if not separator or sentence.count('___') != 1:
            raise ValueError('Gap sentence needs exactly one reviewed placeholder: ' + question['id'])
        words = [s for s in re.split(r'(\s+|___)', sentence.strip()) if s and not s.isspace()]
        # Avoid an isolated punctuation glyph at the top of a taller token
        # when the missing word is the last item in the sentence.
        if len(words)>1 and words[-2]=='___' and words[-1] in ('.','!','?'):
            words.pop()
        parts = []
        for word in words:
            if word == '___':
                parts.append(word)
                continue
            # Formula-word questions explicitly teach the names of these
            # symbols. Render them as math while leaving ordinary prose alone.
            match = re.fullmatch(r'(\(?)([A-Za-z][A-Za-z0-9-]*)([),.;]{0,3})', word)
            if question.get('formula_word_symbols') and match and match.group(2) in INLINE_SYMBOLS:
                symbol = INLINE_SYMBOLS[match.group(2)]
                parts.append('duoaero-math:' + match.group(2) + ':' + match.group(1) + symbol + match.group(3))
            else:
                parts.append(text_latex(word))
        payload = base64.b64encode(json.dumps(parts, ensure_ascii=False).encode('utf-8')).decode('ascii')
        prompt = result['promptInputChallenge']['prompt']
        prompt['instruction']['text'] = difficulty_stars(question) + ' ' + instruction
        prompt['body'] = {'underlyingEntity': {'noEntity': {}}, 'taggedTextElement': {
            'text': 'duoaero-latex:duoaero-gap:' + payload}}
        return result
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

def lesson_questions(questions, expand_steps=True, teach_words=False):
    """Turn reviewed multi-step exercises into consecutive original challenges."""
    expanded = []
    for question in questions:
        steps = question.get('lesson_steps') if expand_steps else None
        if not steps:
            expanded.append(question)
            continue
        if question['type'] != 'choice' or len(steps) < 2 or steps[-1]['id'] != question['id']:
            raise ValueError('Invalid reviewed lesson steps: ' + question['id'])
        for step in steps:
            # Each expanded question teaches or uses its own formula. A hint
            # on the unsplit source is not automatically valid for every step.
            part = {k: v for k, v in question.items() if k not in ('lesson_steps', 'rich_text', 'formula_hint')}
            part.update(step)
            expanded.append(part)
    if teach_words:
        expanded = [part for q in expanded for part in
                    ([word_introduction(q)]
                     + ([named_equation_all(q)] if KINDS[q['id']] in MULTI_NAMED else [])
                     + [named_equation(q), q] if q['type'] == 'formula_blocks' else [q])]
    ids = [q['id'] for q in expanded]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate native challenge IDs in lesson')
    return expanded


def session(questions, identifier, skill_id='duoaero_aerospace_diagnostic', expand_steps=True, teach_words=False):
    # Original MathSessionCoordinator requires a Math skill ID to start the
    # original JS grader. GLOBAL_PRACTICE can display blobs but cannot grade them.
    return {'id': identifier, 'type': 'MATH_LESSON', 'fromLanguage': 'en',
            'skillId': skill_id, 'levelIndex': 0, 'levelSessionIndex': 0,
            'metadata': {'id': identifier, 'type': 'math_lesson'},
            'challenges': [challenge(q) for q in lesson_questions(questions, expand_steps, teach_words)]}

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
