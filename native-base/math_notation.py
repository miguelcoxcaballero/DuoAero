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
FRACTION = re.compile(r'(?<![A-Za-z0-9_,/])((?:\d+(?:\.\d+)?[A-Za-z][A-Za-z0-9_]*|' + _NAME + r'))\s*/\s*(\([A-Za-z0-9_ .+*×−-]{1,60}\)|' + _NAME + r')(' + _POWER + r')?(?![A-Za-z0-9_/])')
_UNITS = {'m','km','mm','cm','s','h','kg','g','N','kN','MN','J','W','kW','Pa','kPa','MPa','GPa','K','L','rad','Hz'}
_SYMBOL_NAMES = {'rho','eta','alpha','beta','gamma','sigma','lambda','pi','delta','mu','ce','cl','cd','isp','mi','mf'}
_BODY = re.compile(r'[A-Za-z][A-Za-z0-9_]*|\d+(?:\.\d+)?|\s+|[^A-Za-z0-9_\s]+')
# Avoid treating English words as products of individual letters. These
# matches require notation that is unambiguous in the source question bank.
TOKEN = re.compile(
    r'(?<![A-Za-z0-9_])(?:'
    r'(?:TAS|Vapp|Vs|Pcrit|[A-Z])\s*(?:>=|<=)\s*(?:\d+(?:\.\d+)?|\.\d+)(?:\s*Vs)?(?![A-Za-z0-9_]|\.\d)'
    r'|(?:Vapp|Vstall|Vs|Vmd|CLmax|CLopt|Pjet)\s*=\s*[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:\s*(?:Vapp|Vstall|Vs|Vmd))?(?![A-Za-z0-9_]|\.\d)'
    r'|(?:rho[012]?|gamma|cp|ce|CL0|CD0|CL|CD|mi|mf|Tt|[A-Za-z](?:[012]|_[A-Za-z0-9]+)?)\s*=\s*[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?(?![A-Za-z0-9_./*^])'
    r'|(?:\d+(?:\.\d+)?|\.\d+)[eE][+-]?\d+(?![A-Za-z0-9_.])'
    r'|exp\([A-Za-z0-9+*./-]+\)'
    r'|(?:Vapp|Vstall|Vs|Vmd|CLmax|CLopt|Pjet|CL0|CD0|CL|CD)(?![\^⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺])'
    r'|(?:p|T|g|V|rho)[012]'
    r'|RE'
    r'|[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+'
    r'|[A-Za-z]+\^(?:[+-]?\d+(?:\.\d+)?)'
    r'|(?:\d+(?:\.\d+)?|[A-Za-z]+)[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+'
    r'|(?:rho|eta|alpha|beta|gamma|sigma|lambda|pi|delta|mu)'
    r')(?![A-Za-z0-9_])'
)


def symbol(value):
    aliases = {'CL_opt':r'C_{L,\mathrm{opt}}','CL_max':r'C_{L,\max}',
               'CLmax':r'C_{L,\max}','CLopt':r'C_{L,\mathrm{opt}}',
               'Vapp':r'V_{\mathrm{app}}','Vstall':r'V_{\mathrm{stall}}',
               'Vs':r'V_s','Vmd':r'V_{\mathrm{md}}','Pjet':r'P_{\mathrm{jet}}',
               'CD0':r'C_{D0}','CL0':r'C_{L0}'}
    if value in aliases:
        return aliases[value]
    aliased_assignment = re.fullmatch(r'(Vapp|Vstall|Vs|Vmd|CLmax|CLopt|Pjet)\s*=\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+))(?:\s*(Vapp|Vstall|Vs|Vmd))?', value)
    if aliased_assignment:
        return aliases[aliased_assignment.group(1)] + '=' + aliased_assignment.group(2) + (aliases[aliased_assignment.group(3)] if aliased_assignment.group(3) else '')
    inequality = re.fullmatch(r'(TAS|Vapp|Vs|Pcrit|[A-Z])\s*(>=|<=)\s*((?:\d+(?:\.\d+)?|\.\d+))(?:\s*(Vs))?', value)
    if inequality:
        names = {'TAS': r'\mathrm{TAS}', 'Vapp': r'V_{\mathrm{app}}',
                 'Vs': r'V_s', 'Pcrit': r'P_{\mathrm{crit}}'}
        lhs = names.get(inequality.group(1), inequality.group(1))
        op = r'\geq ' if inequality.group(2) == '>=' else r'\leq '
        return lhs + op + inequality.group(3) + (r'V_s' if inequality.group(4) else '')
    assignment = re.fullmatch(r'(rho[012]?|gamma|cp|ce|CL0|CD0|CL|CD|mi|mf|Tt|[A-Za-z](?:[012]|_[A-Za-z0-9]+)?)\s*=\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?)', value)
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
    if value in ('cp', 'ce', 'CL', 'CD', 'mi', 'mf', 'Tt'):
        return value[0] + '_{' + value[1] + '}'
    scientific = re.fullmatch(r'((?:\d+(?:\.\d+)?|\.\d+))[eE]([+-]?\d+)', value)
    if scientific:
        return scientific.group(1) + r'\times 10^{' + str(int(scientific.group(2))) + '}'
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
        return symbol(base) + '^{' + exponent + '}'
    match = re.fullmatch(r'(.+?)([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)', value)
    if match:
        base = (r'\mathrm{' + match[1] + '}') if len(match[1]) > 1 and match[1] in _UNITS else symbol(match[1])
        return base + '^{' + match[2].translate(SUPERSCRIPTS) + '}'
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


