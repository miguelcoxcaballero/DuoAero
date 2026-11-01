"""Replace selected generated practice with sourced V6 content, preserving exams.

Run once against the pre-V6 bank. The manifest records each retired practice ID.
No original exam, reflection, or reviewed question may be replaced.
"""
import collections
import json
import math
from pathlib import Path
from textbook_content import formula_questions, systems_questions

ROOT = Path(__file__).resolve().parents[1]


def integrate(bank, nodes):
    if any(q['id'].startswith('BOOK-V6-') for q in bank):
        raise ValueError('V6 content is already integrated; do not replace another batch')
    before = {q['id']: q for q in bank}
    protected = {q['id'] for q in bank if q['origin']['kind'] != 'practice' or q.get('editorial_review') or q.get('rich_text')}
    # Retain the independently verified first native diagnostic session inputs.
    fixture = ROOT / 'native-base/tests/fixtures/aerospace_lesson.json'
    protected.update(c['id'] for c in json.loads(fixture.read_text())['challenges'])
    node_for = {qid: node for node in nodes for qid in node['ids']}
    manifest = []
    authored = formula_questions() + systems_questions()
    systems = {'id': '2.6-systems-point-0', 'topic': '2.6',
               'name': 'Aircraft systems: energy, control and instruments', 'ids': [], 'lessons': []}
    nodes.append(systems)
    for question in authored:
        targets = [n for n in nodes if n['topic'] == question['topic'] and
                   (question['topic'] == '2.6' or question['node_hint'].lower() in n['name'].lower())]
        if not targets:
            raise ValueError(f"No appropriate named node for {question['id']}")
        candidates = [q for q in bank if q['id'] not in protected and q['type'] == 'choice'
                      and q['origin']['kind'] == 'practice' and q['difficulty'] == question['difficulty']
                      and (question['topic'] == '2.6' or q['topic'] == question['topic'])
                      and len(node_for[q['id']]['ids']) > 15]
        # Prefer a replacement already in the intended node; otherwise take a
        # generated item from a larger node in the same topic. Systems receives
        # capacity from large existing practice nodes, not exam/reflection items.
        candidates.sort(key=lambda q: (node_for[q['id']] not in targets,
                                       -len(node_for[q['id']]['ids']), q['id']))
        if not candidates:
            raise ValueError(f"No safe practice replacement for {question['id']}")
        old = candidates[0]
        source_node = node_for[old['id']]
        destination = source_node if source_node in targets else min(targets, key=lambda n: len(n['ids']))
        if source_node is destination:
            destination['ids'][destination['ids'].index(old['id'])] = question['id']
        else:
            source_node['ids'].remove(old['id'])
            destination['ids'].append(question['id'])
        clean = {k: v for k, v in question.items() if k != 'node_hint'}
        bank[bank.index(old)] = clean
        protected.add(clean['id'])
        node_for[clean['id']] = destination
        manifest.append({'new_id': clean['id'], 'retired_practice_id': old['id'],
                         'difficulty': clean['difficulty'], 'node_id': destination['id']})
    for node in nodes:
        ids = node['ids']
        count = math.ceil(len(ids) / 20)
        if not 1 <= count <= 3 or len(ids) // count < 10:
            raise ValueError(f"Cannot preserve lesson bounds in {node['id']}")
        sizes = [len(ids) // count + (i < len(ids) % count) for i in range(count)]
        node['name'] = node['name'].replace(' — ', ': ')
        node['lessons'] = []
        start = 0
        for i, size in enumerate(sizes):
            node['lessons'].append({'id': f"{node['id']}-lesson-{i}", 'ids': ids[start:start+size],
                                    'name': f"{node['name']} · Lesson {i+1}"})
            start += size
    after = {q['id']: q for q in bank}
    assert len(bank) == len(after) == 1200
    assert collections.Counter(q['difficulty'] for q in bank) == {1: 400, 2: 400, 3: 400}
    assert all(after[key] == q for key, q in before.items() if q['origin']['kind'] in ('exam', 'reflection'))
    assert len([q for q in bank if q['topic'] == '2.6']) == 24
    return bank, nodes, manifest


if __name__ == '__main__':
    bank = json.loads((ROOT/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
    nodes = json.loads((ROOT/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
    bank, nodes, manifest = integrate(bank, nodes)
    for relative, content in [('app/assets/questions.json', bank), ('app/assets/lesson_plan.json', nodes),
                              ('web/bank_en_final.json', bank), ('web/lesson_plan.json', nodes),
                              ('native-base/textbook-integration.json', manifest)]:
        (ROOT/relative).write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Integrated {len(manifest)} textbook questions; {len(nodes)} nodes, '
          f'{sum(len(n["lessons"]) for n in nodes)} lessons. Runtime acceptance is separate.')
