"""Check staged spar arithmetic, formula ordering and migration inputs."""
import json
import re
from decimal import Decimal
from pathlib import Path
from course_adapter import lesson_questions, session

root = Path(__file__).resolve().parents[1]
bank = {q['id']: q for q in json.loads((root/'app/assets/questions.json').read_text())}
ids = ['TA1-0737-D3', 'TA1-0774-D3', 'TA1-0836-D3', 'TA1-0950-D3']
pattern = re.compile(r'length ([0-9.]+) m under transverse tip force ([0-9.]+) N\. E=([0-9.]+) GPa, total section height h=([0-9.]+) m, allowable stress=([0-9.]+) MPa and allowable deflection=([0-9.]+) m')
names = ('SPAR-MOMENT-FORMULA', 'SPAR-STRESS-FORMULA', 'SPAR-DEFLECTION-FORMULA')
first = lesson_questions([bank[ids[0]]], teach_words=True)
assert len(first) == 17 and first[0]['type'] == 'matching' and len(first[0]['pairs']) == 4
for name in names:
    positions = [next(i for i,q in enumerate(first) if q['id'] == name + suffix)
                 for suffix in ('-WORDS', '-NAMED-ALL', '-NAMED', '')]
    assert positions == sorted(positions)
    assert first[positions[1]]['inline_latex'].count('___') == len(first[positions[1]]['answer_blocks'])
assert next(q for q in first if q['id']=='SPAR-STRESS-FORMULA-NAMED-ALL')['answer_blocks'] == ['inertia','moment','distance','stress']
assert next(q for q in first if q['id']=='SPAR-DEFLECTION-FORMULA-NAMED-ALL')['answer_blocks'] == ['inertia','force','length cubed','Young modulus','deflection']
assert max(i for i,q in enumerate(first) if q['id'] in names) < next(i for i,q in enumerate(first) if q['id'].endswith('-M'))
for qid in ids:
    original = bank[qid]
    match = pattern.search(original['stem']); assert match, qid
    length, force, young, height, stress, deflection = map(Decimal, match.groups())
    expected = [force*length, (force*length*height/2)/stress,
                force*length**3/(3*young*deflection*1000)]
    parts = lesson_questions([original])[-4:]
    for part, value, prerequisite in zip(parts[:3], expected, names):
        assert part['formula_hint']['prerequisite'] == prerequisite
        got = Decimal(re.match(r'[0-9.]+', part['options'][part['answer']]).group())
        assert abs(got-value) < Decimal('0.00011'), (qid, part['id'], got, value)
        assert len(set(part['options'])) == 4 and len(part['stem']) < 160
    answer = Decimal(re.match(r'[0-9.]+', parts[-1]['options'][parts[-1]['answer']]).group())
    assert abs(answer-max(expected[1:])) < Decimal('0.0006'), qid
    assert len(parts[-1]['stem']) < 160
    for part in parts[1:]:
        rich = part['rich_text']
        assert any('latex' in segment for segment in rich['stem'])
        assert len(rich['options']) == len(part['options'])
        assert all(r'10^{-6}' in option[0]['latex'] for option in rich['options'])
    session([original], qid, teach_words=True)
print('PASS: four staged spar problems and three word-first formulas; Android UI unverified.')
