"""Arithmetic draft for the reviewed taper family; never connected to course.

The original expressions must first be taught as word, named-quantity and
symbol exercises. Formula hints, lesson partitioning, migration and native
interaction are intentionally not claimed by this arithmetic scaffold.
"""
import math
import hashlib
from taper_domain import PATTERN
from jet_family_steps import number_latex

FORMULA_BY_STEP = {
    **dict.fromkeys(('VCR2','RHOV2','Q'), 'TAPER-Q'),
    **dict.fromkeys(('VS2','RVS2','STALLDEN','TWOW','SMIN'), 'TAPER-SMIN'),
    **dict.fromkeys(('B2','QPI','QE','QB2','W2','DI'), 'TAPER-DI'),
    **dict.fromkeys(('REMAINING','QCD','SMAX'), 'TAPER-SMAX'),
    **dict.fromkeys(('BCR','TWO-SMIN','LOWRATIO','LOW','TWO-SMAX','UPRATIO','UP'), 'TAPER-BOUND'),
    'WIDTH': 'TAPER-WIDTH',
}


def draft(source):
    match = PATTERN.match(source['stem'])
    if match is None:
        raise ValueError('Not the reviewed taper family')
    b, root, weight, rho, vs, cl, drag, speed, efficiency, cd0 = map(float, match.groups())
    questions = []

    def operation(name, label, left, symbol, right):
        left, right = float(f'{left:.10g}'), float(f'{right:.10g}')
        value = {'+': lambda: left + right, '-': lambda: left - right,
                 '×': lambda: left * right, '÷': lambda: left / right}[symbol]()
        question_id = source['id']+'-'+name
        delta = max(abs(value)*.1, 1e-12)
        options = [f'{x:.10g}' for x in (value, value+delta, value-delta, value+2*delta)]
        if len(set(options)) != 4:
            raise ValueError('Arithmetic options are not distinct')
        shift = int.from_bytes(hashlib.sha256(question_id.encode()).digest()[:2], 'big') % 4
        if shift:
            options = options[-shift:] + options[:-shift]
        question = {'id': question_id, 'type': 'choice', 'difficulty': 1,
                    'stem': f'{label} Calculate {left:.10g} {symbol} {right:.10g}.',
                    'rich_text': {'stem': [{'text': label+' Calculate '},
                        {'latex': number_latex(left)+{'+':'+','-':'-','×':r'\times','÷':r'\div'}[symbol]+number_latex(right)},
                        {'text': '.'}]}, 'options': options, 'answer': shift,
                    'explanation': f'{value:.10g}', 'expected': value,
                    'draft_formula_prerequisite': FORMULA_BY_STEP.get(name)}
        questions.append(question)
        return value

    q = operation('VCR2', 'Cruise speed squared:', speed, '×', speed)
    q = operation('RHOV2', 'Density times cruise speed squared:', rho, '×', q)
    q = operation('Q', 'Cruise dynamic pressure:', q, '÷', 2)
    stall = operation('VS2', 'Stall speed squared:', vs, '×', vs)
    stall = operation('RVS2', 'Density times stall speed squared:', rho, '×', stall)
    stall = operation('STALLDEN', 'Multiply by maximum lift coefficient:', stall, '×', cl)
    twice_weight = operation('TWOW', 'Twice the weight:', 2, '×', weight)
    min_area = operation('SMIN', 'Minimum wing area:', twice_weight, '÷', stall)
    span2 = operation('B2', 'Wingspan squared:', b, '×', b)
    induced_den = operation('QPI', 'Dynamic pressure times pi:', q, '×', math.pi)
    induced_den = operation('QE', 'Multiply by span efficiency:', induced_den, '×', efficiency)
    induced_den = operation('QB2', 'Multiply by wingspan squared:', induced_den, '×', span2)
    weight2 = operation('W2', 'Weight squared:', weight, '×', weight)
    induced = operation('DI', 'Induced drag:', weight2, '÷', induced_den)
    residual = operation('REMAINING', 'Drag limit less induced drag:', drag, '-', induced)
    qcd = operation('QCD', 'Dynamic pressure times zero-lift drag coefficient:', q, '×', cd0)
    max_area = operation('SMAX', 'Maximum wing area:', residual, '÷', qcd)
    geometry = operation('BCR', 'Wingspan times root chord:', b, '×', root)
    x = operation('TWO-SMIN', 'Twice the minimum wing area:', 2, '×', min_area)
    x = operation('LOWRATIO', 'Divide by wingspan times root chord:', x, '÷', geometry)
    lower = operation('LOW', 'Subtract one for the lower taper bound:', x, '-', 1)
    y = operation('TWO-SMAX', 'Twice the maximum wing area:', 2, '×', max_area)
    y = operation('UPRATIO', 'Divide by wingspan times root chord:', y, '÷', geometry)
    upper = operation('UP', 'Subtract one for the upper taper bound:', y, '-', 1)
    physical_lower = max(0.0, lower)
    lower_choice = float(f'{physical_lower:.10g}')
    questions.append({
        'id': source['id']+'-DOMAIN-LOWER', 'type': 'choice', 'difficulty': 1,
        'stem': f'The algebraic lower bound is {lower:.10g}. Which lower bound also satisfies a nonnegative taper ratio?',
        'options': ['0', f'{lower:.10g}', 'Use the upper bound', 'There is no lower bound'],
        'answer': 0 if lower < 0 else 1,
        'explanation': 'Use the greater of the algebraic lower bound and zero.',
    })
    feasible = upper >= lower_choice
    decision = {
        'id': source['id']+'-DOMAIN', 'type': 'choice', 'difficulty': 1,
        'stem': f'The physical lower bound is {lower_choice:.10g} and the upper bound is {upper:.10g}. Is there a feasible interval?',
        'options': ['A feasible interval exists', 'No feasible interval exists',
                    'Only negative taper ratios are allowed', 'The lower bound does not matter'],
        'answer': 0 if feasible else 1,
        'explanation': 'A feasible interval exists when its upper bound is at least its lower bound.',
    }
    questions.append(decision)
    if feasible:
        operation('WIDTH', 'Subtract the physical lower bound from the upper bound:', upper, '-', lower_choice)
    final = dict(source)
    final['stem'] = (f'The physical lower bound is {lower_choice:.10g} and the upper bound is {upper:.10g}. '
                     'Choose the interval width, or no feasible taper ratio.')
    final.pop('rich_text', None)
    questions.append(final)
    return questions, lower, upper
