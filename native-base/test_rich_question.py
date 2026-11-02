"""Validate generated grading against every selection, including empty/multiple."""
import json
import math
import re
from pathlib import Path
import subprocess
from rich_question import choice_blob, content
from math_notation import parts as notation_parts

assert notation_parts('At V0, g0 and rho1') == [
    {'text': 'At '}, {'latex': r'V_{0}'}, {'text': ', '}, {'latex': r'g_{0}'},
    {'text': ' and '}, {'latex': r'\rho_{1}'}]
assert notation_parts('p0 and T0 at RE') == [
    {'latex': r'p_{0}'}, {'text': ' and '}, {'latex': r'T_{0}'},
    {'text': ' at '}, {'latex': r'R_{E}'}]
assert notation_parts('M=1 at V = 190 m/s') == [
    {'latex': 'M=1'}, {'text': ' at '}, {'latex': 'V=190'}, {'text': ' m/s'}]
assert notation_parts('g0=9.80665 and E=7e+10 Pa') == [
    {'latex': 'g_{0}=9.80665'}, {'text': ' and '}, {'latex': r'E=7\times 10^{10}'}, {'text': ' Pa'}]
assert notation_parts('Tt=280 K, cp=1004.5 J/(kg K), gamma=1.4') == [
    {'latex': 'T_{t}=280'}, {'text': ' K, '}, {'latex': 'c_{p}=1004.5'},
    {'text': ' J/(kg K), '}, {'latex': r'\gamma=1.4'}]
assert notation_parts('2.2e+06 m at ce=1.4e-05') == [
    {'latex': r'2.2\times 10^{6}'}, {'text': ' m at '}, {'latex': r'c_{e}=1.4\times 10^{-5}'}]
assert notation_parts('409.8 mm²') == [{'text': '409.8 '}, {'latex': r'\mathrm{mm}^{2}'}]
assert notation_parts('mi/mf') == [{'latex': r'\textstyle \frac{m_{i}}{m_{f}}'}]
assert notation_parts('4 MN/m and 30 kN/m') == [{'text': '4 MN/m and 30 kN/m'}]
assert notation_parts('Require TAS>=1.3Vs and M<=0.75.') == [
    {'text': 'Require '}, {'latex': r'\mathrm{TAS}\geq 1.3V_s'},
    {'text': ' and '}, {'latex': r'M\leq 0.75'}, {'text': '.'}]
assert notation_parts('Vapp>=1.3 Vs; Vs<=71') == [
    {'latex': r'V_{\mathrm{app}}\geq 1.3V_s'}, {'text': '; '}, {'latex': r'V_s\leq 71'}]
assert notation_parts('Use Vapp=1.3Vs and CLmax=1.75.') == [
    {'text': 'Use '}, {'latex': r'V_{\mathrm{app}}=1.3V_s'}, {'text': ' and '},
    {'latex': r'C_{L,\max}=1.75'}, {'text': '.'}]
assert notation_parts('Approach Vapp and stall speed Vs.') == [
    {'text': 'Approach '}, {'latex': r'V_{\mathrm{app}}'},
    {'text': ' and stall speed '}, {'latex': r'V_s'}, {'text': '.'}]
assert notation_parts('The camera is fine') == [{'text': 'The camera is fine'}]
assert notation_parts('Vstall=sqrt(2W/(rho S CLmax))') == [
    {'latex':r'V_{\mathrm{stall}}=\sqrt{\frac{2W}{\rho\,S\,C_{L,\max}}}'}]
assert notation_parts('CL=sqrt(CD0/k)') == [
    {'latex':r'C_{L}=\sqrt{\frac{C_{D0}}{k}}'}]
assert notation_parts('R1=sqrt(T2/T1)') == [
    {'latex':r'R_{1}=\sqrt{\frac{T_{2}}{T_{1}}}'}]
