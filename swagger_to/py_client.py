#!/usr/bin/env python3
"""Generate a Python client from Swagger specification."""

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches
# pylint: disable=too-many-statements,too-many-lines

import collections
import re
from typing import MutableMapping, Union, List, Optional, Dict, Mapping  # pylint: disable=unused-import

import icontract
import jinja2
import jinja2.exceptions

import swagger_to
import swagger_to.intermediate
import swagger_to.swagger


class Typedef:
    """Represent a type definition in Python."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.description = ''
        self.identifier = ''

    def __str__(self) -> str:
        """Represent the type definition as its class name and the identifier."""
        return '{}({})'.format(self.__class__.__name__, self.identifier)


class Booldef(Typedef):
    """Represent a Python boolean."""

    pass


class Intdef(Typedef):
    """Represent a Python integer."""

    pass


class Floatdef(Typedef):
    """Represent a Python floating-point number."""

    pass


class Strdef(Typedef):
    """Represent a Python string."""

    pass


class Bytesdef(Typedef):
    """Represent a Python immutable bytes object."""

    pass


class Filedef(Typedef):
    """Represents a Python file type in form-data parameters."""

    pass


class Anydef(Typedef):
    """Represent a definition of Python Any object."""

    pass


class Attribute:
    """Represent an instance attribute of a Python class."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.typedef = None  # type: Optional[Typedef]
        self.description = ''
        self.name = ''
        self.required = False

        self.classdef = None  # type: Optional[Classdef]


class Classdef(Typedef):
    """Represent a definition of a Python class."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        super().__init__()
        self.attributes = collections.OrderedDict()  # type: MutableMapping[str, Attribute]


class Listdef(Typedef):
    """Represent a definition of a Python list."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        super().__init__()

        self.items = None  # type: Union[None, Typedef]


class Dictdef(Typedef):
    """Represent a definition of a Python dictionary."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        super().__init__()

        self.values = None  # type: Union[None, Typedef]


class Parameter:
    """Represent a parameter of a request in Python."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        # Original parameter name
        self.name = ''

        # Parameter identifier in the code
        self.identifier = ''

        self.in_what = ''
        self.typedef = None  # type: Optional[Typedef]
        self.required = False
        self.description = None  # type: Optional[str]


class Response:
    """Represent a response from the server in Python."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.code = ''
        self.typedef = None  # type: Optional[Typedef]
        self.description = ''


class Request:
    """Represent a request function of the client in Python."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.operation_id = ''
        self.path = ''
        self.method = ''
        self.description = ''

        # the union of all parameters
        self.parameters = []  # type: List[Parameter]

        # parameters split into categories
        self.body_parameter = None  # type: Optional[Parameter]
        self.header_parameters = []  # type: List[Parameter]
        self.query_parameters = []  # type: List[Parameter]
        self.path_parameters = []  # type: List[Parameter]
        self.formdata_parameters = []  # type: List[Parameter]
        self.file_parameters = []  # type: List[Parameter]

        self.responses = collections.OrderedDict()  # type: MutableMapping[str, Response]
        self.produces = []  # type: List[str]


def _anonymous_or_get_typedef(intermediate_typedef: swagger_to.intermediate.Typedef,
                              typedefs: Mapping[str, Typedef]) -> Typedef:
    """
    Get the Python representation of the type definition from the table of Python type definitions by its identifier.

    If the type definition has no identifier, it is translated on the spot to the corresponding Python type definition.

    :param intermediate_typedef: intermediate representation of the type definition
    :param typedefs: table of type definitions in Python representation
    :return: type definition in Python representation
    """
    if intermediate_typedef.identifier:
        if intermediate_typedef.identifier not in typedefs:
            raise KeyError('Intermediate typedef not found in the translated typedefs: {!r}'.format(
                intermediate_typedef.identifier))

        return typedefs[intermediate_typedef.identifier]

    typedef = _create_initial_typedef(intermediate_typedef=intermediate_typedef)
    _translate_to_typedef_in_place(intermediate_typedef=intermediate_typedef, typedef=typedef, typedefs=typedefs)

    return typedef


def _properties_to_attributes(intermediate_typedef: swagger_to.intermediate.Objectdef, classdef: Classdef,
                              typedefs: Mapping[str, Typedef]) -> MutableMapping[str, Attribute]:
    """
    Translate the intermediate properties to class attributes of the given ``classdef``.

    :param intermediate_typedef: intermediate representation of the object definition
    :param classdef: class definition for which we construct the attributes
    :param typedefs: type definitions (or their placeholders, if the mapping is in process of construction)
    """
    attributes = collections.OrderedDict()  # type: MutableMapping[str, Attribute]

    for intermediate_prop in intermediate_typedef.properties.values():
        attr = Attribute()
        attr.description = intermediate_prop.description
        attr.name = intermediate_prop.name
        attr.typedef = _anonymous_or_get_typedef(intermediate_typedef=intermediate_prop.typedef, typedefs=typedefs)
        attr.required = intermediate_prop.required
        attr.classdef = classdef

        attributes[attr.name] = attr

    attributes = collections.OrderedDict(sorted(list(attributes.items()), key=lambda kv: not kv[1].required))

    return attributes


def _translate_to_typedef_in_place(intermediate_typedef: swagger_to.intermediate.Typedef, typedef: Typedef,
                                   typedefs: Mapping[str, Typedef]) -> None:
    """
    Translate the type definition in intermediate representation to Python.

    :param intermediate_typedef: type definition in intermediate representation
    :param typedefs: type definitions (or their placeholders if typedefs are in process of construction)
    :return: type definition in Python representation
    """
    if isinstance(intermediate_typedef, swagger_to.intermediate.Primitivedef):
        return

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Arraydef):
        assert isinstance(typedef, Listdef)
        typedef.items = _anonymous_or_get_typedef(intermediate_typedef=intermediate_typedef.items, typedefs=typedefs)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        assert isinstance(typedef, Dictdef)
        typedef.values = _anonymous_or_get_typedef(intermediate_typedef=intermediate_typedef.values, typedefs=typedefs)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.AnyValuedef):
        return

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        assert typedef is not None and isinstance(typedef, Classdef)
        typedef.attributes = _properties_to_attributes(
            intermediate_typedef=intermediate_typedef, classdef=typedef, typedefs=typedefs)
    else:
        raise NotImplementedError('Converting intermediate typedef to Python is not supported: {!r}'.format(
            type(intermediate_typedef)))

    assert typedef is not None


