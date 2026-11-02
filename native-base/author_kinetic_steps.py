"""Split seven reviewed probe calculations; retain source answers and metadata."""
import json
import math
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'app/assets/questions.json'
text = path.read_text(encoding='utf-8-sig')
bank = json.loads(text)
ids = ['TA1-0156-D2', 'TA1-0164-D2', 'TA1-0195-D2', 'TA1-0327-D2',
       'TA1-0348-D2', 'TA1-0371-D2', 'TA1-0456-D2']
updates = {}
for q in bank:
    if q['id'] not in ids:
        continue
    match = re.search(r'total temperature Tt=(\d+) K at flow speed V=(\d+) m/s', q['stem'])
    assert match, q['id']
    total, speed = map(int, match.groups())
    rise = speed * speed / (2 * 1004.5)
    static = total - rise
    sound = math.sqrt(1.4 * 287 * static)
    mach = speed / sound
    assert abs(mach - float(q['options'][q['answer']])) < 0.000006, q['id']
    def step(suffix, stem, values, unit, formula, prerequisite):
        options = [f'{value:.2f}{unit}' for value in values]
        assert len(set(options)) == 4
        return dict(id=q['id'] + suffix, stem=stem, options=options, answer=0,
                    explanation=options[0], formula_hint={'latex':formula, 'prerequisite':prerequisite})
    q['lesson_steps'] = [
        step('-S1', f'A probe slows air from {speed} m/s. With specific heat 1004.5 J/(kg K), what is the temperature rise?',
             [rise, rise*2, rise/2, rise+10], ' K', r'\Delta T=\frac{V^2}{2c_p}', 'TA1-0107-D2-F1'),
        step('-S2', f'Total temperature is {total} K and the temperature rise is {rise:.2f} K. What is static temperature?',
             [static, total+rise, total, rise], ' K', r'T=T_t-\Delta T', 'TA1-0107-D2-F2'),
        step('-S3', f'Static temperature is {static:.2f} K. For gamma = 1.4 and R = 287 J/(kg K), what is sound speed?',
             [sound, sound*2, sound/2, sound+50], ' m/s', r'a^2=\gamma RT', 'TA1-0107-D2-F3'),
        dict(id=q['id'], stem=f'Flow speed is {speed} m/s and sound speed is {sound:.2f} m/s. What is the Mach number?',
             options=list(q['options']), answer=q['answer'], explanation=f'M = {speed} / {sound:.2f} ≈ {mach:.5f}.',
             formula_hint={'latex':r'M=\frac{V}{a}', 'prerequisite':'TA1-0107-D2-F4'})]
    updates[q['id']] = q
assert set(updates) == set(ids)
decoder = json.JSONDecoder()
offset = text.index('[') + 1
edits = []
while True:
    while text[offset] in ' \t\r\n,': offset += 1
    if text[offset] == ']': break
    old, end = decoder.raw_decode(text, offset)
    if old['id'] in updates:
        edits.append((offset, end, json.dumps(updates[old['id']], ensure_ascii=False, indent=2).replace('\n', '\n  ')))
    offset = end
assert len(edits) == len(ids)
for start, end, replacement in reversed(edits):
    text = text[:start] + replacement + text[end:]
path.write_text(text, encoding='utf-8')
print('Authored 28 checked kinetic-heating steps for seven source questions.')
