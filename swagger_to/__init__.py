"""Parse Swagger specification and generates server and client stubs."""
import re
import string
from typing import List, MutableMapping, Tuple

import collections
import icontract

# pylint: disable=missing-docstring

LOCAL_DEFINITION_REF_RE = re.compile(r'^#/definitions/(?P<name>[a-zA-Z0-9_.\- ]+)$')
NAME_RE = re.compile(r'^[a-zA-Z0-9_.\- ]+$')


@icontract.require(
    lambda ref: LOCAL_DEFINITION_REF_RE.match(ref),
    'swagger-to can handle only definitions local to the spec file. '
    'Please create an issue if you need to handle a different kind of '
    'definition reference: https://github.com/Parquery/swagger-to/issues/new',
    error=ValueError,
    enabled=True)
@icontract.ensure(lambda result: NAME_RE.match(result))
def parse_definition_ref(ref: str) -> str:
    """
    Parse a reference to a definition and return the definition name.

    >>> parse_definition_ref('#/definitions/Some-Type')
    'Some-Type'
    """
    mtch = LOCAL_DEFINITION_REF_RE.match(ref)
    assert mtch is not None
    return mtch.group('name')


LOCAL_PARAMETER_REF_RE = re.compile(r'^#/parameters/(?P<name>[a-zA-Z0-9_.\- ]+)$')


@icontract.require(
    lambda ref: LOCAL_PARAMETER_REF_RE.match(ref),
    'swagger-to can handle only parameters local to the spec file. '
    'Please create an issue if you need to handle a different kind of '
    'parameter reference: https://github.com/Parquery/swagger-to/issues/new',
    error=ValueError,
    enabled=True)
@icontract.ensure(lambda result: NAME_RE.match(result))
def parse_parameter_ref(ref: str) -> str:
    """
    Parse a reference to a parameter and return the parameter name.

    >>> parse_parameter_ref('#/parameters/some-parameter')
    'some-parameter'
    """
    mtch = LOCAL_PARAMETER_REF_RE.match(ref)
    assert mtch is not None
    return mtch.group('name')


# Abbreviations to be treated specially in snake_case and camelCase conversions
SPECIALS = ['URLs', 'IDs', 'URL', 'ID', 'HTTP', 'HTTPS', 'JSONLD', 'JSON']


def camel_case_split(identifier: str) -> List[str]:
    """
    Split the identifier given in camel case into parts.

    >>> camel_case_split(identifier='CamelCase')
    ['Camel', 'Case']

    >>> camel_case_split(identifier='CamelURLs')
    ['Camel', 'URLs']

    >>> camel_case_split(identifier='JSONLDObject')
    ['JSONLD', 'Object']
    """
    if identifier == '':
        raise ValueError("Unexpected empty identifier")

    cur = 0

    parts = []  # type: List[str]
    while cur < len(identifier):
        found_special = False
        for special in SPECIALS:
            if identifier[cur:cur + len(special)] == special:
                parts.append(special)
                cur += len(special)
                found_special = True

        if not found_special:
            if identifier[cur] in string.ascii_uppercase:
                parts.append('')
                parts[-1] += identifier[cur]
                cur += 1
            else:
                if len(parts) == 0:
                    parts.append('')

                parts[-1] += identifier[cur]
                cur += 1

    return parts


_NONLETTER_PREFIX_RE = re.compile(r'^[^a-zA-Z]+')
_NONLETTER_SUFFIX_RE = re.compile(r'[^a-zA-Z]+$')