def _create_initial_typedef(intermediate_typedef: swagger_to.intermediate.Typedef) -> Typedef:
    """
    Create a placeholder so that a mapping for identifiable typedefs can be pre-populated.

    This is necessary to avoid looping endlessly through cycles.
    """
    typedef = None  # type: Optional[Typedef]

    if isinstance(intermediate_typedef, swagger_to.intermediate.Primitivedef):
        if intermediate_typedef.type == 'boolean':
            typedef = Booldef()
        elif intermediate_typedef.type == 'integer':
            typedef = Intdef()
        elif intermediate_typedef.type == 'number':
            typedef = Floatdef()
        elif intermediate_typedef.type == 'string':
            if intermediate_typedef.format == 'binary':
                typedef = Filedef()
            else:
                typedef = Strdef()
        elif intermediate_typedef.type == 'file':
            typedef = Filedef()
        else:
            raise NotImplementedError('Converting intermediate type to Python is not supported: {}'.format(
                intermediate_typedef.type))

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Arraydef):
        typedef = Listdef()

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Dictdef()

    elif isinstance(intermediate_typedef, swagger_to.intermediate.AnyValuedef):
        typedef = Anydef()

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Classdef()

    else:
        raise NotImplementedError('Converting intermediate typedef to Python is not supported: {!r}'.format(
            type(intermediate_typedef)))

    assert typedef is not None

    typedef.description = intermediate_typedef.description
    typedef.identifier = intermediate_typedef.identifier

    return typedef


