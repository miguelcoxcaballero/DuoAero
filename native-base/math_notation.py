"""Conservative mathematical notation in legacy mixed prose.

Only explicit symbolic notation is converted. Ordinary prose and ambiguous
unmarked identifiers stay literal; authored rich_text takes precedence.
"""
import re

GREEK = {'rho': r'\rho', 'eta': r'\eta', 'alpha': r'\alpha',
         'beta': r'\beta', 'gamma': r'\gamma', 'sigma': r'\sigma',
         'lambda': r'\lambda', 'pi': r'\pi', 'delta': r'\Delta', 'mu': r'\mu'}
SUPERSCRIPTS = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺', '0123456789-+')
# Recognise simple symbolic ratios as a unit, before the individual symbols.
# Keep physical unit expressions such as m/s and J/(kg K) as ordinary text.
_NAME = r'[A-Za-z][A-Za-z0-9_]*'
_POWER = r'(?:\^[+-]?\d+(?:\.\d+)?|[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)'
FRACTION = re.compile(r'(?<![A-Za-z0-9_,/])(' + _NAME + r')\s*/\s*(\([A-Za-z0-9_ .+*×−-]{1,60}\)|' + _NAME + r')(' + _POWER + r')?(?![A-Za-z0-9_/])')
_UNITS = {'m','km','mm','cm','s','h','kg','g','N','kN','J','W','kW','Pa','kPa','MPa','GPa','K','L','rad','Hz'}
_SYMBOL_NAMES = {'rho','eta','alpha','beta','gamma','sigma','lambda','pi','delta','mu','ce','cl','cd','isp'}
_BODY = re.compile(r'[A-Za-z][A-Za-z0-9_]*|\d+(?:\.\d+)?|\s+|[^A-Za-z0-9_\s]+')
# Avoid treating English words as products of individual letters. These
# matches require notation that is unambiguous in the source question bank.
TOKEN = re.compile(
    r'(?<![A-Za-z0-9_])(?:'
    r'(?:rho[012]?|[A-Za-z](?:[012]|_[A-Za-z0-9]+)?)\s*=\s*[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?(?![A-Za-z0-9_./*^])'
    r'|exp\([A-Za-z0-9+*./-]+\)'
    r'|(?:p|T|g|V|rho)[012]'
    r'|RE'
    r'|[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+'
    r'|[A-Za-z]+\^(?:[+-]?\d+(?:\.\d+)?)'
    r'|(?:\d+(?:\.\d+)?|[A-Za-z]+)[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+'
    r'|(?:rho|eta|alpha|beta|gamma|sigma|lambda|pi|delta|mu)'
    r')(?![A-Za-z0-9_])'
)


def symbol(value):
    assignment = re.fullmatch(r'(rho[012]?|[A-Za-z](?:[012]|_[A-Za-z0-9]+)?)\s*=\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?)', value)
    if assignment:
        rhs = assignment.group(2)
        scientific = re.fullmatch(r'(.+)[eE]([+-]?\d+)', rhs)
        if scientific:
            rhs = scientific.group(1) + r'\times 10^{' + str(int(scientific.group(2))) + '}'
        return symbol(assignment.group(1)) + '=' + rhs
    numeric = re.fullmatch(r'(rho|p|T|g|V)([012])', value)
    if numeric:
        return GREEK.get(numeric.group(1), numeric.group(1)) + '_{' + numeric.group(2) + '}'
    if value == 'RE':
        return r'R_{E}'
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
        return GREEK.get(match[1], match[1]) + '^{' + match[2].translate(SUPERSCRIPTS) + '}'
    return GREEK.get(value, value)


def _ordinary_parts(value):
    result, offset = [], 0
    for match in TOKEN.finditer(value):
        if match.start() > offset:
            result.append({'text': value[offset:match.start()]})
        result.append({'latex': symbol(match[0])})
        offset = match.end()
    if offset < len(value):
        result.append({'text': value[offset:]})
    return result or [{'text': value}]


def _symbolic(name):
    return len(name) == 1 or any(c.isupper() or c.isdigit() or c == '_' for c in name) or name.casefold() in _SYMBOL_NAMES


def _math_body(value):
    result = []
    for match in _BODY.finditer(value):
        token = match.group()
        if token.isspace(): result.append(r'\,')
        elif token[0].isalpha():
            indexed = re.fullmatch(r'([A-Za-z]+)(\d+)', token)
            result.append(symbol(indexed.group(1)) + '_{' + indexed.group(2) + '}' if indexed else symbol(token))
        else: result.append(token.replace('×', r'\times ').replace('−', '-').replace('*', r'\cdot '))
    return ''.join(result)


def parts(value):
    result, offset = [], 0
    for match in FRACTION.finditer(value):
        numerator, denominator, exponent = match.group(1), match.group(2), match.group(3)
        inner = denominator[1:-1] if denominator.startswith('(') else denominator
        names = re.findall(_NAME, inner)
        if not names or not _symbolic(numerator) or not all(_symbolic(name) for name in names):
            continue
        if numerator in _UNITS and all(name in _UNITS for name in names):
            continue
        if match.start() > offset: result.extend(_ordinary_parts(value[offset:match.start()]))
        rendered = _math_body(inner)
        if exponent:
            power = exponent[1:] if exponent.startswith('^') else exponent.translate(SUPERSCRIPTS)
            rendered = ('(' + rendered + ')' if denominator.startswith('(') else rendered) + '^{' + power + '}'
        result.append({'latex': r'\textstyle \frac{' + _math_body(numerator) + '}{' + rendered + '}'})
        offset = match.end()
    if offset < len(value): result.extend(_ordinary_parts(value[offset:]))
    return result or [{'text': value}]