def _trim_nonletters(identifier: str) -> Tuple[str, str, str]:
    """
    Trim the non-letter prefix and suffix from the identifier.

    >>> _trim_nonletters('_1some_text23_')
    ('_1', 'some_text', '23_')

    >>> _trim_nonletters('_1some_text')
    ('_1', 'some_text', '')

    >>> _trim_nonletters('some_text23_')
    ('', 'some_text', '23_')

    >>> _trim_nonletters('')
    ('', '', '')

    :param identifier: to be converted
    :return: lowercase snake_case identifier
    """
    if not identifier:
        return '', identifier, ''

    prefix = ''
    prefix_mtch = _NONLETTER_PREFIX_RE.search(identifier)
    if prefix_mtch:
        prefix = prefix_mtch.group(0)

    suffix = ''
    suffix_mtch = _NONLETTER_SUFFIX_RE.search(identifier)
    if suffix_mtch:
        suffix = suffix_mtch.group(0)

    trimmed = identifier[len(prefix):len(identifier) - len(suffix)]

    return prefix, trimmed, suffix


@icontract.require(
    lambda identifier: identifier != '', error=lambda: ValueError("Unexpected empty identifier"), enabled=True)
@icontract.ensure(lambda result: '-' not in result)
@icontract.ensure(lambda result: result[0] == result[0].upper())
@icontract.ensure(lambda result: result != '')
def capital_camel_case(identifier: str) -> str:
    """
    Translate an arbitrary identifier to a CamelCase.

    >>> capital_camel_case(identifier='camelCase')
    'CamelCase'

    >>> capital_camel_case(identifier='snake_case')
    'SnakeCase'

    >>> capital_camel_case(identifier='Dash-Case')
    'DashCase'

    >>> capital_camel_case(identifier='dash-case')
    'DashCase'

    >>> capital_camel_case(identifier='_snake_case')
    '_SnakeCase'

    >>> capital_camel_case(identifier='snake_case_')
    'SnakeCase_'

    >>> capital_camel_case(identifier='__')
    '__'

    :param identifier: arbitrary identifier
    :return: identifier as CamelCase
    """
    prefix, trimmed, suffix = _trim_nonletters(identifier=identifier)

    if not trimmed:
        return identifier

    # yapf: disable
    parts = [
        part
        for underscore_part in trimmed.split("_")
        for dash_part in underscore_part.split("-")
        for part in camel_case_split(identifier=dash_part)
    ]
    # yapf: enable

    new_parts = []  # type: List[str]
    for part in parts:
        part = part.lower()

        if part in ['url', 'id']:
            new_parts.append(part.upper())
        elif part == 'urls':
            new_parts.append('URLs')
        elif part == 'ids':
            new_parts.append('IDs')
        else:
            new_parts.append(part[0].upper() + part[1:].lower())

    return "".join([prefix] + new_parts + [suffix])


@icontract.require(
    lambda identifier: identifier != '', error=lambda: ValueError("Unexpected empty identifier"), enabled=True)
@icontract.ensure(lambda result: '-' not in result)
@icontract.ensure(lambda result: result[0] == result[0].lower())
@icontract.ensure(lambda result: result != '')
def camel_case(identifier: str) -> str:
    """
    Translate an arbitrary identifier to a camelCase.

    >>> camel_case(identifier='CamelCase')
    'camelCase'

    >>> camel_case(identifier='snake_case')
    'snakeCase'

    >>> camel_case(identifier='Snake_case')
    'snakeCase'

    >>> camel_case(identifier='Dash-Case')
    'dashCase'

    >>> camel_case(identifier='dash-case')
    'dashCase'

    >>> camel_case(identifier='_snake_case')
    '_snakeCase'

    >>> camel_case(identifier='snake_case_')
    'snakeCase_'

    >>> camel_case(identifier='__')
    '__'

    :param identifier: arbitrary identifier
    :return: identifier as camelCase
    """
    prefix, trimmed, suffix = _trim_nonletters(identifier=identifier)

    if not trimmed:
        return identifier

    # yapf: disable
    parts = [
        part
        for underscore_part in trimmed.split("_")
        for dash_part in underscore_part.split("-")
        for part in camel_case_split(identifier=dash_part)
    ]
    # yapf: enable

    new_parts = [parts[0].lower()]  # type: List[str]

    for part in parts[1:]:
        part = part.lower()

        if part in ['url', 'id']:
            new_parts.append(part.upper())
        elif part == 'urls':
            new_parts.append('URLs')
        elif part == 'ids':
            new_parts.append('IDs')
        else:
            new_parts.append(part[0].upper() + part[1:].lower())

    return "".join([prefix] + new_parts + [suffix])


