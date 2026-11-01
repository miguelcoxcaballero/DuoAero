"""Conservative mathematical notation in legacy mixed prose.

Only explicit symbolic notation is converted. Ordinary prose and ambiguous
unmarked identifiers stay literal; authored rich_text takes precedence.
"""
import re

GREEK = {'rho': r'\rho', 'eta': r'\eta', 'alpha': r'\alpha',
         'beta': r'\beta', 'gamma': r'\gamma', 'sigma': r'\sigma',
         'lambda': r'\lambda', 'pi': r'\pi', 'delta': r'\Delta'}
SUPERSCRIPTS = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺', '0123456789-+')
# Avoid treating English words as products of individual letters. These
# matches require notation that is unambiguous in the source question bank.
TOKEN = re.compile(
    r'(?<![A-Za-z0-9_])(?:'
    r'exp\([A-Za-z0-9+*./-]+\)'
    r'|[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+'
    r'|(?:rho|eta|alpha|beta|gamma|sigma|lambda|pi|delta)'
    r'|[A-Za-z]+\^(?:[+-]?\d+(?:\.\d+)?)'
    r'|(?:\d+(?:\.\d+)?|[A-Za-z]+)[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+'
    r')(?![A-Za-z0-9_])'
)


def symbol(value):
    if value.startswith('exp(') and value.endswith(')'):
        exponent = re.sub(r'\bln(?=\d)', r'\\ln ', value[4:-1])
        return 'e^{' + exponent + '}'
    if value == 'm_dot':
        return r'\dot{m}'
    if value == 'delta_alpha':
        return r'\Delta\alpha'
    if '_' in value:
        base, subscript = value.split('_', 1)
        base = GREEK.get(base, base)
        # Multi-character labels are a single subscript, never just the first
        # character as in raw `p_base`. Keep mathematical one-letter indices.
        label = subscript if len(subscript) == 1 else r'\mathrm{' + subscript.replace('_', r'\,') + '}'
        return base + '_{' + label + '}'
    if '^' in value:
        base, exponent = value.split('^', 1)
        return base + '^{' + exponent + '}'
    match = re.fullmatch(r'(.+?)([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)', value)
    if match:
        return match[1] + '^{' + match[2].translate(SUPERSCRIPTS) + '}'
    return GREEK.get(value, value)


def parts(value):
    result, offset = [], 0
    for match in TOKEN.finditer(value):
        if match.start() > offset:
            result.append({'text': value[offset:match.start()]})
        result.append({'latex': symbol(match[0])})
        offset = match.end()
    if offset < len(value):
        result.append({'text': value[offset:]})
    return result or [{'text': value}]
