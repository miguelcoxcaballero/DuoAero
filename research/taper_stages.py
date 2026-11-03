"""Arithmetic draft for the reviewed taper family; never connected to course.

The original expressions must first be taught as word, named-quantity and
symbol exercises. Formula hints, lesson partitioning, migration and native
interaction are intentionally not claimed by this arithmetic scaffold.
"""
import math
from taper_domain import PATTERN
from jet_family_steps import number_latex


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
        question = {'id': source['id']+'-'+name, 'type': 'choice',
                    'stem': f'{label} Calculate {left:.10g} {symbol} {right:.10g}.',
                    'rich_text': {'stem': [{'text': label+' Calculate '},
                        {'latex': number_latex(left)+{'+':'+','-':'-','×':r'\times','÷':r'\div'}[symbol]+number_latex(right)},
                        {'text': '.'}]}, 'expected': value}
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
    return questions, lower, upper