def to_typedefs(
        intermediate_typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> MutableMapping[str, Typedef]:
    """
    Translate type definitions from intermediate representation to Python.

    :param intermediate_typedefs: table of type definitions in intermediate representation
    :return: table of type definitions in Python representation
    """
    typedefs = collections.OrderedDict()  # type: MutableMapping[str, Typedef]

    # Pre-populate object definitions with placeholders to avoid looping endlessly through cycles;
    # See: https://github.com/Parquery/swagger-to/issues/129
    for intermediate_typedef in intermediate_typedefs.values():
        typedefs[intermediate_typedef.identifier] = _create_initial_typedef(intermediate_typedef=intermediate_typedef)

    for typedef in typedefs.values():
        intermediate_typedef = intermediate_typedefs[typedef.identifier]
        _translate_to_typedef_in_place(intermediate_typedef=intermediate_typedef, typedef=typedef, typedefs=typedefs)

    return typedefs


def _to_response(intermediate_response: swagger_to.intermediate.Response,
                 typedefs: MutableMapping[str, Typedef]) -> Response:
    """
    Translate an endpoint response from the intermediate to a Python representation.

    :param intermediate_response: intermediate representation of a response
    :param typedefs: table of type definitions in Python representation
    :return: Python representation of the response
    """
    resp = Response()
    resp.code = intermediate_response.code
    resp.typedef = None if intermediate_response.typedef is None else \
        _anonymous_or_get_typedef(intermediate_typedef=intermediate_response.typedef, typedefs=typedefs)
    resp.description = intermediate_response.description
    return resp


# yapf: disable
@icontract.ensure(
    lambda result:
    sorted(result.parameters, key=id) ==
    sorted((
        param
        for param in (
             [result.body_parameter] if result.body_parameter else []) +
             result.query_parameters +
             result.header_parameters +
             result.path_parameters +
             result.formdata_parameters +
             result.file_parameters),
        key=id),
    enabled=icontract.SLOW)
# yapf: enable
@icontract.ensure(lambda result: all(isinstance(param.typedef, Filedef) for param in result.file_parameters))
def _to_request(endpoint: swagger_to.intermediate.Endpoint, typedefs: MutableMapping[str, Typedef]) -> Request:
    """
    Translate an endpoint from an intermediate representation to a Python client request function.

    :param endpoint: intermediate representation of the endpoint
    :param typedefs: table of type definitions in Python representation
    :return: Python representation of the client request function
    """
    req = Request()
    req.description = endpoint.description
    req.method = endpoint.method
    req.operation_id = endpoint.operation_id
    req.path = endpoint.path

    ##
    # Generate identifiers corresponding to the parameters.
    ##

    for intermediate_param in endpoint.parameters:
        if intermediate_param.name == "":
            raise ValueError("Unexpected empty intermediate parameter name in the endpoint: {}".format(
                endpoint.operation_id))

    param_to_identifier = {
        intermediate_param: swagger_to.snake_case(identifier=intermediate_param.name)
        for intermediate_param in endpoint.parameters
    }

    identifiers = list(param_to_identifier.values())
    needs_location_prefix = len(set(identifiers)) != len(identifiers)
    if needs_location_prefix:
        param_to_identifier = {
            inter_param: swagger_to.snake_case(identifier="{}_{}".format(inter_param.in_what, inter_param.name))
            for inter_param in endpoint.parameters
        }

        ##
        # Assert that there are no conflicts at this point
        ##

        by_identifier = collections.defaultdict(
            list)  # type: MutableMapping[str, List[swagger_to.intermediate.Parameter]]
        for inter_param, identifier in param_to_identifier.items():
            by_identifier[identifier].append(inter_param)

        # yapf: disable
        msgs = [
            "in the endpoint {} {} for the identifier {!r}: {}".format(
                endpoint.method.upper(), endpoint.path, identifier, ", ".join(
                    ["{} in {}".format(inter_param.name, inter_param.in_what)
                     for inter_param in inter_params]))
            for identifier, inter_params in by_identifier.items()
            if len(inter_params) > 1
        ]
        # yapf: enable

        if len(msgs) > 0:
            raise ValueError("There are conflicting identifiers for parameters:\n{}".format("\n".join(msgs)))

    ##
    # Convert parameters
    ##

    assert all(intermediate_param in param_to_identifier for intermediate_param in endpoint.parameters), \
        "Expected all parameters to have a generated argument identifier."

    req.parameters = []
    for intermediate_param in endpoint.parameters:
        identifier = param_to_identifier[intermediate_param]

        param = Parameter()
        param.identifier = identifier
        param.name = intermediate_param.name
        param.in_what = intermediate_param.in_what
        param.typedef = _anonymous_or_get_typedef(intermediate_typedef=intermediate_param.typedef, typedefs=typedefs)
        param.required = intermediate_param.required
        param.description = intermediate_param.description

        req.parameters.append(param)

    ##
    # Check that there is only one body parameter
    ##

    body_parameter_names = [param.name for param in req.parameters if param.in_what == 'body']
    if len(body_parameter_names) > 1:
        raise KeyError('Duplicate body parameters in an endpoint: {}'.format(body_parameter_names))

    ##
    # Categorize parameters
    ##

    for param in req.parameters:
        if isinstance(param.typedef, Filedef):
            req.file_parameters.append(param)
        elif param.in_what == 'body':
            req.body_parameter = param
        elif param.in_what == 'header':
            req.header_parameters.append(param)
        elif param.in_what == 'query':
            req.query_parameters.append(param)
        elif param.in_what == 'path':
            req.path_parameters.append(param)
        elif param.in_what == 'formData':
            req.formdata_parameters.append(param)
        else:
            raise NotImplementedError("Unsupported parameter location: in {}".format(param.in_what))

    # Parameters are sorted so that first come the required ones; python requires the optional parameters to come
    # at the end.
    req.parameters.sort(key=lambda param: not param.required)

    ##
    # Convert responses
    ##

    for code, intermediate_resp in endpoint.responses.items():
        req.responses[code] = _to_response(intermediate_response=intermediate_resp, typedefs=typedefs)

    req.produces = endpoint.produces[:]

    return req


@icontract.ensure(lambda endpoints, result: len(endpoints) == len(result))
def to_requests(endpoints: List[swagger_to.intermediate.Endpoint],
                typedefs: MutableMapping[str, Typedef]) -> List[Request]:
    """
    Translate endpoints from intermediate representation to Python client request functions.

    :param endpoints: intermediate representation of the endpoints
    :param typedefs: table of type definitions in Python representation
    :return: Python representation of client's request functions corresponding to the endpoints
    """
    requests = []  # type: List[Request]
    for endpoint in endpoints:
        requests.append(_to_request(endpoint=endpoint, typedefs=typedefs))

    return requests


@icontract.ensure(lambda result: not result.endswith('\n'))
def _comment(text: str) -> str:
    r"""
    Generate a (possibly multi-line) comment from the text.

    >>> cmt = _comment('  testme\n  \nagain\n')
    >>> assert cmt == '#   testme\n#\n# again\n#'

    :param text: of the comment
    :return: Python code
    """
    out = []  # type: List[str]
    lines = text.split('\n')
    for line in lines:
        rstripped = line.rstrip()
        if len(rstripped) > 0:
            out.append('# {}'.format(rstripped))
        else:
            out.append('#')

    return '\n'.join(out)


@icontract.require(lambda text: text != '')
@icontract.ensure(lambda result: not result.endswith('\n'))
@icontract.ensure(lambda result: result.startswith('r"""') or result.startswith('"""'))
@icontract.ensure(lambda result: result.endswith('"""'))
def _docstring(text: str) -> str:
    """
    Generate a (possibly multi-line) docstring from the text.

    :param text: of the docstring
    :return: Python code
    """
    has_backslash = '\\' in text
    has_triple_quote = '"""' in text

    is_raw = False
    content = text

    if has_triple_quote:
        is_raw = False
        content = text.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
    else:
        if has_backslash:
            is_raw = True

    parts = []  # type: List[str]
    if is_raw:
        parts.append('r')

    lines = text.splitlines()
    if len(lines) > 1:
        parts.append('"""\n')
        parts.append(content)
        parts.append('\n"""')
    elif len(lines) == 1:
        parts.append('"""{}"""'.format(content))

    return ''.join(parts)


def _raise(message: str) -> None:
    """Raise an exception in a template."""
    raise Exception(message)


_NON_IDENTIFIER_RE = re.compile(r'[^a-zA-Z0-9_]')
IDENTIFIER_RE = re.compile('[a-zA-Z_][a-zA-Z0-9_]*')


@icontract.require(lambda name: name != '')
@icontract.ensure(lambda result: IDENTIFIER_RE.fullmatch(result))
def _function_name(name: str) -> str:
    """
    Generate the name of the function which will send the request based on the operation ID.

    :param name: ID of the operation from the Swagger spec
    :return: pep-8 conform name

    >>> _function_name('TestMe')
    'test_me'

    >>> _function_name('test_me')
    'test_me'

    >>> _function_name('Test_me')
    'test_me'

    >>> _function_name('test-me')
    'test_me'

    >>> _function_name('TestMe_to_json')
    'test_me_to_json'

    >>> _function_name('Some Definition' + '_to_jsonable')
    'some_definition_to_jsonable'
    """
    return swagger_to.snake_case(_NON_IDENTIFIER_RE.sub("_", name))


@icontract.require(lambda name: name != '')
@icontract.ensure(lambda result: IDENTIFIER_RE.fullmatch(result))
def _class_name(name: str) -> str:
    """
    Generate the Python name of the class corresponding to the Swagger definition.

    :param name: name of the type definition
    :return: pep-8 conform name

    >>> _class_name('TestMe')
    'TestMe'

    >>> _class_name('test_me')
    'TestMe'

    >>> _class_name('Test_me')
    'TestMe'

    >>> _class_name('test-me')
    'TestMe'
    """
    return swagger_to.capital_camel_case(_NON_IDENTIFIER_RE.sub("_", name))


@icontract.require(lambda name: name != '')
@icontract.ensure(lambda result: IDENTIFIER_RE.fullmatch(result))
def _property_name(name: str) -> str:
    """
    Generate the Python name of the property corresponding to the Swagger definition.

    :param name: name of the type property
    :return: pep-8 conform name

    >>> _property_name('TestMe')
    'test_me'

    >>> _property_name('test_me')
    'test_me'

    >>> _property_name('Test_me')
    'test_me'

    >>> _property_name('test-me')
    'test_me'
    """
    return swagger_to.snake_case(_NON_IDENTIFIER_RE.sub("_", name))


@icontract.require(lambda name: name != '')
@icontract.ensure(lambda result: IDENTIFIER_RE.fullmatch(result))
def _arg_name(name: str) -> str:
    """
    Generate the Python name of the argument corresponding to a Swagger definition.

    :param name: name of the type property
    :return: pep-8 conform name

    >>> _arg_name('TestMe')
    'test_me'

    >>> _arg_name('test_me')
    'test_me'

    >>> _arg_name('Test_me')
    'test_me'

    >>> _arg_name('test-me')
    'test_me'
    """
    return swagger_to.snake_case(_NON_IDENTIFIER_RE.sub("_", name))


@icontract.require(lambda name: name != '')
@icontract.ensure(lambda result: IDENTIFIER_RE.fullmatch(result))
def _var_name(name: str) -> str:
    """
    Generate the Python name of the variable corresponding to a Swagger definition.

    :param name: name of the type property
    :return: pep-8 conform name

    >>> _var_name('TestMe')
    'test_me'

    >>> _var_name('test_me')
    'test_me'

    >>> _var_name('Test_me')
    'test_me'

    >>> _var_name('test-me')
    'test_me'
    """
    return swagger_to.snake_case(_NON_IDENTIFIER_RE.sub("_", name))


# Jinja2 environment
_ENV = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, loader=jinja2.BaseLoader())
_ENV.filters.update({
    'comment': _comment,
    'docstring': _docstring,
    'function_name': _function_name,
    'class_name': _class_name,
    'property_name': _property_name,
    'arg_name': _arg_name,
    'var_name': _var_name,
    'raise': _raise,
    'repr': lambda value: repr(value),
    'upper_first': swagger_to.upper_first
})


def _from_string_with_informative_exceptions(env: jinja2.Environment, text: str) -> jinja2.Template:
    """
    Parse the jinja2 template raising more informative exceptions if there are any.

    :param env: global jinja2 environment
    :param text: text of the template
    :return: parsed template
    """
    syntax_err = None  # type: Optional[jinja2.exceptions.TemplateSyntaxError]
    try:
        return env.from_string(source=text)
    except jinja2.exceptions.TemplateSyntaxError as err:
        syntax_err = err

    if syntax_err is not None:
        lines = text.splitlines()
        line = lines[syntax_err.lineno - 1]

        msg = '{}\n{}'.format(syntax_err.message, line)

        raise jinja2.exceptions.TemplateSyntaxError(
            message=msg, lineno=syntax_err.lineno, name=syntax_err.name, filename=syntax_err.filename)
    else:
        raise AssertionError("Unhandled execution path")


