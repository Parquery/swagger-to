#!/usr/bin/env python3
"""Generate a Python client from Swagger specification."""

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches
# pylint: disable=too-many-statements,too-many-lines

import collections
from typing import MutableMapping, Union, List, Optional, Dict  # pylint: disable=unused-import

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
                              typedefs: MutableMapping[str, Typedef]) -> Typedef:
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

    return _to_typedef(intermediate_typedef=intermediate_typedef)


def _to_typedef(intermediate_typedef: swagger_to.intermediate.Typedef) -> Typedef:
    """
    Translate the type definition in intermediate representation to Python.

    :param intermediate_typedef: type definition in intermediate representation
    :return: type definition in Python representation
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
            typedef = Strdef()
        elif intermediate_typedef.type == 'file':
            typedef = Filedef()
        else:
            raise NotImplementedError('Converting intermediate type to Python is not supported: {}'.format(
                intermediate_typedef.type))

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Arraydef):
        typedef = Listdef()
        typedef.items = _to_typedef(intermediate_typedef=intermediate_typedef.items)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Dictdef()
        typedef.values = _to_typedef(intermediate_typedef=intermediate_typedef.values)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Classdef()

        for intermediate_prop in intermediate_typedef.properties.values():
            attr = Attribute()
            attr.description = intermediate_prop.description
            attr.name = intermediate_prop.name
            attr.typedef = _to_typedef(intermediate_typedef=intermediate_prop.typedef)
            attr.required = intermediate_prop.required
            attr.classdef = typedef

            typedef.attributes[attr.name] = attr

        typedef.attributes = collections.OrderedDict(
            sorted(list(typedef.attributes.items()), key=lambda kv: not kv[1].required))
    else:
        raise NotImplementedError('Converting intermediate typedef to Python is not supported: {!r}'.format(
            type(intermediate_typedef)))

    typedef.description = intermediate_typedef.description
    typedef.identifier = intermediate_typedef.identifier

    assert typedef is not None

    return typedef


def to_typedefs(
        intermediate_typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> MutableMapping[str, Typedef]:
    """
    Translate type definitions from intermediate representation to Python.

    :param intermediate_typedefs: table of type definitions in intermediate representation
    :return: table of type definitions in Python representation
    """
    typedefs = collections.OrderedDict()  # type: MutableMapping[str, Typedef]

    for intermediate_typedef in intermediate_typedefs.values():
        assert intermediate_typedef is not None

        typedef = _to_typedef(intermediate_typedef=intermediate_typedef)
        typedefs[typedef.identifier] = typedef

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


@icontract.ensure(
    lambda result:
    sorted(result.parameters, key=id) == sorted([
        param
        for param in ([result.body_parameter] if result.body_parameter else []) +
                     result.query_parameters +
                     result.header_parameters +
                     result.path_parameters +
                     result.formdata_parameters +
                     result.file_parameters], key=id),
    enabled=icontract.SLOW)
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


# Jinja2 environment
_ENV = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, loader=jinja2.BaseLoader())
_ENV.filters.update({
    'comment': _comment,
    'docstring': _docstring,
    'snake_case': swagger_to.snake_case,
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
        return 'List[' + _type_expression(typedef=typedef.items, path=str(path) + '.items') + ']'
    elif isinstance(typedef, Dictdef):
        return 'Dict[str, ' + _type_expression(typedef=typedef.values, path=str(path) + '.values') + ']'
    elif isinstance(typedef, Classdef):
        if typedef.identifier == '':
            raise NotImplementedError(('Translating an anonymous class to a type expression '
                                       'is not supported: {}').format(path))

        return typedef.identifier
    else:
        raise NotImplementedError('Translating the typedef to a type expression is not supported: {!r}: {}'.format(
            type(typedef), path))


_CLASS_DEF_WO_ATTRIBUTES = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
{% if classdef.attributes %}{{ raise('Expected a classdef without attributes, but got some.') }}{% endif %}
class {{ classdef.identifier }}:
    {% if classdef.description %}
    {{ classdef.description|upper_first|docstring|indent }}

    {% endif %}
    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to {{ classdef.identifier|snake_case }}_to_jsonable.

        :return: a JSON-able representation
        """
        return {{ classdef.identifier|snake_case }}_to_jsonable(self)''')

_CLASS_DEF_WITH_ATTRIBUTES_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
{% if not classdef.attributes %}{{ raise('Expected a classdefinition with attributes, but got none.') }}{% endif %}
class {{ classdef.identifier }}:
    {% if classdef.description %}
    {{ classdef.description|upper_first|docstring|indent }}

    {% endif %}
    def __init__(
            self,
    {% for attr in classdef.attributes.values() %}
    {% if not attr.required %}
            {{ attr.name }}: Optional[{{ attribute_type[attr] }}] = None{{ ') -> None:' if loop.last else ',' }}
    {% else %}
            {{ attr.name }}: {{ attribute_type[attr] }}{{ ') -> None:' if loop.last else ',' }}
    {% endif %}{# /if not attr.required #}
    {% endfor %}{# /for attr #}
        """Initializes with the given values."""
        {% set newliner = joiner('SWITCH') %}
        {% for attr in classdef.attributes.values() %}
        {% if newliner() %}{{ '\\n' }}{% endif %}
        {% if attr.description %}
        {{ attr.description|comment|indent|indent }}
        {% endif %}
        self.{{ attr.name }} = {{ attr.name }}
        {% endfor %}

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to {{ classdef.identifier|snake_case }}_to_jsonable.

        :return: JSON-able representation
        """
        return {{ classdef.identifier|snake_case }}_to_jsonable(self)''')


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

    return _CLASS_DEF_WITH_ATTRIBUTES_TPL.render(
        classdef=classdef,
        attribute_type={
            attr: _type_expression(typedef=attr.typedef, path='{}.{}'.format(attr.classdef.identifier, attr.name))
            for attr in classdef.attributes.values()
        })


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
    elif isinstance(typedef, Classdef):
        return 'new_{}()'.format(swagger_to.snake_case(identifier=typedef.identifier))
    else:
        raise NotImplementedError('Translating the typedef to a default value is not supported: {}'.format(typedef))