@icontract.require(
    lambda identifier: identifier != '', error=lambda: ValueError("Unexpected empty identifier"), enabled=True)
@icontract.ensure(lambda result: '-' not in result)
@icontract.ensure(lambda result: result == result.lower())
def snake_case(identifier: str) -> str:
    """
    Convert an identifier to a lowercase snake case.

    >>> snake_case(identifier='CamelCase')
    'camel_case'

    >>> snake_case(identifier='camelCase')
    'camel_case'

    >>> snake_case(identifier='snake_case')
    'snake_case'

    >>> snake_case(identifier='Snake_case')
    'snake_case'

    >>> snake_case(identifier='Dash-Case')
    'dash_case'

    >>> snake_case(identifier='dash-case')
    'dash_case'

    >>> snake_case(identifier='_CamelCase')
    '_camel_case'

    >>> snake_case(identifier='CamelCase_')
    'camel_case_'

    >>> snake_case(identifier='__')
    '__'

    :param identifier: to be converted
    :return: lowercase snake_case identifier
    """
    prefix = ''
    prefix_mtch = _NONLETTER_PREFIX_RE.search(identifier)
    if prefix_mtch:
        prefix = prefix_mtch.group(0)

    suffix = ''
    suffix_mtch = _NONLETTER_SUFFIX_RE.search(identifier)
    if suffix_mtch:
        suffix = suffix_mtch.group(0)

    trimmed = identifier[len(prefix):len(identifier) - len(suffix)]

    if not trimmed:
        return identifier

    # yapf: disable
    parts = [
        part
        for underscore_part in trimmed.split("_")
        for dash_part in underscore_part.split("-")
        for part in camel_case_split(identifier=dash_part)
    ]
    # yapf: enable

    result = '_'.join(parts)
    return ''.join([prefix, result.lower(), suffix])


def upper_first(text: str) -> str:
    """
    Capitalizes the first letter of the text.

    >>> upper_first(text='some text')
    'Some text'

    >>> upper_first(text='Some text')
    'Some text'

    >>> upper_first(text='')
    ''

    >>> upper_first(text='_some text')
    '_some text'

    :param text: to be capitalized
    :return: text with the first letter capitalized
    """
    if len(text) == 0:
        return ''

    return text[0].upper() + text[1:]


class TokenizedPath:
    """Represent a tokenization of a Swagger path to an endpoint."""

    def __init__(self):
        """Initialize with defaults."""
        self.tokens = []  # type: List[str]
        self.parameter_to_token_indices = collections.OrderedDict()  # type: MutableMapping[str, List[int]]
        self.token_index_to_parameter = collections.OrderedDict()  # type: MutableMapping[int, str]


PATH_TOKENIZATION_RE = re.compile(r'\{(?P<name>[a-zA-Z0-9_]*)\}|[^{]+|.')


def tokenize_path(path: str) -> TokenizedPath:
    """
    Tokenize the path coming from a Swagger spec to a dictionary such that you can modify the path parameters easily.

    :param path: original path
    :return: tokenized path with the dictionary
    """
    token_pth = TokenizedPath()

    for mtch in PATH_TOKENIZATION_RE.finditer(path):
        token_pth.tokens.append(mtch.group(0))

        if mtch.group("name") is not None:
            name = mtch.group("name")
            if name not in token_pth.parameter_to_token_indices:
                token_pth.parameter_to_token_indices[name] = []

            token_pth.parameter_to_token_indices[name].append(len(token_pth.tokens) - 1)
            token_pth.token_index_to_parameter[len(token_pth.tokens) - 1] = name

    return token_pth