def _parts_without_roots(value):
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


def _closing_parenthesis(value, start):
    """Return the closing parenthesis paired with start, or None."""
    depth = 0
    for index in range(start, len(value)):
        if value[index] == '(':
            depth += 1
        elif value[index] == ')':
            depth -= 1
            if depth == 0:
                return index
            if depth < 0:
                return None
    return None


_ROOT_NAME = re.compile(r'\bsqrt\s*\(')
_ROOT_BODY = re.compile(r'[A-Za-z0-9_\s.+*/()^−+\-⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+')
_ROOT_SYMBOLS = {
    'CLmax':r'C_{L,\max}', 'CLopt':r'C_{L,\mathrm{opt}}',
    'CL_max':r'C_{L,\max}', 'CL_opt':r'C_{L,\mathrm{opt}}',
    'CD0':r'C_{D0}', 'CL0':r'C_{L0}',
    'Vstall':r'V_{\mathrm{stall}}', 'Vmd':r'V_{\mathrm{md}}', 'Vs':r'V_s',
    'Pjet':r'P_{\mathrm{jet}}',
}
_ROOT_ASSIGNMENT = re.compile(r'(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9_]{0,20})\s*=\s*$')
_ROOT_DENOMINATOR = re.compile(r'(?<![A-Za-z0-9_./])((?:\d+(?:\.\d+)?|[A-Za-z][A-Za-z0-9_]*))\s*/\s*$')


def _root_symbol(value):
    if value in _ROOT_SYMBOLS:
        return _ROOT_SYMBOLS[value]
    indexed = re.fullmatch(r'([A-Za-z])(\d+)', value)
    if indexed:
        return symbol(indexed.group(1)) + '_{' + indexed.group(2) + '}'
    return symbol(value)


def _root_body(value):
    """Render a reviewed-looking arithmetic body, including a true fraction.

    Only expressions with symbolic names, numbers and mathematical operators
    are accepted. In particular, do not convert prose or physical unit paths
    merely because they happen to appear near a square-root token.
    """
    value = value.strip()
    if not value or not _ROOT_BODY.fullmatch(value):
        return None
    names = re.findall(_NAME, value)
    if any(not _symbolic(name) and name != 'sqrt' for name in names):
        return None
    if names and value[0].isalpha() and all(name in _UNITS for name in names):
        return None
    # Preserve parentheses that are part of a larger expression, but remove a
    # pair that encloses the entire fraction operand.
    if value.startswith('(') and _closing_parenthesis(value, 0) == len(value)-1:
        return _root_body(value[1:-1])
    nested = _ROOT_NAME.match(value)
    if nested and _closing_parenthesis(value, nested.end()-1) == len(value)-1:
        inner = _root_body(value[nested.end():-1])
        return None if inner is None else r'\sqrt{' + inner + '}'
    depth = 0
    divisions, sums = [], []
    for index, char in enumerate(value):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth < 0:
                return None
        elif char == '/' and depth == 0:
            divisions.append(index)
        elif char in '+-−' and depth == 0:
            previous = value[:index].rstrip()
            # A leading sign, an exponent sign or scientific-notation sign
            # is unary; all other top-level signs split the additive terms.
            if previous and previous[-1] not in '+-−*/(^':
                scientific = previous[-1] in 'eE' and len(previous)>1 and previous[-2].isdigit()
                if not scientific:
                    sums.append(index)
    if depth:
        return None
    if sums:
        pieces, start = [], 0
        for at in sums:
            term = _root_body(value[start:at])
            if term is None:
                return None
            pieces.extend((term, '-' if value[at]=='−' else value[at]))
            start = at+1
        term = _root_body(value[start:])
        return None if term is None else ''.join(pieces)+term
    if len(divisions) == 1:
        at = divisions[0]
        numerator, denominator = _root_body(value[:at]), _root_body(value[at+1:])
        if numerator is None or denominator is None:
            return None
        return r'\frac{' + numerator + '}{' + denominator + '}'
    if divisions:
        # Several unparenthesized divisions are ambiguous; leave them alone.
        return None
    if 'sqrt' in names:
        return None
    if '/' in value:
        # A division hidden inside a larger parenthesized expression needs a
        # fuller parser; do not produce an incomplete typeset representation.
        return None
    output = []
    for match in _BODY.finditer(value):
        token = match.group()
        if token.isspace():
            output.append(r'\,')
        elif token[0].isalpha():
            output.append(_root_symbol(token))
        else:
            output.append(token.replace('×',r'\times ').replace('−','-').replace('*',r'\cdot ')
                          .replace('²','^2').replace('³','^3'))
    return ''.join(output)