def _type_expression(typedef: Typedef, path: Optional[str] = None) -> str:
    """
    Translate the type definition in Python representation to a type expression as Python code.

    :param typedef: Python representation of the type definition
    :param path: path in the Swagger spec
    :return: Python code
    """
    # pylint: disable=too-many-return-statements
    if isinstance(typedef, Booldef):
        return 'bool'
    elif isinstance(typedef, Intdef):
        return 'int'
    elif isinstance(typedef, Floatdef):
        return 'float'
    elif isinstance(typedef, Strdef):
        return 'str'
    elif isinstance(typedef, Bytesdef):
        return 'bytes'
    elif isinstance(typedef, Filedef):
        return 'BinaryIO'
    elif isinstance(typedef, Listdef):
        if typedef.items is None:
            raise ValueError('Unexpected None items in typedef: {!r}'.format(typedef.identifier))

        return 'List[' + _type_expression(typedef=typedef.items, path=str(path) + '.items') + ']'
    elif isinstance(typedef, Dictdef):
        if typedef.values is None:
            raise ValueError('Unexpected None values in typedef: {!r}'.format(typedef.identifier))

        return 'Dict[str, ' + _type_expression(typedef=typedef.values, path=str(path) + '.values') + ']'

    elif isinstance(typedef, Anydef):
        return 'Any'

    elif isinstance(typedef, Classdef):
        if typedef.identifier == '':
            raise NotImplementedError(('Translating an anonymous class to a type expression '
                                       'is not supported: {}').format(path))

        return "'{}'".format(_class_name(typedef.identifier))
    else:
        raise NotImplementedError('Translating the typedef to a type expression is not supported: {!r}: {}'.format(
            type(typedef), path))


_CLASS_DEF_WO_ATTRIBUTES = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
{% if classdef.attributes %}{{ raise('Expected a classdef without attributes, but got some.') }}{% endif %}
class {{ classdef.identifier|class_name }}:
    {% if classdef.description %}
    {{ classdef.description|upper_first|docstring|indent }}

    {% endif %}
    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to {{ (classdef.identifier+"_to_jsonable")|function_name }}.

        :return: a JSON-able representation
        """
        return {{ (classdef.identifier+"_to_jsonable")|function_name }}(self)''')

_CLASS_DEF_WITH_ATTRIBUTES_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
{% if not classdef.attributes %}{{ raise('Expected a class definition with attributes, but got none.') }}{% endif %}
class {{ classdef.identifier|class_name }}:
    {% if classdef.description %}
    {{ classdef.description|upper_first|docstring|indent }}

    {% endif %}
    def __init__(
            self,
    {% for attr in classdef.attributes.values() %}
    {% if not attr.required %}
            {{ attr.name|arg_name }}: Optional[{{ attribute_type[attr] }}] = None{{ ') -> None:' if loop.last else ',' }}
    {% else %}
            {{ attr.name|arg_name }}: {{ attribute_type[attr] }}{{ ') -> None:' if loop.last else ',' }}
    {% endif %}{# /if not attr.required #}
    {% endfor %}{# /for attr #}
        """Initializes with the given values."""
        {% set newliner = joiner('SWITCH') %}
        {% for attr in classdef.attributes.values() %}
        {% if newliner() %}{{ '\\n' }}{% endif %}
        {% if attr.description %}
        {{ attr.description|comment|indent|indent }}
        {% endif %}
        self.{{ attr.name|property_name }} = {{ attr.name|arg_name }}
        {% endfor %}

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to {{ (classdef.identifier+"_to_jsonable")|function_name }}.

        :return: JSON-able representation
        """
        return {{ (classdef.identifier+"_to_jsonable")|function_name }}(self)''')


@icontract.require(lambda classdef: classdef.identifier != '', 'Anonymous classes not allowed', enabled=True)
@icontract.ensure(lambda result: not result.endswith('\n'))
def _generate_class_definition(classdef: Classdef) -> str:
    """
    Generate the Python code defining the class given the class definition.

    :param classdef: class definition in Python representation
    :return: Python code
    """
    if len(classdef.attributes) == 0:
        return _CLASS_DEF_WO_ATTRIBUTES.render(classdef=classdef)

    attribute_type = dict()
    for attr in classdef.attributes.values():
        if attr.typedef is None:
            raise ValueError('Unexpected None typedef of attr {!r} in class {!r}'.format(
                attr.name, classdef.identifier))

        attribute_type[attr] = _type_expression(
            typedef=attr.typedef, path='{}.{}'.format(classdef.identifier, attr.name))

    return _CLASS_DEF_WITH_ATTRIBUTES_TPL.render(classdef=classdef, attribute_type=attribute_type)


def _default_value(typedef: Typedef) -> str:
    """
    Determine the default value of the given type definition.

    :param typedef: type definition in Python representation.
    :return: Python code
    """
    # pylint: disable=too-many-return-statements
    if isinstance(typedef, Booldef):
        return 'False'
    elif isinstance(typedef, Intdef):
        return '0'
    elif isinstance(typedef, Floatdef):
        return '0.0'
    elif isinstance(typedef, Strdef):
        return "''"
    elif isinstance(typedef, Bytesdef):
        return "b''"
    elif isinstance(typedef, Listdef):
        return '[]'
    elif isinstance(typedef, Dictdef):
        return 'dict()'
    elif isinstance(typedef, Anydef):
        return 'None'
    elif isinstance(typedef, Classdef):
        return _function_name('new_{}()'.format(typedef.identifier))
    else:
        raise NotImplementedError('Translating the typedef to a default value is not supported: {}'.format(typedef))


_FACTORY_METHOD_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
def {{ ("new_"+classdef.identifier)|function_name }}() -> {{ classdef.identifier|class_name }}:
    """Generates an instance of {{ classdef.identifier|class_name }} with default values."""
    {% if not required_attributes %}
    return {{ classdef.identifier|class_name }}()
    {% else %}
    return {{ classdef.identifier|class_name }}(
        {% for attr in required_attributes %}
        {{ attr.name|arg_name }}={{ default_value[attr] }}{{ ')' if loop.last else ',' }}
        {% endfor %}
    {% endif %}{# /if not required_attrbiutes #}
''')


@icontract.ensure(lambda result: not result.endswith('\n'))
def _generate_factory_method(classdef: Classdef) -> str:
    """
    Generate the code of the factory method for a class conforming to the given class definition.

    :param classdef: class definition in Python representation
    :return: Python code
    """
    default_value = dict()
    for attr in classdef.attributes.values():
        if attr.typedef is None:
            raise ValueError('Unexpected None typedef of attr {!r}'.format(attr.name))

        default_value[attr] = _default_value(typedef=attr.typedef)

    return _FACTORY_METHOD_TPL.render(
        classdef=classdef,
        required_attributes=[attr for attr in classdef.attributes.values() if attr.required],
        default_value=default_value).strip()