_FACTORY_METHOD_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
def new_{{ classdef.identifier|snake_case }}() -> {{ classdef.identifier }}:
    """Generates an instance of {{ classdef.identifier }} with default values."""
    {% if not required_attributes %}
    return {{ classdef.identifier }}()
    {% else %}
    return {{ classdef.identifier }}(
        {% for attr in required_attributes %}
        {{ attr.name }}={{ default_value[attr] }}{{ ')' if loop.last else ',' }}
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
    return _FACTORY_METHOD_TPL.render(
        classdef=classdef,
        required_attributes=[attr for attr in classdef.attributes.values() if attr.required],
        default_value={attr: _default_value(typedef=attr.typedef)
                       for attr in classdef.attributes.values()}).strip()


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

    if exp == {{ classdef.identifier }}:
        return {{ classdef.identifier|snake_case }}_from_obj(obj, path=path)
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
        return 'list, {}'.format(_expected_type_expression(typedef=typedef.items))
    elif isinstance(typedef, Dictdef):
        return 'dict, {}'.format(_expected_type_expression(typedef=typedef.values))
    elif isinstance(typedef, Classdef):
        return typedef.identifier
    else:
        raise NotImplementedError('Translating the typedef to an expected type is not supported: {}'.format(typedef))


_CLASS_FROM_OBJ_TPL = _from_string_with_informative_exceptions(
    env=_ENV,
    text='''\
def {{ classdef.identifier|snake_case }}_from_obj(obj: Any, path: str = "") -> {{ classdef.identifier }}:
    """
    Generates an instance of {{ classdef.identifier }} from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of {{ classdef.identifier }}
    :param path: path to the object used for debugging
    :return: parsed instance of {{ classdef.identifier }}
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    {% if not classdef.attributes %}
    return {{ classdef.identifier }}()
    {% else %}
    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))
    {% for attr in classdef.attributes.values() %}

    {% if attr.required %}
    {{ attr.name }}_from_obj = from_obj(
        obj[{{ attr.name|repr }}],
        expected=[{{ expected_type_expression[attr] }}],
        path=path + {{ '.%s'|format(attr.name)|repr }})  # type: {{ type_expression[attr] }}
    {% else %}
    if {{ attr.name|repr }} in obj:
        {{ attr.name }}_from_obj = from_obj(
            obj[{{ attr.name|repr }}],
            expected=[{{ expected_type_expression[attr] }}],
            path=path + {{ '.%s'|format(attr.name)|repr }})  # type: Optional[{{ type_expression[attr] }}]
    else:
        {{ attr.name }}_from_obj = None
    {% endif %}{# /if attr.required #}
    {% endfor %}{# /for attr in classdef.attributes.values() #}

    return {{ classdef.identifier }}(
    {% for attr in classdef.attributes.values() %}
        {{ attr.name }}={{ attr.name }}_from_obj{{ ')' if loop.last else ',' }}
    {% endfor %}{# /for attr in classdef.attributes.values() #}
    {% endif %}{# /if not classdef.attributes #}''')


@icontract.ensure(lambda result: not result.endswith('\n'))
def _generate_class_from_obj(classdef: Classdef) -> str:
    """
    Generate the code of the ``{class}_from_obj`` function that parses the JSON-ed object to an instance of a class.

    :param classdef: class definition in Python representation
    :return: Python code
    """
    return _CLASS_FROM_OBJ_TPL.render(
        classdef=classdef,
        expected_type_expression={
            attr: _expected_type_expression(typedef=attr.typedef)
            for attr in classdef.attributes.values()
        },
        type_expression={
            attr: _type_expression(typedef=attr.typedef, path=attr.classdef.identifier + '.' + attr.name)
            for attr in classdef.attributes.values()
        }).strip()


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

    if exp == {{ classdef.identifier }}:
        assert isinstance(obj, {{ classdef.identifier }})
        return {{ classdef.identifier|snake_case }}_to_jsonable(obj, path=path)
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
def {{ classdef.identifier|snake_case }}_to_jsonable(
        {{ classdef.identifier|snake_case }}: {{ classdef.identifier }},
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of {{ classdef.identifier }}.

    :param {{ classdef.identifier|snake_case }}: instance of {{ classdef.identifier }} to be JSON-ized
    :param path: path to the {{ classdef.identifier|snake_case }} used for debugging
    :return: a JSON-able representation
    """
    {% if not classdef.attributes %}
    return dict()
    {% else %}
    res = dict()  # type: Dict[str, Any]
    {% for attr in classdef.attributes.values() %}

    {% set assignment %}
{% if is_primitive[attr] %}
res[{{ attr.name|repr }}] = {{ classdef.identifier|snake_case }}.{{ attr.name }}
{% else %}
res[{{ attr.name|repr }}] = to_jsonable(
    {{ classdef.identifier|snake_case }}.{{ attr.name }},
    expected=[{{ expected_type_expression[attr] }}],
    path={{ '{}.%s'|format(attr.name)|repr }}.format(path))
{% endif %}{# /if is_primitive[attr] #}
    {% endset %}{# /set assignment #}
    {% if not attr.required %}
    if {{ classdef.identifier|snake_case }}.{{ attr.name }} is not None:
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
    return _CLASS_TO_JSONABLE_TPL.render(
        classdef=classdef,
        is_primitive={
            attr: isinstance(attr.typedef, (Booldef, Intdef, Floatdef, Strdef))
            for attr in classdef.attributes.values()
        },
        expected_type_expression={
            attr: _expected_type_expression(typedef=attr.typedef)
            for attr in classdef.attributes.values()
        }).strip()


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
:param {{ param.identifier }}:
{% else %}
{% if '\\n' in param.description %}
:param {{ param.identifier }}:
    {{ param.description|indent }}
{% else %}
:param {{ param.identifier }}: {{ param.description }}
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
def {{ request.operation_id}}(self) -> {{ return_type }}:
{% else %}
{% set suffix = ') -> %s:'|format(return_type) %}
def {{ request.operation_id}}(
        self,
        {% for param in request.parameters %}
        {% if not param.required %}
        {{ param.identifier }}: Optional[{{ type_expression[param] }}] = None{{ suffix if loop.last else ',' }}
        {% else %}
        {{ param.identifier }}: {{ type_expression[param] }}{{ suffix if loop.last else ',' }}
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
headers[{{ param.name|repr }}] = {{ param.identifier }}
                {% elif is_primitive[param] %}
headers[{{ param.name|repr }}] = json.dumps({{ param.identifier }})
                {% else %}
headers[{{ param.name|repr }}] = json.dumps(
    to_jsonable(
        {{ param.identifier }},
        expected=[{{ expected_type_expression[param] }}]))
                {% endif %}{# /if is_primitive[param] #}
            {% endset %}
            {% if param.required %}
    {{ set_header_item|trim|indent }}
            {% else %}
    if {{ param.identifier }} is not None:
        {{ set_header_item|trim|indent|indent }}
            {% endif %}{# /if param.required #}
        {% endfor %}{# /for param in request.header_parameters #}
    {% endif %}{# /if request.header_parameters #}
    {% if request.query_parameters %}{### Query parameters ###}

    params = {}  # type: Dict[str, str]
        {% for param in request.query_parameters %}

            {% set set_params_item %}
                {% if is_str[param] %}
params[{{ param.name|repr }}] = {{ param.identifier }}
                {% elif is_primitive[param] %}
params[{{ param.name|repr }}] = json.dumps({{ param.identifier }})
                {% else %}
params[{{ param.name|repr }}] = json.dumps(
    to_jsonable(
        {{ param.identifier }},
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
data = {{ request.body_parameter.identifier }}
        {% else %}
data = to_jsonable(
    {{ request.body_parameter.identifier }},
    expected=[{{ expected_type_expression[request.body_parameter] }}])
        {% endif %}{# /is_primitive[request.body_parameter] #}
    {% endset %}
    {% if request.body_parameter.required %}
    {{ set_body|indent }}
    {% else %}
    data = None  # type: Optional[Any]
    if {{ request.body_parameter.identifier }} != None:
        {{ set_body|trim|indent|indent }}
    {% endif %}{# /if request.body_parameter.required #}
    {% endif %}{# /if request.body_parameter #}
    {% if request.formdata_parameters %}{### Form-data parameters ###}

    data = {}  # type: Dict[str, str]
    {% for param in request.formdata_parameters %}

        {% set set_data_item %}
            {% if is_str[param] %}
data[{{ param.name|repr }}] = {{ param.identifier }}
            {% elif is_primitive[param] %}
data[{{ param.name|repr }}] = json.dumps({{ param.identifier }})
            {% else %}
data[{{ param.name|repr }}] = json.dumps(
    to_jsonable(
        {{ param.identifier}},
        expected=[{{ expected_type_expression[param] }}]))
            {% endif %}{# /if is_primitive[param] #}
        {% endset %}
        {% if param.required %}
    {{ set_data_item|trim|indent|indent }}
        {% else %}
    if {{ param.identifier }} is not None:
        {{ set_data_item|trim|indent|indent }}
        {% endif %}{# /if param.required #}
    {% endfor %}{# /for param in request.formdata_parameters #}
    {% endif %}{# /if request.formdata_parameters #}
    {% if request.file_parameters %}{### File parameters ###}

    files = {}  # type: Dict[str, BinaryIO]
        {% for param in request.file_parameters %}

            {% if param.required %}
    files[{{ param.name|repr }}] = {{ param.identifier }}
            {% else %}
    if {{ param.identifier }} is not None:
        files[{{ param.name|repr }}] = {{ param.identifier }}
            {% endif %}{# /if param.required #}
        {% endfor %}{# /for param in request.file_parameters #}
    {% endif %}{# /if request.file_parameters #}

    {% if not request.parameters %}
    resp = requests.request(method={{ request.method|repr }}, url=url)
    {% else %}
    resp = requests.request(
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
        auth=self.auth)
    {% endif %}{# /if not request.parameters #}

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

    expected_type_expression = {
        param: _expected_type_expression(typedef=param.typedef)
        for param in request.parameters if not isinstance(param.typedef, Filedef)
    }  # type: Dict[Union[Parameter, Response], str]

    if return_type not in ['bytes', 'MutableMapping[str, Any]']:
        expected_type_expression[resp] = _expected_type_expression(typedef=resp.typedef)

    ##
    # Render
    ##

    return _REQUEST_FUNCTION_TPL.render(
        request=request,
        return_type=return_type,
        resp=resp,
        request_docstring=request_docstring,
        type_expression={
            param: _type_expression(typedef=param.typedef, path='{}.{}'.format(request.operation_id, param.name))
            for param in request.parameters
        },
        path_tokens=path_tokens,
        is_str={param: isinstance(param.typedef, Strdef)
                for param in request.parameters},
        is_primitive={
            param: isinstance(param.typedef, (Booldef, Intdef, Floatdef, Strdef))
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
from typing import Any, BinaryIO, Dict, List, MutableMapping, Optional

import requests
import requests.auth
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

    def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth
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

    assert len(set(classdefs)) == len(classdefs), \
        'All class definitions in Python representation are expected to be unique.'

    return _CLIENT_PY.render(
        service_name=service_name,
        classdefs=classdefs,
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