assert notation_parts('Vs=sqrt(2W/(rho S CLmax))') == [
    {'latex':r'V_s=\sqrt{\frac{2W}{\rho\,S\,C_{L,\max}}}'}]
assert notation_parts('sqrt(V²+2Pjet/m_dot)') == [
    {'latex':r'\sqrt{V^2+\frac{2P_{\mathrm{jet}}}{\dot{m}}}'}]
assert notation_parts('Apply sqrt(2) at fixed load.') == [
    {'text':'Apply '}, {'latex':r'\sqrt{2}'}, {'text':' at fixed load.'}]
assert notation_parts('sqrt(1/sqrt(CL))') == [
    {'latex':r'\sqrt{\frac{1}{\sqrt{C_{L}}}}'}]
assert notation_parts('1/sqrt(CLmax)') == [
    {'latex':r'\textstyle \frac{1}{\sqrt{C_{L,\max}}}'}]
assert notation_parts('280/sqrt(2) = 198 km/h') == [
    {'latex':r'\textstyle \frac{280}{\sqrt{2}}'}, {'text':' = 198 km/h'}]
assert notation_parts('weight/sqrt(2)') == [
    {'text':'weight/'}, {'latex':r'\sqrt{2}'}]
assert notation_parts('sqrt(weight)') == [{'text':'sqrt(weight)'}]
assert notation_parts('sqrt(m/s)') == [{'text':'sqrt(m/s)'}]
assert notation_parts('2W/(rho S CL_opt) = 6400 m²/s²') == [
    {'latex':r'\textstyle \frac{2W}{\rho\,S\,C_{L,\mathrm{opt}}}'},
    {'text':' = 6400 '}, {'latex':r'm^{2}'}, {'text':'/'}, {'latex':r's^{2}'}]
assert not any('latex' in p for p in notation_parts('k=1/(pi e AR)')) or not any(
    p.get('latex') == 'k=1' for p in notation_parts('k=1/(pi e AR)'))

root = Path(__file__).resolve().parents[1]
bank = json.loads((root / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))
dynamic_pressure = next(q for q in bank if q['id'] == 'TA1-0063-F1')
assert dynamic_pressure['formula_hint'] == {
    'latex': r'q=\frac12\rho V^2', 'prerequisite': 'BOOK-V6-02-D1'}
assert dynamic_pressure['options'][dynamic_pressure['answer']] == '5 kPa'
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
from course_adapter import lesson_questions, session
import base64
for gap in (q for q in bank if q['type'] == 'gap'):
    prompt = challenge(gap)['promptInputChallenge']['prompt']
    assert 'Missing word:' not in json.dumps(prompt)
    marker = prompt['body']['taggedTextElement']['text']
    assert marker.startswith('duoaero-latex:duoaero-gap:')
    pieces = json.loads(base64.b64decode(marker.split('duoaero-gap:', 1)[1]))
    assert pieces.count('___') == 1 and pieces.index('___') > 0
pressure_problem = next(q for q in bank if q['id'] == 'TA1-0397-D2')
steps = lesson_questions([pressure_problem])
assert [q['id'] for q in steps] == ['ISA-PRESSURE-RATIO','TA1-0397-D2-S1', 'TA1-0397-D2']
assert [q['id'] for q in lesson_questions([pressure_problem], expand_steps=False)] == ['TA1-0397-D2']
assert [c['id'] for c in session([pressure_problem], 'lesson')['challenges']] == [q['id'] for q in steps]
assert all(len(q['stem']) < 160 for q in steps)
assert steps[1]['options'][steps[1]['answer']] == '19.33 kPa'
assert steps[2]['options'][steps[2]['answer']] == '0.584'
assert math.isclose(22.63 * .854, 19.33, abs_tol=.005)
assert math.isclose(19.33 / 33.09, .584, abs_tol=.001)
mach_problem = next(q for q in bank if q['id'] == 'TA1-0107-D2')
mach_expanded = lesson_questions([mach_problem])
assert [q['type'] for q in mach_expanded] == ['formula_blocks', 'choice'] * 4
for formula, exercise in zip(mach_expanded[::2], mach_expanded[1::2]):
    assert exercise['formula_hint']['prerequisite'] == formula['id']