_FROM_OBJ_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
def from_obj(obj: Any, expected: List[type], path: str = '') -> Any:
    """
    Checks and converts the given obj along the expected types.

    :param obj: to be converted
    :param expected: list of types representing the (nested) structure
    :param path: to the object used for debugging
    :return: the converted object
    """
    if not expected:
        raise ValueError("`expected` is empty, but at least one type needs to be specified.")

    exp = expected[0]

    if exp == float:
        if isinstance(obj, int):
            return float(obj)

        if isinstance(obj, float):
            return obj

        raise ValueError(
            'Expected object of type int or float at {!r}, but got {}.'.format(path, type(obj)))

    if exp in [bool, int, str, list, dict]:
        if not isinstance(obj, exp):
            raise ValueError(
                'Expected object of type {} at {!r}, but got {}.'.format(exp, path, type(obj)))

    if exp in [bool, int, float, str]:
        return obj

    if exp == list:
        lst = []  # type: List[Any]
        for i, value in enumerate(obj):
            lst.append(
                from_obj(value, expected=expected[1:], path='{}[{}]'.format(path, i)))

        return lst

    if exp == dict:
        adict = dict()  # type: Dict[str, Any]
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError(
                    'Expected a key of type str at path {!r}, got: {}'.format(path, type(key)))

            adict[key] = from_obj(value, expected=expected[1:], path='{}[{!r}]'.format(path, key))

        return adict
    {% for classdef in classdefs %}

    if exp == {{ classdef.identifier|class_name }}:
        return {{ (classdef.identifier+"_from_obj")|function_name }}(obj, path=path)
    {% endfor %}

    raise ValueError("Unexpected `expected` type: {}".format(exp))''')


@icontract.ensure(lambda result: not result.endswith('\n'))
def _generate_from_obj(classdefs: List[Classdef]) -> str:
    """
    Generate the code of the ``from_obj`` function.

    :param classdefs: all available class definitions in Python representation
    :return: Python code
    """
    return _FROM_OBJ_TPL.render(classdefs=classdefs)


def _expected_type_expression(typedef: Typedef) -> str:
    """
    Determine the type expression supplied to ``from_obj`` function corresponding to the type definition.

    :param typedef: type definition in Python representation
    :return: Python code representing the type definition
    """
    # pylint: disable=too-many-return-statements
    if isinstance(typedef, Booldef):
        return 'bool'
    elif isinstance(typedef, Intdef):
        return 'int'
    elif isinstance(typedef, Floatdef):
        return 'float'
    elif isinstance(typedef, Strdef):
        return 'str'
    elif isinstance(typedef, Bytesdef):
        return 'bytes'
    elif isinstance(typedef, Listdef):
        if typedef.items is None:
            raise ValueError('Unexpected None items in typedef: {!r}'.format(typedef.identifier))
        if isinstance(typedef.items, Anydef):
            return 'list, Any'
        return 'list, {}'.format(_expected_type_expression(typedef=typedef.items))
    elif isinstance(typedef, Dictdef):
        if typedef.values is None:
            raise ValueError('Unexpected None values in typedef: {!r}'.format(typedef.identifier))
        if isinstance(typedef.values, Anydef):
            return 'dict, Any'
        return 'dict, {}'.format(_expected_type_expression(typedef=typedef.values))
    elif isinstance(typedef, Classdef):
        return _class_name(typedef.identifier)
    elif isinstance(typedef, Anydef):
        return 'Any'
    else:
        raise NotImplementedError('Translating the typedef to an expected type is not supported: {}'.format(typedef))


_CLASS_FROM_OBJ_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
def {{ (classdef.identifier+"_from_obj")|function_name }}(obj: Any, path: str = "") -> {{ classdef.identifier|class_name }}:
    """
    Generates an instance of {{ classdef.identifier|class_name }} from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of {{ classdef.identifier|class_name }}
    :param path: path to the object used for debugging
    :return: parsed instance of {{ classdef.identifier|class_name }}
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    {% if not classdef.attributes %}
    return {{ classdef.identifier|class_name }}()
    {% else %}
    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))
    {% for attr in classdef.attributes.values() %}

    {% if attr.required %}
    {% if attr in expected_type_expression %}
    {{ (attr.name+"_from_obj")|var_name }} = from_obj(
        obj[{{ attr.name|repr }}],
        expected=[{{ expected_type_expression[attr] }}],
        path=path + {{ '.%s'|format(attr.name)|repr }})  # type: {{ type_expression[attr] }}
    {% else %}{# if attr in expected_type_expression #}
    {{ (attr.name+"_from_obj")|var_name }} = obj[{{ attr.name|repr }}]
    {% endif %}{# /if attr in expected_type_expression #}
    {% else %}{# if attr.required #}
    {% if attr in expected_type_expression %}
    {{ ("obj_"+attr.name)|var_name }} = obj.get({{ attr.name|repr }}, None)
    if {{ ("obj_"+attr.name)|var_name }} is not None:
        {{ (attr.name+"_from_obj")|var_name }} = from_obj(
            {{ ("obj_"+attr.name)|var_name }},
            expected=[{{ expected_type_expression[attr] }}],
            path=path + {{ '.%s'|format(attr.name)|repr }})  # type: Optional[{{ type_expression[attr] }}]
    else:
        {{ (attr.name+"_from_obj")|var_name }} = None
    {% else %}{# if attr in expected_type_expression #}
    {{ (attr.name+"_from_obj")|var_name }} = obj.get({{ attr.name|repr }}, None)
    {% endif %}{# /if attr in expected_type_expression #}
    {% endif %}{# /if attr.required #}
    {% endfor %}{# /for attr in classdef.attributes.values() #}

    return {{ classdef.identifier|class_name }}(
    {% for attr in classdef.attributes.values() %}
        {{ attr.name|arg_name }}={{ (attr.name+"_from_obj")|var_name }}{{ ')' if loop.last else ',' }}
    {% endfor %}{# /for attr in classdef.attributes.values() #}
    {% endif %}{# /if not classdef.attributes #}''')


@icontract.ensure(lambda result: not result.endswith('\n'))
def _generate_class_from_obj(classdef: Classdef) -> str:
    """
    Generate the code of the ``{class}_from_obj`` function that parses the JSON-ed object to an instance of a class.

    :param classdef: class definition in Python representation
    :return: Python code
    """
    expected_type_expression = dict()
    type_expression = dict()
    for attr in classdef.attributes.values():
        if attr.typedef is None:
            raise ValueError('Unexpected None typedef of attr {!r} in class {!r}'.format(
                attr.name, classdef.identifier))

        if not isinstance(attr.typedef, Anydef):
            expected_type_expression[attr] = _expected_type_expression(typedef=attr.typedef)
        type_expression[attr] = _type_expression(typedef=attr.typedef, path=classdef.identifier + '.' + attr.name)

    return _CLASS_FROM_OBJ_TPL.render(
        classdef=classdef, expected_type_expression=expected_type_expression, type_expression=type_expression).strip()


