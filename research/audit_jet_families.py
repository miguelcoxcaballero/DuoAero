"""Independently check two practice families before sequencing their lessons.

This is a read-only audit, not an authoring pass or an Android acceptance test.
"""
import json
import math
import re
from pathlib import Path

BANK = Path(__file__).resolve().parents[1] / 'app/assets/questions.json'
NUM = r'([0-9.eE+-]+)'
RANGE = re.compile(r'An ideal jet has OEM=' + NUM + r' kg, payload=' + NUM +
    r' kg, MTOM=' + NUM + r' kg and fuel capacity=' + NUM +
    r' kg\. It burns ' + NUM + r' kg before cruise and must retain ' + NUM +
    r' kg after cruise\. With V=' + NUM + r' m/s, E=' + NUM +
    r', ce=' + NUM + r' kg/\(N s\) and g=' + NUM)
PAYLOAD = re.compile(r'An ideal jet has OEM=' + NUM + r' kg, MTOM=' + NUM +
    r' kg, maximum landing mass=' + NUM + r' kg, maximum payload=' + NUM +
    r' kg and fuel capacity=' + NUM + r' kg\. It must finish with reserve ' + NUM +
    r' kg and cover ' + NUM + r' m at V=' + NUM + r' m/s, E=' + NUM +
    r', ce=' + NUM + r' kg/\(N s\), g=' + NUM)


def audit(question):
    stem = question.get('stem', '')
    m = RANGE.match(stem)
    if m:
        empty, payload, mtom, tank, burn, reserve, speed, efficiency, ce, gravity = map(float, m.groups())
        dry = empty + payload
        takeoff = min(mtom, dry + tank)
        initial, final = takeoff - burn, dry + reserve
        assert initial > final > 0 and burn >= 0 and tank >= burn + reserve
        result = speed * efficiency / (gravity * ce) * math.log(initial / final) / 1000
        return 'range', result, (dry, dry + tank, takeoff, initial, final, initial / final)
    m = PAYLOAD.match(stem)
    if m:
        empty, mtom, landing, structural, tank, reserve, distance, speed, efficiency, ce, gravity = map(float, m.groups())
        k = math.exp(distance * gravity * ce / (speed * efficiency))
        assert k > 1 and tank >= reserve
        limits = (structural, mtom / k - empty - reserve,
                  landing - empty - reserve, (tank - k * reserve) / (k - 1) - empty)
        assert min(limits) >= 0
        return 'payload', min(limits), (k, *limits)
    return None


def main():
    bank = json.loads(BANK.read_text(encoding='utf-8-sig'))
    found = {'range': [], 'payload': []}
    for q in bank:
        result = audit(q)
        if result is None:
            continue
        family, expected, intermediates = result
        values = [float(re.match(NUM, option).group(1)) for option in q['options']]
        distances = [abs(value - expected) for value in values]
        assert math.isfinite(expected) and all(math.isfinite(x) for x in intermediates)
        assert distances.count(min(distances)) == 1 and distances.index(min(distances)) == q['answer'], q['id']
        found[family].append(q['id'])
    assert all(len(ids) == 10 for ids in found.values()), found
    for family, ids in found.items():
        print(f'{family}: {len(ids)} checked: {", ".join(ids)}')
    print('Original choices agree with independent calculation; steps and Android integration remain pending.')

if __name__ == '__main__':
    main()