def _general_parts(value):
    """Format unambiguous roots before processing ordinary fractions."""
    result, offset = [], 0
    for match in _ROOT_NAME.finditer(value):
        if match.start() < offset:
            continue
        open_at = value.find('(', match.start(), match.end())
        close_at = _closing_parenthesis(value, open_at)
        if close_at is None:
            continue
        body = _root_body(value[open_at+1:close_at])
        if body is None:
            continue
        prefix = value[offset:match.start()]
        # In 1/sqrt(CL) or 280/sqrt(2), the radical is the denominator of
        # the fraction, not a separate square root following a literal slash.
        fraction = _ROOT_DENOMINATOR.search(prefix)
        numerator = fraction.group(1) if fraction else None
        if numerator and (numerator[0].isdigit() or (_symbolic(numerator) and numerator not in _UNITS)):
            before = prefix[:fraction.start()]
            if before:
                result.extend(_parts_without_roots(before))
            result.append({'latex': r'\textstyle \frac{' + _root_symbol(numerator) + r'}{\sqrt{' + body + '}}'})
            offset = close_at + 1
            continue
        assignment = _ROOT_ASSIGNMENT.search(prefix)
        lhs = assignment.group(1) if assignment else None
        if lhs and _symbolic(lhs) and lhs not in _UNITS:
            before = prefix[:assignment.start()]
            if before:
                result.extend(_parts_without_roots(before))
            rendered = _root_symbol(lhs) + '='
        else:
            if prefix:
                result.extend(_parts_without_roots(prefix))
            rendered = ''
        result.append({'latex': rendered + r'\sqrt{' + body + '}'})
        offset = close_at + 1
    if offset < len(value):
        result.extend(_parts_without_roots(value[offset:]))
    return result or [{'text': value}]


# Two exact drag-polar forms recur throughout the reviewed question bank.
# Keep each complete equation together instead of rendering its terms as
# disconnected pieces of prose. The matcher is deliberately narrow.
_POLAR = re.compile(r"(?<![A-Za-z0-9_])CD\s*=\s*CD0\s*\+\s*(?:k\s*CL(?:²|\^2)|CL(?:²|\^2)\s*/\s*\(\s*pi\s+e\s+AR\s*\))(?![A-Za-z0-9_])")
_ISA_EXP = re.compile(r'(?<![A-Za-z0-9_])p\s*=\s*p11\s+exp\[-g\(h-11000\)/\(RT\)\]')
def parts(value):
    result, offset = [], 0
    for match in sorted([*_POLAR.finditer(value), *_ISA_EXP.finditer(value)], key=lambda m: m.start()):
        if match.start() < offset:
            continue
        if match.start() > offset:
            result.extend(_general_parts(value[offset:match.start()]))
        if match.re is _ISA_EXP:
            latex = r'p=p_{11}e^{-\frac{g(h-11000)}{RT}}'
        elif re.search(r"/\s*\(", match.group()):
            latex = r"C_D=C_{D0}+\frac{C_L^2}{\pi e\,AR}"
        else:
            latex = r"C_D=C_{D0}+kC_L^2"
        result.append({'latex': latex})
        offset = match.end()
    if offset < len(value):
        result.extend(_general_parts(value[offset:]))
    return result or _general_parts(value)