_TO_JSONABLE_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
def to_jsonable(obj: Any, expected: List[type], path: str = "") -> Any:
    """
    Checks and converts the given object along the expected types to a JSON-able representation.

    :param obj: to be converted
    :param expected: list of types representing the (nested) structure
    :param path: path to the object used for debugging
    :return: JSON-able representation of the object
    """
    if not expected:
        raise ValueError("`expected` is empty, but at least one type needs to be specified.")

    exp = expected[0]
    if not isinstance(obj, exp):
        raise ValueError('Expected object of type {} at path {!r}, but got {}.'.format(
            exp, path, type(obj)))

    # Assert on primitive types to help type-hinting.
    if exp == bool:
        assert isinstance(obj, bool)
        return obj

    if exp == int:
        assert isinstance(obj, int)
        return obj

    if exp == float:
        assert isinstance(obj, float)
        return obj

    if exp == str:
        assert isinstance(obj, str)
        return obj

    if exp == list:
        assert isinstance(obj, list)

        lst = []  # type: List[Any]
        for i, value in enumerate(obj):
            lst.append(
                to_jsonable(value, expected=expected[1:], path='{}[{}]'.format(path, i)))

        return lst

    if exp == dict:
        assert isinstance(obj, dict)

        adict = dict()  # type: Dict[str, Any]
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError(
                    'Expected a key of type str at path {!r}, got: {}'.format(path, type(key)))

            adict[key] = to_jsonable(
                value,
                expected=expected[1:],
                path='{}[{!r}]'.format(path, key))

        return adict
    {% for classdef in classdefs %}

    if exp == {{ classdef.identifier|class_name }}:
        assert isinstance(obj, {{ classdef.identifier|class_name }})
        return {{ (classdef.identifier+"_to_jsonable")|function_name }}(obj, path=path)
    {% endfor %}{# /for classdef in classdefs #}

    raise ValueError("Unexpected `expected` type: {}".format(exp))''')


@icontract.ensure(lambda result: not result.endswith('\n'))
def _generate_to_jsonable(classdefs: List[Classdef]) -> str:
    """
    Generate the code of the ``to_jsonable`` function that converts a Python object to a JSON-able format.

    :param classdefs: list of all available class definitions
    :return: Python code
    """
    return _TO_JSONABLE_TPL.render(classdefs=classdefs)


_CLASS_TO_JSONABLE_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
def {{ (classdef.identifier + "_to_jsonable")|function_name }}(
        {{ classdef.identifier|arg_name }}: {{ classdef.identifier|class_name }},
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of {{ classdef.identifier|class_name }}.

    :param {{ classdef.identifier|arg_name }}: instance of {{ classdef.identifier|class_name }} to be JSON-ized
    :param path: path to the {{ classdef.identifier|arg_name }} used for debugging
    :return: a JSON-able representation
    """
    {% if not classdef.attributes %}
    return dict()
    {% else %}
    res = dict()  # type: Dict[str, Any]
    {% for attr in classdef.attributes.values() %}

    {% set assignment %}
{% if is_primitive[attr] %}
res[{{ attr.name|repr }}] = {{ classdef.identifier|arg_name }}.{{ attr.name|property_name }}
{% else %}
res[{{ attr.name|repr }}] = to_jsonable(
    {{ classdef.identifier|arg_name }}.{{ attr.name|property_name }},
    expected=[{{ expected_type_expression[attr] }}],
    path={{ '{}.%s'|format(attr.name)|repr }}.format(path))
{% endif %}{# /if is_primitive[attr] #}
    {% endset %}{# /set assignment #}
    {% if not attr.required %}
    if {{ classdef.identifier|arg_name }}.{{ attr.name|property_name }} is not None:
        {{ assignment|trim|indent }}
    {% else %}
    {{ assignment|trim|indent }}
    {% endif %}{# /if not attr.required #}
    {% endfor %}{# /for attr in classdef.attributes.values() #}

    return res
    {% endif %}{# /if not classdef.attributes #}''')


@icontract.ensure(lambda result: not result.endswith('\n'))
def _generate_class_to_jsonable(classdef: Classdef) -> str:
    """
    Generate ``{class}_to_jsonable`` function which converts the given instance of the class to a JSON-able format.

    :param classdef: class definition in Python representation
    :return: Python code
    """
    is_primitive = dict()
    expected_type_expression = dict()

    for attr in classdef.attributes.values():
        if attr.typedef is None:
            raise ValueError('Unexpected None typedef of attr {!r} in class {!r}'.format(
                attr.name, classdef.identifier))

        is_primitive[attr] = isinstance(attr.typedef, (Booldef, Intdef, Floatdef, Strdef, Anydef))
        if not isinstance(attr.typedef, Anydef):
            expected_type_expression[attr] = _expected_type_expression(typedef=attr.typedef)

    return _CLASS_TO_JSONABLE_TPL.render(
        classdef=classdef, is_primitive=is_primitive, expected_type_expression=expected_type_expression).strip()


