"""Parse Swagger specification and generates server and client stubs."""
import collections
import re
import string
from typing import List, MutableMapping

import icontract

# pylint: disable=missing-docstring

VARIABLE_RE = re.compile(r'^[a-zA-Z0-9_]+$')


@icontract.ensure(lambda result: VARIABLE_RE.match(result))
def parse_definition_ref(ref: str) -> str:
    """Parse a reference to a definition and return the definition name."""
    prefix = '#/definitions/'
    if not ref.startswith(prefix):
        raise ValueError("Expected a ref with prefix {!r}, but got: {!r}".format(prefix, ref))

    return ref[len(prefix):]


@icontract.ensure(lambda result: VARIABLE_RE.match(result))
def parse_parameter_ref(ref: str) -> str:
    """Parse a reference to a parameter and return the parameter name."""
    prefix = '#/parameters/'
    if not ref.startswith(prefix):
        raise ValueError("Expected a ref with prefix {!r}, but got: {!r}".format(prefix, ref))

    return ref[len(prefix):]


# Abbreviations to be treated specially in snake_case and camelCase conversions
SPECIALS = ['URLs', 'IDs', 'URL', 'ID', 'HTTP', 'HTTPS']


def camel_case_split(identifier: str) -> List[str]:
    """
    Split the identifier given in camel case into parts.

    >>> camel_case_split(identifier='CamelCase')
    ['Camel', 'Case']

    >>> camel_case_split(identifier='CamelURLs')
    ['Camel', 'URLs']
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


def capital_camel_case(identifier: str) -> str:
    """
    Translate an arbitrary identifier to a CamelCase.

    >>> capital_camel_case(identifier='camelCase')
    'CamelCase'

    >>> capital_camel_case(identifier='snake_case')
    'SnakeCase'

    :param identifier: arbitrary identifier
    :return: identifier as CamelCase
    """
    if identifier == '':
        raise ValueError("Unexpected empty identifier")

    parts = identifier.split("_")

    camel_parts = []  # type: List[str]
    for part in parts:
        camel_parts.extend(camel_case_split(identifier=part))

    new_parts = []  # type: List[str]
    for part in camel_parts:
        part = part.lower()

        if part in ['url', 'id']:
            new_parts.append(part.upper())
        elif part == 'urls':
            new_parts.append('URLs')
        elif part == 'ids':
            new_parts.append('IDs')
        else:
            new_parts.append(part[0].upper() + part[1:].lower())

    return "".join(new_parts)


def camel_case(identifier: str) -> str:
    """
    Translate an arbitrary identifier to a camelCase.

    >>> camel_case(identifier='CamelCase')
    'camelCase'

    >>> camel_case(identifier='snake_case')
    'snakeCase'

    >>> camel_case(identifier='Snake_case')
    'snakeCase'

    :param identifier: arbitrary identifier
    :return: identifier as camelCase
    """
    if identifier == '':
        raise ValueError("Unexpected empty identifier")

    parts = identifier.split("_")

    camel_parts = []  # type: List[str]
    for part in parts:
        camel_parts.extend(camel_case_split(identifier=part))

    new_parts = [camel_parts[0].lower()]  # type: List[str]

    for part in camel_parts[1:]:
        part = part.lower()

        if part in ['url', 'id']:
            new_parts.append(part.upper())
        elif part == 'urls':
            new_parts.append('URLs')
        elif part == 'ids':
            new_parts.append('IDs')
        else:
            new_parts.append(part[0].upper() + part[1:].lower())

    return "".join(new_parts)


def snake_case(identifier: str) -> str:
    """
    Convert an indentifier to a lowercase snake case.

    >>> snake_case(identifier='CamelCase')
    'camel_case'

    >>> snake_case(identifier='camelCase')
    'camel_case'

    >>> snake_case(identifier='snake_case')
    'snake_case'

    >>> snake_case(identifier='Snake_case')
    'snake_case'

    :param identifier: to be converted
    :return: lowercase snake_case identifier
    """
    if identifier == '':
        return ''

    parts = camel_case_split(identifier=identifier)

    result = '_'.join(parts)
    return result.lower()


def upper_first(text: str) -> str:
    """
    Capitalizes the first letter of the text.

    >>> upper_first(text='some text')
    'Some text'

    >>> upper_first(text='Some text')
    'Some text'

    >>> upper_first(text='')
    ''

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
