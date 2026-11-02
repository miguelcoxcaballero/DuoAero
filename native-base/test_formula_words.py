"""Verify authored word introductions and their actual catalog order.

This does not establish Android rendering or touchscreen behavior.
"""
import base64
import json
from pathlib import Path
from course_adapter import challenge, lesson_questions, session
from formula_words import KINDS, MULTI_NAMED

root = Path(__file__).resolve().parents[1]
bank = {q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
for source_id,formula_id,expected in (
    ('TA1-0180-F1','INTRO-TAPER-RATIO',['___','duoaero-math:formula:\\textstyle =','duoaero-fraction-slots']),
    ('TA1-0078-D2','TA1-0078-D2-F2',['duoaero-fraction-slots','duoaero-math:formula:\\textstyle =','duoaero-math:formula:\\textstyle 1','duoaero-math:formula:\\textstyle -','___']),
    ('TA1-0107-D2','TA1-0107-D2-F3',['duoaero-power-slot:2','duoaero-math:formula:\\textstyle =','___','duoaero-math:formula:\\textstyle \\times','___','duoaero-math:formula:\\textstyle \\times','___']),
    ('TA1-0055-F1','INTRO-ASPECT-RATIO',['___','duoaero-math:formula:\\textstyle =','duoaero-squared-fraction-slots']),
):
    named=next(q for q in lesson_questions([bank[source_id]],teach_words=True) if q['id']==formula_id+'-NAMED-ALL')
    text=challenge(named)['promptInputChallenge']['prompt']['body']['taggedTextElement']['text']
    assert json.loads(base64.b64decode(text.split('duoaero-gap:')[1]))==expected
plan = json.loads((root/'app/assets/lesson_plan.json').read_text())
seen = set()
for node in plan:
    for lesson in node['lessons']:
        source = [bank[qid] for qid in lesson['ids']]
        expanded = lesson_questions(source, teach_words=True)
        assert 10 <= len(expanded) <= 20, (lesson['id'], len(expanded))
        ids = [q['id'] for q in expanded]
        assert len(ids) == len(set(ids))
        for i, q in enumerate(expanded):
            if q['type'] != 'formula_blocks':
                continue
            multi = KINDS[q['id']] in MULTI_NAMED
            offset = 1 if multi else 0
            assert i > 1+offset and expanded[i-2-offset]['id'] == q['id']+'-WORDS'
            assert expanded[i-1]['id'] == q['id']+'-NAMED'
            words = expanded[i-2-offset]
            named = expanded[i-1]
            if multi:
                all_named = expanded[i-2]
                assert all_named['id'] == q['id']+'-NAMED-ALL'
                _, answers, _, pieces = MULTI_NAMED[KINDS[q['id']]]
                assert all_named['answer_blocks'] == answers
                assert all_named['inline_latex'] == pieces
            assert words['stem'].count('___') == 1
            assert len(set(words['answer']+words['distractors'])) == 4
            assert words['answer'][0] in words['explanation']
            assert len(named['answer_blocks']) == 1
            assert len(set(named['blocks'])) == 4
            assert named['before_latex']+named['missing_latex']+named['after_latex'] == q['formula_latex']
            seen.add(q['id'])
        actual = session(source, lesson['id'], teach_words=True)['challenges']
        assert [q['id'] for q in actual] == ids
        for q in actual:
            if q['id'] == 'BOOK-V6-01-D1-NAMED-ALL':
                body=q['promptInputChallenge']['prompt']['body']['taggedTextElement']['text']
                marker='duoaero-latex:duoaero-gap:'
                parts=json.loads(base64.b64decode(body[len(marker):]).decode())
                assert parts == ['___',r'duoaero-math:formula:\textstyle =','___',r'duoaero-math:formula:\textstyle \times','___',r'duoaero-math:formula:\textstyle \times','___']
                assert q['promptInputChallenge']['input']['expressionBuildInput']['slotCount'] == 4
            if q['id'] == 'BOOK-V6-01-D1-NAMED':
                body=q['promptInputChallenge']['prompt']['body']['taggedTextElement']['text']
                marker='duoaero-latex:duoaero-gap:'
                parts=json.loads(base64.b64decode(body[len(marker):]).decode())
                assert parts == [r'duoaero-math:formula:\textstyle p=\rho R_a', '___']
            if q['id'] != 'BOOK-V6-01-D1-WORDS':
                continue
            body = q['promptInputChallenge']['prompt']['body']['taggedTextElement']['text']
            marker = 'duoaero-latex:duoaero-gap:'
            assert body.startswith(marker)
            parts = json.loads(base64.b64decode(body[len(marker):]).decode())
            assert r'duoaero-math:rho:\rho' in parts
            assert r'duoaero-math:R-air:R_a' in parts
            assert any(part.startswith('duoaero-math:T:T') for part in parts)
assert seen == set(KINDS), (sorted(seen-set(KINDS)), sorted(set(KINDS)-seen))
# The words must name the physical quantity represented by each symbol, not
# conflate a force with its dimensionless coefficient or an operand with an
# operation. Check both the named equation and the preliminary word exercise.
for q in lesson_questions(list(bank.values()), teach_words=True):
    if q['id'] == 'BOOK-V6-06-D1-NAMED':
        assert q['missing_latex'] == r'C_{D,i}'
        assert q['answer_blocks'] == ['induced drag coefficient']
    if q['id'] == 'BOOK-V6-02-D1-WORDS':
        assert q['answer'] == ['density'] and 'rho' in q['stem']
print(f'PASS: {len(seen)} word and named-equation introductions precede symbolic exercises; Android UI and touch pending.')