_REQUEST_DOCSTRING_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
{% if request.description %}
{{ request.description|upper_first }}
{% else %}
Send a {{ request.method }} request to {{ request.path }}.
{% endif %}{# /if request.description #}
{% if request.parameters %}

{% for param in request.parameters %}
{% if not param.description %}
:param {{ param.identifier|arg_name }}:
{% else %}
{% if '\\n' in param.description %}
:param {{ param.identifier|arg_name }}:
    {{ param.description|indent }}
{% else %}
:param {{ param.identifier|arg_name }}: {{ param.description }}
{% endif %}{# /if '\\n' in param.description #}
{% endif %}{# /if not param.description #}
{% endfor %}{# /for request.parameters #}
{% endif %}{# /if request.parameters #}
{% if resp is none or resp.description == ''%}

:return:
{% else %}
{% if '\\n' in resp.description %}

:return:
    {{ resp.description|indent }}
{% else %}

:return: {{ resp.description }}
{% endif %}{# /if '\\n' in resp.description #}
{% endif %}{# /if resp is none #}''')

_REQUEST_FUNCTION_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
{% if not request.parameters %}
def {{ function_name }}(self) -> {{ return_type }}:
{% else %}
{% set suffix = ') -> %s:'|format(return_type) %}
def {{ function_name }}(
        self,
        {% for param in request.parameters %}
        {% if not param.required %}
        {{ param.identifier|arg_name }}: Optional[{{ type_expression[param] }}] = None{{ suffix if loop.last else ',' }}
        {% else %}
        {{ param.identifier|arg_name }}: {{ type_expression[param] }}{{ suffix if loop.last else ',' }}
        {% endif %}
        {% endfor %}{# /for param in request.parameters #}
{% endif %}{# /if not request.parameters #}
    {{ request_docstring|docstring|indent }}
    {% if not path_tokens %}{### Path parameters ###}
    url = self.url_prefix + {{ request.path|repr }}
    {% else %}
    url = "".join([
        self.url_prefix,
    {% for token in path_tokens %}
    {% if token.parameter %}
        {{ 'str(%s)'|format(token.parameter.identifier if is_str[token.parameter] else token.parameter.identifier) }}{#
            #}{{ '])' if loop.last else ',' }}
    {% else %}
        {{ token.text|repr }}{{ '])' if loop.last else ',' }}
    {% endif %}
    {% endfor %}{# /for token in path_tokens #}
    {% endif %}{# /if not path_tokens #}
    {% if request.header_parameters %}{### Header parameters ###}

    headers = {}  # type: Dict[str, str]
        {% for param in request.header_parameters %}

            {% set set_header_item %}
                {% if is_str[param] %}
headers[{{ param.name|repr }}] = {{ param.identifier|arg_name }}
                {% elif is_primitive[param] %}
headers[{{ param.name|repr }}] = json.dumps({{ param.identifier|arg_name }})
                {% else %}
headers[{{ param.name|repr }}] = json.dumps(
    to_jsonable(
        {{ param.identifier|arg_name }},
        expected=[{{ expected_type_expression[param] }}]))
                {% endif %}{# /if is_primitive[param] #}
            {% endset %}
            {% if param.required %}
    {{ set_header_item|trim|indent }}
            {% else %}
    if {{ param.identifier|arg_name }} is not None:
        {{ set_header_item|trim|indent|indent }}
            {% endif %}{# /if param.required #}
        {% endfor %}{# /for param in request.header_parameters #}
    {% endif %}{# /if request.header_parameters #}
    {% if request.query_parameters %}{### Query parameters ###}

    params = {}  # type: Dict[str, str]
        {% for param in request.query_parameters %}

            {% set set_params_item %}
                {% if is_str[param] %}
params[{{ param.name|repr }}] = {{ param.identifier|arg_name }}
                {% elif is_primitive[param] %}
params[{{ param.name|repr }}] = json.dumps({{ param.identifier|arg_name }})
                {% else %}
params[{{ param.name|repr }}] = json.dumps(
    to_jsonable(
        {{ param.identifier|arg_name }},
        expected=[{{ expected_type_expression[param] }}]))
                {% endif %}{# /if is_primitive[param] #}
            {% endset %}
            {% if param.required %}
    {{ set_params_item|trim|indent }}
            {% else %}
    if {{ param.identifier }} is not None:
        {{ set_params_item|trim|indent|indent }}
            {% endif %}{# /if param.required #}
        {% endfor %}{# /for param in request.query_parameters #}
    {% endif %}{# /if request.query_parameters #}
    {% if request.body_parameter %}{### Body parameter ###}

    {% set set_body %}
        {% if is_primitive[request.body_parameter] %}
data = {{ request.body_parameter.identifier|arg_name }}
        {% else %}
data = to_jsonable(
    {{ request.body_parameter.identifier|arg_name }},
    expected=[{{ expected_type_expression[request.body_parameter] }}])
        {% endif %}{# /is_primitive[request.body_parameter] #}
    {% endset %}
    {% if request.body_parameter.required %}
    {{ set_body|indent }}
    {% else %}
    data = None  # type: Optional[Any]
    if {{ request.body_parameter.identifier|arg_name }} != None:
        {{ set_body|trim|indent|indent }}
    {% endif %}{# /if request.body_parameter.required #}
    {% endif %}{# /if request.body_parameter #}
    {% if request.formdata_parameters %}{### Form-data parameters ###}

    data = {}  # type: Dict[str, str]
    {% for param in request.formdata_parameters %}

        {% set set_data_item %}
            {% if is_str[param] %}
data[{{ param.name|repr }}] = {{ param.identifier|arg_name }}
            {% elif is_primitive[param] %}
data[{{ param.name|repr }}] = json.dumps({{ param.identifier|arg_name }})
            {% else %}
data[{{ param.name|repr }}] = json.dumps(
    to_jsonable(
        {{ param.identifier|arg_name }},
        expected=[{{ expected_type_expression[param] }}]))
            {% endif %}{# /if is_primitive[param] #}
        {% endset %}
        {% if param.required %}
    {{ set_data_item|trim|indent|indent }}
        {% else %}
    if {{ param.identifier|arg_name }} is not None:
        {{ set_data_item|trim|indent|indent }}
        {% endif %}{# /if param.required #}
    {% endfor %}{# /for param in request.formdata_parameters #}
    {% endif %}{# /if request.formdata_parameters #}
    {% if request.file_parameters %}{### File parameters ###}

    files = {}  # type: Dict[str, BinaryIO]
        {% for param in request.file_parameters %}

            {% if param.required %}
    files[{{ param.name|repr }}] = {{ param.identifier|arg_name }}
            {% else %}
    if {{ param.identifier|arg_name }} is not None:
        files[{{ param.name|repr }}] = {{ param.identifier|arg_name }}
            {% endif %}{# /if param.required #}
        {% endfor %}{# /for param in request.file_parameters #}
    {% endif %}{# /if request.file_parameters #}

    {% if not request.parameters %}
    resp = self.session.request(method={{ request.method|repr }}, url=url)
    {% else %}
    resp = self.session.request(
        method={{ request.method|repr }},
        url=url,
        {% if request.header_parameters %}
        headers=headers,
        {% endif %}
        {% if request.query_parameters %}
        params=params,
        {% endif %}
        {% if request.body_parameter %}
        json=data,
        {% endif %}
        {% if request.formdata_parameters %}
        data=data,
        {% endif %}
        {% if request.file_parameters %}
        files=files,
        {% endif %}
        {% if return_type == 'BinaryIO' %}
        stream=True,
        {% endif %}
    )
    {% endif %}{# /if not request.parameters #}

    {% if return_type == 'BinaryIO' %}
    resp.raise_for_status()
    return _wrap_response(resp)
    {% else %}
    with contextlib.closing(resp):
        resp.raise_for_status()
        {% if return_type == 'bytes' %}
        return resp.content
        {% elif return_type == 'MutableMapping[str, Any]' %}
        return resp.json()
        {% else %}
        return from_obj(
            obj=resp.json(),
            expected=[{{ expected_type_expression[resp] }}])
        {% endif %}
    {% endif %}''')


class _Token:
    """Represent a token of the tokenized Swagger path to an endpoint."""

    def __init__(self, text: str, parameter: Optional[Parameter] = None) -> None:
        """
        Initialize with the given values.

        :param text: text encompassed by the token
        :param parameter: parameter, if referenced by the token
        """
        self.text = text
        self.parameter = parameter


@icontract.require(
    lambda request: not request.body_parameter or not request.formdata_parameters,
    'Both body parameter and form-data parameters are specified. '
    'The python client does not know how to resolve this request.',
    enabled=True)
@icontract.ensure(lambda result: not result.endswith('\n'))
def _generate_request_function(request: Request) -> str:
    """
    Generate the code of the client request function.

    :param request: request to the endpoint in Python representation
    :return: Python code
    """
    ##
    # Prepare response
    ##

    resp = None  # type: Optional[Response]
    return_type = 'bytes'

    if '200' in request.responses:
        resp = request.responses['200']

        if request.produces == ['application/json']:
            if resp.typedef is not None:
                return_type = _type_expression(typedef=resp.typedef, path=request.operation_id + '.' + str(resp.code))
            else:
                # The schema for the response has not been defined. Hence we can not parse the response to an object,
                # but we can at least parse it as JSON.
                return_type = 'MutableMapping[str, Any]'
        elif resp.typedef is not None:
            return_type = _type_expression(typedef=resp.typedef, path=request.operation_id + '.' + str(resp.code))

    ##
    # Preapre request docstring
    ##

    request_docstring = _REQUEST_DOCSTRING_TPL.render(request=request, resp=resp).rstrip()

    ##
    # Prepare a representation of path parameters
    ##

    token_pth = swagger_to.tokenize_path(path=request.path)
    name_to_parameters = {param.name: param for param in request.parameters}

    path_tokens = []  # type: List[_Token]
    if token_pth.parameter_to_token_indices:
        for i, token_text in enumerate(token_pth.tokens):
            param = None  # type: Optional[Parameter]
            if i in token_pth.token_index_to_parameter:
                param_name = token_pth.token_index_to_parameter[i]
                param = name_to_parameters[param_name]

            path_tokens.append(_Token(text=token_text, parameter=param))

    ##
    # Prepare expected types
    ##

    expected_type_expression = dict()  # type: Dict[Union[Parameter, Response], str]
    for param in request.parameters:
        if isinstance(param.typedef, Filedef):
            continue

        if param.typedef is None:
            raise ValueError('Unexpected None typedef in param {!r} of request {!r}'.format(
                param.name, request.operation_id))

        expected_type_expression[param] = _expected_type_expression(typedef=param.typedef)

    if return_type not in ['bytes', 'MutableMapping[str, Any]', 'BinaryIO']:
        if resp is None:
            raise ValueError('Unexpected None resp with return_type {!r} in request {!r}'.format(
                return_type, request.operation_id))

        if resp.typedef is None:
            raise ValueError('Unexpected None resp.typedef with return_type {!r} in request {!r}'.format(
                return_type, request.operation_id))

        expected_type_expression[resp] = _expected_type_expression(typedef=resp.typedef)

    ##
    # Render
    ##

    type_expression = dict()
    for param in request.parameters:
        if param.typedef is None:
            raise ValueError('Unexpected None typedef of param {!r} in request {!r}'.format(
                param.name, request.operation_id))

        type_expression[param] = _type_expression(
            typedef=param.typedef, path='{}.{}'.format(request.operation_id, param.name))

    return _REQUEST_FUNCTION_TPL.render(
        request=request,
        function_name=_function_name(request.operation_id),
        return_type=return_type,
        resp=resp,
        request_docstring=request_docstring,
        type_expression=type_expression,
        path_tokens=path_tokens,
        is_str={param: isinstance(param.typedef, Strdef)
                for param in request.parameters},
        is_primitive={
            param: isinstance(param.typedef, (Booldef, Intdef, Floatdef, Strdef, Filedef))
            for param in request.parameters
        },
        expected_type_expression=expected_type_expression).strip()


_CLIENT_PY = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for {{ service_name }}."""

# pylint: skip-file
# pydocstyle: add-ignore=D105,D107,D401

import contextlib
import json
from typing import Any, BinaryIO, Dict, List, MutableMapping, Optional, cast

import requests
import requests.auth
{% if file_responses %}

from http.client import HTTPResponse

import urllib3


class _WrappedResponse(urllib3.HTTPResponse):
    """
    Wrap `requests.Response` so that it fits the `BinaryIO` interface.

    If we directly used `requests.Response`, the user would need to use `requests.Response.raw`,
    but explicitly close `requests.Response`.
    This is confusing and error-prone, so we wrap it all together into a `BinaryIO` interface.

    Additionally, `requests` have no official type annotation making it hard
    for client code to be statically type-checked.
    """

    # noinspection PyMissingConstructor
    def __init__(self, response: requests.Response):
        self._response = response

    def __getattr__(self, item):
        return getattr(self._response.raw, item)

    def close(self):
        self._response.close()


def _wrap_response(resp: requests.Response) -> HTTPResponse:
    """
    Wrap HTTPResponse object.
    """

    # urllib3.HTTPResponse has compatible interface of standard http lib.
    # (see docs for urllib3.HTTPResponse)
    return cast(HTTPResponse, _WrappedResponse(resp))
{% endif %}{# /if file_responses #}
{% if classdefs %}


{{ from_obj }}


{{ to_jsonable }}
{% for classdef in classdefs %}


{{ class_definition[classdef] }}


{{ factory_method[classdef] }}


{{ class_from_obj[classdef] }}


{{ class_to_jsonable[classdef] }}
{% endfor %}{# /for classdef in classdefs #}
{% endif %}{# /if classdefs #}


class RemoteCaller:
    """Executes the remote calls to the server."""

    def __init__(
        self,
        url_prefix: str,
        auth: Optional[requests.auth.AuthBase] = None,
        session: Optional[requests.Session] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth
        self.session = session

        if not self.session:
            self.session = requests.Session()
            self.session.auth = self.auth
    {% for request in requests %}

    {{ request_function[request]|indent }}
    {% endfor %}{# /for request in requests #}


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

''')


@icontract.ensure(lambda result: result.endswith('\n'), 'File ends with a new line.')
def generate_client_py(service_name: str, typedefs: MutableMapping[str, Typedef], requests: List[Request]) -> str:
    """
    Generate the client code.

    :param service_name: used to designate the service that client connects to
    :param typedefs: table of type definitions in Python representation
    :param requests: request functions in Python representation
    :return: Python code
    """
    classdefs = [typedef for typedef in typedefs.values() if isinstance(typedef, Classdef)]
    file_responses = [
        request for request in requests
        if '200' in request.responses and isinstance(request.responses['200'].typedef, Filedef)
    ]

    assert len(set(classdefs)) == len(classdefs), \
        'All class definitions in Python representation are expected to be unique.'

    observed_request_function_names = dict()  # type: Dict[str, Request]
    for request in requests:
        function_name = _function_name(name=request.operation_id)
        if function_name in observed_request_function_names:
            raise KeyError(
                'The function names for the requests with the operation IDs {!r} and {!r} are identical: {!r}'.format(
                    request.operation_id, observed_request_function_names[function_name], function_name))

    return _CLIENT_PY.render(
        service_name=service_name,
        classdefs=classdefs,
        file_responses=file_responses,
        from_obj=_generate_from_obj(classdefs=classdefs),
        to_jsonable=_generate_to_jsonable(classdefs=classdefs),
        class_definition={classdef: _generate_class_definition(classdef=classdef)
                          for classdef in classdefs},
        factory_method={classdef: _generate_factory_method(classdef=classdef)
                        for classdef in classdefs},
        class_from_obj={classdef: _generate_class_from_obj(classdef=classdef)
                        for classdef in classdefs},
        class_to_jsonable={classdef: _generate_class_to_jsonable(classdef=classdef)
                           for classdef in classdefs},
        requests=requests,
        request_function={request: _generate_request_function(request=request)
                          for request in requests})