mach_steps = [q for q in mach_expanded if q['type'] == 'choice']
assert [q['id'] for q in mach_steps] == ['TA1-0107-D2-S1', 'TA1-0107-D2-S2', 'TA1-0107-D2-S3', 'TA1-0107-D2']
assert all(len(q['stem']) < 160 for q in mach_steps)
rise = 190**2 / (2 * 1004.5)
static_temperature = 280 - rise
sound_speed = math.sqrt(1.4 * 287 * static_temperature)
assert math.isclose(rise, 17.97, abs_tol=.005)
assert math.isclose(static_temperature, 262.03, abs_tol=.005)
assert math.isclose(sound_speed, 324.47, abs_tol=.005)
assert math.isclose(190 / sound_speed, .58556, abs_tol=.000005)
assert [q['options'][q['answer']] for q in mach_steps] == ['17.97 K', '262.03 K', '324.47 m/s', '0.58556']
plan = json.loads((Path(__file__).resolve().parents[1]/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
mach_lesson = next(lesson for node in plan for lesson in node['lessons'] if mach_problem['id'] in lesson['ids'])
bank_by_id = {q['id']: q for q in bank}
lesson_bank = [bank_by_id[qid] for qid in mach_lesson['ids']]
legacy = session(lesson_bank, mach_lesson['id'], expand_steps=False)
updated = session(lesson_bank, mach_lesson['id'])
assert len(updated['challenges']) <= 20
assert {q['id'] for q in legacy['challenges']} <= {q['id'] for q in updated['challenges']}
assert mach_lesson['id'] == legacy['id'] == updated['id']
breguet_problem = next(q for q in bank if q['id'] == 'TA1-0078-D2')
breguet_steps = lesson_questions([breguet_problem])
assert [q['type'] for q in breguet_steps] == ['formula_blocks', 'choice'] * 2
for formula, exercise in zip(breguet_steps[::2], breguet_steps[1::2]):
    assert exercise['formula_hint']['prerequisite'] == formula['id']
    assert 'formula_hint' not in formula
exponent = 2.2e6 * 9.81 * 1.4e-5 / (210 * 14)
remaining = math.exp(-exponent)
assert math.isclose(exponent, .10277, abs_tol=.000005)
assert math.isclose(remaining, .90233, abs_tol=.000005)
assert math.isclose(53000 * (1-remaining), 5176.3, abs_tol=.1)
breguet_lesson = next(lesson for node in plan for lesson in node['lessons'] if breguet_problem['id'] in lesson['ids'])
breguet_bank = [bank_by_id[qid] for qid in breguet_lesson['ids']]
old = session(breguet_bank, breguet_lesson['id'], expand_steps=False)
new = session(breguet_bank, breguet_lesson['id'])
assert len(new['challenges']) <= 20 and old['id'] == new['id']
assert {q['id'] for q in old['challenges']} <= {q['id'] for q in new['challenges']}
breguet_pattern = re.compile(r'^An ideal jet cruise without wind starts at mass (\d+) kg and must cover ([\deE.+-]+) m at V=([\d.]+) m/s, L/D=([\d.]+), ce=([\deE.+-]+) kg/\(N s\) and g=([\d.]+) m/s²\.')
reviewed_breguet = [q for q in bank if q.get('lesson_steps') and breguet_pattern.match(q['stem'])]
assert len(reviewed_breguet) == 7
for original in reviewed_breguet:
    mass, distance, speed, efficiency, consumption, gravity = map(float, breguet_pattern.match(original['stem']).groups())
    x = distance * gravity * consumption / (speed * efficiency)
    fuel = mass * (1 - math.exp(-x))
    calculations = [q for q in lesson_questions([original]) if q['type'] == 'choice']
    assert len(calculations) == 2
    assert math.isclose(float(calculations[0]['options'][calculations[0]['answer']]), x, abs_tol=.000005)
    assert math.isclose(float(calculations[1]['options'][calculations[1]['answer']].split()[0]), fuel, abs_tol=.1)
for question in prototypes() + [q for q in bank if q['type'] == 'formula_blocks'] + mach_expanded[::2] + breguet_steps[::2]:
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
for source, expected in [
    ('p/(R T)', r'\textstyle \frac{p}{R\,T}'),
    ('p/(RT)', r'\textstyle \frac{p}{RT}'),
    ('rho2/rho1', r'\textstyle \frac{\rho_{2}}{\rho_{1}}'),
    ('m_dot/(rho V)', r'\textstyle \frac{\dot{m}}{\rho\,V}'),
    ('L/D', r'\textstyle \frac{L}{D}'),
    ('EI/(KL)²', r'\textstyle \frac{EI}{(KL)^{2}}'),
    ('B/V²', r'\textstyle \frac{B}{V^{2}}'),
]:
    assert parts(source) == [{'latex': expected}], (source, parts(source))
for units in ('m/s', 'kg/s', 'J/(kg K)', 'km/h'):
    assert parts(units) == [{'text': units}], (units, parts(units))
assert parts('Use lift/drag comparisons.') == [{'text': 'Use lift/drag comparisons.'}]
assert symbol('pi²') == r'\pi^{2}'
assert symbol('CL²') == r'C_{L}^{2}'
assert symbol('CD^2') == r'C_{D}^{2}'
assert parts('CD = CD0 + k CL²') == [{'latex': r'C_D=C_{D0}+kC_L^2'}]
assert parts('CD=CD0+CL²/(pi e AR)') == [{'latex': r'C_D=C_{D0}+\frac{C_L^2}{\pi e\,AR}'}]
assert parts('The CD=CD0+kCL² model applies.')[0] == {'text': 'The '}
reported = next(q for q in bank if q['id'] == 'TA1-0148')
shirt = json.loads(choice_blob(reported)['challengeBlob'])['shirt']['value']
assert r'\frac{p}{R\,T}' in shirt and 'p/(R T)' not in shirt
assert reported['options'][reported['answer']] == 'Density'
assert 'hint' not in json.loads(choice_blob(reported)['challengeBlob'])
hint = json.loads(choice_blob(reported, include_formula_hint=True)['challengeBlob'])['hint']
from course_adapter import challenge as native_challenge
assert json.loads(native_challenge(reported)['challengeBlob'])['hint'] == hint
assert hint['explanation']['value'] == r'p=\rho R_aT'
plan = json.loads((root / 'app/assets/lesson_plan.json').read_text())
course_order = [qid for node in plan for lesson in node['lessons'] for qid in lesson['ids']]
assert course_order.index(reported['formula_hint']['prerequisite']) < course_order.index(reported['id'])
gravity = next(q for q in bank if q['id'] == 'TH-2026-OTHER-1')
gravity_blob = json.loads(choice_blob(gravity)['challengeBlob'])
assert gravity['answer'] == 0
assert all(r'\frac' in choice['child']['value'] for choice in gravity_blob['pants'])
assert gravity['rich_text']['options'][0][0]['latex'] == r'g=g_0\left(\frac{R_E}{R_E+h}\right)^2'
# At positive altitude, the inverse-square law decreases; each displayed
# distractor gives a different value and must remain incorrect.
earth, altitude = 6371.0, 100.0
ratio = earth / (earth + altitude)
assert 0 < ratio ** 3 < ratio ** 2 < ratio < 1 < (1 / ratio) ** 2
print('PASS: explicit subscripts, Greek symbols and powers render as math; prose and word gaps stay literal.')
