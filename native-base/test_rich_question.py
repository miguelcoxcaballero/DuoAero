"""Validate generated grading against every selection, including empty/multiple."""
import json
import math
from pathlib import Path
import subprocess
from rich_question import choice_blob, content

root = Path(__file__).resolve().parents[1]
bank = json.loads((root / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))
fixtures = []
for question in bank:
    if question['type'] != 'choice' or not question.get('rich_text'):
        continue
    blob = json.loads(choice_blob(question)['challengeBlob'])
    fixtures.append({'id': question['id'], 'code': blob['grading_function'],
                     'answer': question['answer'], 'count': len(question['options'])})
assert len(fixtures) >= 4
isa = next(q for q in bank if q['id'] == 'TA1-0182-F1')
isa_blob = json.loads(choice_blob(isa)['challengeBlob'])
assert r'p_b' in isa_blob['shirt']['value']
assert r'e^{-X}' in isa_blob['shirt']['value']
assert r'\exp' not in isa_blob['shirt']['value']
assert 'p_base' not in isa_blob['shirt']['value']
# The supplied exponential factor is already e^(-X)=0.50; do not
# exponentiate 0.50 again. 20 kPa * 0.50 is 10 kPa.
assert isa['options'][isa['answer']] == '10 kPa'
assert 20 * 0.50 == 10
assert content(isa['rich_text']['explanation'], isa['explanation']) == r'p=20\times0.50=10\,\mathrm{kPa}'
# Independently check the altitude-dependent question against hydrostatic
# balance and the ideal-gas relation at a non-zero altitude.
varying = next(q for q in bank if q['id'] == 'EX-2021-10-28-3a')
assert varying['answer'] == 0
assert all('exp[' not in content(parts, '') for parts in varying['rich_text']['options'])
g, gas_constant, temperature0, k, altitude = 9.81, 287.0, 288.0, 2e-5, 2000.0
pressure = lambda h: math.exp(-g * math.expm1(k*h) / (gas_constant*temperature0*k))
step = .01
derivative = (math.log(pressure(altitude+step))-math.log(pressure(altitude-step)))/(2*step)
assert math.isclose(pressure(0), 1.0)
assert math.isclose(derivative, -g/(gas_constant*temperature0*math.exp(-k*altitude)), rel_tol=1e-8)

from formula_exercises import formula_challenge, prototypes
from course_adapter import challenge
import base64
for gap in (q for q in bank if q['type'] == 'gap'):
    prompt = challenge(gap)['promptInputChallenge']['prompt']
    assert 'Missing word:' not in json.dumps(prompt)
    marker = prompt['body']['taggedTextElement']['text']
    assert marker.startswith('duoaero-latex:duoaero-gap:')
    pieces = json.loads(base64.b64decode(marker.split('duoaero-gap:', 1)[1]))
    assert pieces.count('___') == 1 and pieces.index('___') > 0
for question in prototypes() + [q for q in bank if q['type'] == 'formula_blocks']:
    prompt = formula_challenge(question)['promptInputChallenge']['prompt']
    feedback = prompt['gradingFeedbackSpecification']['staticFeedback']['gradingFeedback']
    assert feedback['taggedTextElement']['text'] == 'duoaero-latex:' + r'\textstyle ' + question['formula_latex']
    assert question['explanation'] not in feedback['taggedTextElement']['text']
script = r'''
const fixtures=JSON.parse(require('fs').readFileSync(0,'utf8'));
let checked=0;
for(const f of fixtures){
  const grade=new Function(f.code+'; return grade;')();
  for(let mask=0; mask<(1<<f.count); mask++){
    const variables={};
    for(let i=0;i<f.count;i++) variables['answer_'+i]={selected:!!(mask&(1<<i))};
    const result=grade(variables);
    if(result.isCorrect !== (mask===(1<<f.answer))) throw Error(f.id+': '+mask);
    if(!result.feedback.value || !result.displayAnswer.value) throw Error('Missing feedback');
    checked++;
  }
}
console.log(checked+' grading combinations passed');
'''
subprocess.run(['node', '-e', script], input=json.dumps(fixtures), text=True, check=True)
assert content([{'latex': r'\frac{L}{D}'}], '') == r'\frac{L}{D}'
try:
    content([{'latex': 'x', 'text': 'y'}], '')
except ValueError:
    pass
else:
    raise AssertionError('Ambiguous rich content accepted')
print('LaTeX preserved; ambiguous content rejected. Rendering still requires device QA.')

from math_notation import parts, symbol
assert symbol('p_base') == r'p_{\mathrm{base}}'
assert symbol('eta_p') == r'\eta_{p}'
assert symbol('m_dot') == r'\dot{m}'
assert symbol('sigma_max') == r'\sigma_{\mathrm{max}}'
assert symbol('m^-1') == r'm^{-1}'
assert symbol('m²') == r'm^{2}'
assert symbol('exp(-Kh)') == r'e^{-Kh}'
assert symbol('exp(-ln2)') == r'e^{-\ln 2}'
assert parts('Use exp(-Kh).')[1] == {'latex': r'e^{-Kh}'}
assert parts('The mass generally increases.') == [{'text': 'The mass generally increases.'}]
assert parts('Fill ___ with one word.') == [{'text': 'Fill ___ with one word.'}]
assert content(None, 'Use eta_p and m_dot in kg/s².') == r'\text{Use }\eta_{p}\text{ and }\dot{m}\text{ in kg/}s^{2}\text{.}'
print('PASS: explicit subscripts, Greek symbols and powers render as math; prose and word gaps stay literal.')
