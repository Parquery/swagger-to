#!/usr/bin/env python3
"""Generate server stubs from Swagger specification in Go."""

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches
# pylint: disable=too-many-statements, too-many-lines

from typing import MutableMapping, Union, Set, List, Optional, Mapping, Iterable, Tuple  # pylint: disable=unused-import

import collections
import icontract
import jinja2

import swagger_to
import swagger_to.indent
import swagger_to.intermediate
import swagger_to.swagger


class JsonSchema:
    """Represent a JSON validation schema."""

    def __init__(self):
        """Initialize with default values."""
        self.identifier = ''
        self.text = ''


def _to_json_schema(intermediate_schema: swagger_to.intermediate.JsonSchema) -> JsonSchema:
    """
    Convert the intermediate schema to a representation that we can use to easily generate go code.

    :param intermediate_schema: intermediate representation of a JSON schema
    :return: representation suitable for generation of Go code
    """
    schema = JsonSchema()
    schema.identifier = intermediate_schema.identifier
    schema.text = intermediate_schema.text

    return schema


class Typedef:
    """Represent a type definition such that it's suitable for generation of Go code."""

    def __init__(self):
        """Initialize with default values."""
        self.identifier = ''
        self.description = ''
        self.json_schema = None  # type: Union[None, JsonSchema]


class Fielddef:
    """Represent a field definition of a struct suitable for generation of Go code."""

    def __init__(self):
        """Initialize with default values."""
        self.typedef = None  # type: Union[None, Typedef]
        self.description = ''
        self.json_name = ''
        self.name = ''


class Structdef(Typedef):
    """Represent a struct type."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.fields = collections.OrderedDict()  # type: MutableMapping[str, Fielddef]
        self.required = []  # type: List[str]


class Arraydef(Typedef):
    """Represent an array type."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.items = None  # type: Union[None, Typedef]


class Mapdef(Typedef):
    """Represent a map type."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.values = None  # type: Union[None, Typedef]


class Pointerdef(Typedef):
    """Represent a pointer type."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.pointed = None  # type: Union[None, Typedef]


class Primitivedef(Typedef):
    """Represent a primitive type."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.type = ''


def _to_typedef(intermediate_typedef: swagger_to.intermediate.Typedef) -> Typedef:
    """Convert intermediate type definition into a type definition suitable for Go code generation."""
    typedef = None  # type: Union[None, Typedef]

    if isinstance(intermediate_typedef, swagger_to.intermediate.Primitivedef):
        typedef = Primitivedef()

        if intermediate_typedef.type == 'string':
            if intermediate_typedef.format == 'date-time':
                typedef.type = 'time.Time'
            else:
                typedef.type = 'string'
        elif intermediate_typedef.type == 'number':
            if intermediate_typedef.format == '':
                typedef.type = 'float64'
            elif intermediate_typedef.format == 'float':
                typedef.type = 'float32'
            elif intermediate_typedef.format == 'double':
                typedef.type = 'float64'
            else:
                raise ValueError("Unexpected format {!r} for type {!r}".format(intermediate_typedef.format,
                                                                               intermediate_typedef.type))

        elif intermediate_typedef.type == 'integer':
            if intermediate_typedef.format == '':
                typedef.type = 'int'
            elif intermediate_typedef.format == 'int32':
                typedef.type = 'int32'
            elif intermediate_typedef.format == 'int64':
                typedef.type = 'int64'
            else:
                raise ValueError("Unexpected format {!r} for type {!r}".format(intermediate_typedef.format,
                                                                               intermediate_typedef.type))

        elif intermediate_typedef.type == 'boolean':
            typedef.type = 'bool'

        else:
            raise NotImplementedError(
                "Unhandled translation of a primitive intermediate type to Go with 'type': {!r}".format(
                    intermediate_typedef.type))

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Arraydef):
        if intermediate_typedef.items is None:
            raise ValueError("Unexpected intermediate type definition of an array to have items None: {!r}".format(
                intermediate_typedef.identifier))

        typedef = Arraydef()
        typedef.items = _to_typedef(intermediate_typedef=intermediate_typedef.items)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Mapdef()
        typedef.values = _to_typedef(intermediate_typedef=intermediate_typedef.values)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Structdef()

        for propdef in intermediate_typedef.properties.values():
            field = Fielddef()

            field_typedef = _to_typedef(intermediate_typedef=propdef.typedef)
            if not propdef.name in intermediate_typedef.required and isinstance(field_typedef, Primitivedef):
                optional_field_typedef = Pointerdef()
                optional_field_typedef.pointed = field_typedef
                field_typedef = optional_field_typedef

            field.typedef = field_typedef
            field.description = propdef.description
            field.json_name = propdef.name
            field.name = swagger_to.capital_camel_case(identifier=propdef.name)

            typedef.fields[field.name] = field

            if propdef.name in intermediate_typedef.required:
                typedef.required.append(field.name)

    else:
        raise NotImplementedError("Unhandled translation of an intermediate type to Go: {!r}".format(
            type(intermediate_typedef)))

    assert typedef is not None

    if intermediate_typedef.identifier != '':
        typedef.identifier = swagger_to.capital_camel_case(identifier=intermediate_typedef.identifier)

    typedef.description = intermediate_typedef.description

    typedef.json_schema = _to_json_schema(intermediate_schema=intermediate_typedef.json_schema)

    return typedef


@icontract.ensure(lambda result: all(key == typedef.identifier for key, typedef in result.items()))
def to_typedefs(
        intermediate_typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> MutableMapping[str, Typedef]:
    """Convert a table of intermediate type representations to a table of type definitions for generation of Go code."""
    typedefs = collections.OrderedDict()  # type: MutableMapping[str, Typedef]

    for intermediate_typedef in intermediate_typedefs.values():
        assert intermediate_typedef is not None

        typedef = _to_typedef(intermediate_typedef=intermediate_typedef)
        typedefs[typedef.identifier] = typedef

    return typedefs


# yapf: disable
@icontract.ensure(
    lambda intermediate_typedef, result:
    intermediate_typedef.identifier == '' or result.identifier == intermediate_typedef.identifier)
@icontract.ensure(
    lambda intermediate_typedef, result:
    intermediate_typedef.identifier != '' or result.identifier == '')
# yapf: enable
def _anonymous_or_get_typedef(intermediate_typedef: swagger_to.intermediate.Typedef,
                              typedefs: MutableMapping[str, Typedef]) -> Typedef:
    """Create an anonymous type definition or retrieve the type definition from the existing definition table."""
    if intermediate_typedef.identifier != '':
        identifier = swagger_to.capital_camel_case(identifier=intermediate_typedef.identifier)

        if not identifier in typedefs:
            raise ValueError("Undefined Go type for intermediate typedef {!r}: {!r}".format(
                intermediate_typedef.identifier, identifier))

        return typedefs[identifier]

    return _to_typedef(intermediate_typedef=intermediate_typedef)


def _walk(typedef: Typedef, parent: Optional[Typedef] = None) -> Iterable[Tuple[Optional[Typedef], Typedef]]:
    """Walk the tree of nested type definitions as (nesting type definition, nested type definition)."""
    yield parent, typedef

    if isinstance(typedef, Primitivedef):
        pass

    elif isinstance(typedef, Pointerdef):
        yield from _walk(typedef=typedef.pointed, parent=typedef)

    elif isinstance(typedef, Arraydef):
        yield from _walk(typedef=typedef.items, parent=typedef)

    elif isinstance(typedef, Mapdef):
        yield from _walk(typedef=typedef.values, parent=typedef)

    elif isinstance(typedef, Structdef):
        for fielddef in typedef.fields.values():
            yield from _walk(typedef=fielddef.typedef, parent=typedef)

    else:
        raise NotImplementedError("_walk for Go type definition of type: {}".format(type(typedef)))


class Argument:
    """Represent an argument of a handler implementation."""

    def __init__(self):
        """Initialize with default values."""
        self.typedef = None  # type: Union[None, Typedef]
        self.identifier = ''
        self.in_what = ''

        # Original name of the endpoint parameter
        self.parameter_name = ''

        self.required = False
        self.parsing_identifier = ''
        self.json_schema = None  # type: Optional[JsonSchema]


class Handler:
    """Represent a handler interface of an endpoint."""

    def __init__(self):
        """Initialize with default values."""
        self.identifier = ''
        self.arguments = []  # type: List[Argument]


class Wrapper:
    """Represent a wrapper that parses the arguments from a request and forwards them to the handler."""

    def __init__(self):
        """Initialize with default values."""
        self.identifier = ''
        self.handler = None  # type: Union[None, Handler]

        self.header_arguments = []  # type: List[Argument]
        self.query_arguments = []  # type: List[Argument]
        self.path_arguments = []  # type: List[Argument]
        self.body_argument = None  # type: Union[None, Argument]


class Route:
    """Represent a muxing route to an endpoint."""

    def __init__(self):
        """Initialize with default values."""
        self.description = ''
        self.path = ''
        self.method = ''
        self.wrapper = Wrapper()
        self.handler = Handler()


def _endpoint_to_route_path(endpoint: swagger_to.intermediate.Endpoint) -> str:
    """
    Convert an endpoint path to Gorrila Mux route path.

    :param endpoint: whose path we need to convert
    :return: Gorrila Mux route path
    """
    token_pth = swagger_to.tokenize_path(path=endpoint.path)

    tkns = token_pth.tokens[:]

    for param in endpoint.parameters:
        if param.in_what != 'path':
            continue

        if param.name not in token_pth.parameter_to_token_indices:
            continue

        if not isinstance(param.typedef, swagger_to.intermediate.Primitivedef):
            raise ValueError("Expected path parameter {!r} in the path {!r} to be primitive, but got: {!r}".format(
                param.name, endpoint.path, type(param.typedef)))

        assert isinstance(param.typedef, swagger_to.intermediate.Primitivedef)
        if param.typedef.pattern != '':
            param_in_route = '{' + param.name + ":" + param.typedef.pattern + "}"
        else:
            param_in_route = '{' + param.name + '}'

        for i in token_pth.parameter_to_token_indices[param.name]:
            tkns[i] = param_in_route

    return "".join(tkns)


def _to_route(endpoint: swagger_to.intermediate.Endpoint, typedefs: MutableMapping[str, Typedef]) -> Route:
    """
    Convert an intermediate representation of an endpoint to a muxing route of Go server stub.

    :param endpoint: intermediate representation of an endpoint
    :param typedefs: table of type definitions
    :return: converted route
    """
    route = Route()
    route.method = endpoint.method.lower()
    route.path = _endpoint_to_route_path(endpoint=endpoint)
    route.description = endpoint.description

    ##
    # Determine handable parameters
    ##
    handable_parameters = []  # type: List[swagger_to.intermediate.Parameter]

    for param in endpoint.parameters:
        # Assert that we can handle all the supplied parameters.
        if param.in_what == 'formData':
            # No code is generated for the parameters in the form data since there are so many edge cases
            # which we possibly can't cover.
            continue
        elif param.in_what in ['query', 'body', 'path', 'header']:
            handable_parameters.append(param)
        else:
            raise NotImplementedError(
                "Handling of parameters in {} is not implemented yet: endpoint {} {}, parameter {}.".format(
                    param.in_what, endpoint.path, endpoint.method, param.name))

    ##
    # Generate identifiers corresponding to the parameters.
    ##

    param_to_identifier = {param: swagger_to.camel_case(identifier=param.name) for param in handable_parameters}

    # Add the location as prefix if the argument identifiers overlap
    identifiers = list(param_to_identifier.values())
    needs_location_prefix = len(set(identifiers)) != len(identifiers)
    if needs_location_prefix:
        param_to_identifier = {
            param: swagger_to.camel_case(identifier="{}_{}".format(param.in_what, param.name))
            for param in endpoint.parameters
        }

        ##
        # Assert that there are no conflicts at this point
        ##

        by_identifier = collections.defaultdict(
            list)  # type: MutableMapping[str, List[swagger_to.intermediate.Parameter]]
        for param, identifier in param_to_identifier.items():
            by_identifier[identifier].append(param)

        # yapf: disable
        msgs = [
            "in the endpoint {} {} for the identifier {!r}: {}".format(
                endpoint.method.upper(), endpoint.path, identifier, ", ".join(
                    ["{} in {}".format(param.name, param.in_what) for param in params]))
            for identifier, params in by_identifier.items()
            if len(params) > 1
        ]
        # yapf: enable

        if len(msgs) > 0:
            raise ValueError("There are conflicting identifiers for parameters:\n{}".format("\n".join(msgs)))

    ##
    # Convert parameters to arguments
    ##

    assert all(param in param_to_identifier for param in handable_parameters), \
        "Expected all parameters to have a generated argument identifier."

    for param in handable_parameters:
        identifier = param_to_identifier[param]

        argument = Argument()
        argument.typedef = _anonymous_or_get_typedef(intermediate_typedef=param.typedef, typedefs=typedefs)
        argument.required = param.required

        if not param.required and isinstance(argument.typedef, Primitivedef):
            pointer_typedef = Pointerdef()
            pointer_typedef.identifier = argument.typedef.identifier
            pointer_typedef.description = argument.typedef.description
            pointer_typedef.pointed = argument.typedef

            argument.typedef = pointer_typedef

        argument.parameter_name = param.name
        argument.identifier = identifier
        argument.in_what = param.in_what
        argument.parsing_identifier = swagger_to.camel_case(identifier='a_' + identifier)

        if param.json_schema is not None:
            argument.json_schema = _to_json_schema(intermediate_schema=param.json_schema)

        if argument.in_what == 'header':
            route.wrapper.header_arguments.append(argument)

        elif argument.in_what == 'query':
            route.wrapper.query_arguments.append(argument)

        elif argument.in_what == 'body':
            route.wrapper.body_argument = argument

        elif argument.in_what == 'path':
            route.wrapper.path_arguments.append(argument)

        else:
            raise AssertionError("Unexpected argument given in: {}".format(argument.in_what))

        route.handler.arguments.append(argument)

    ##
    # Determine route attributes
    ##

    route.wrapper.identifier = swagger_to.capital_camel_case(identifier='wrap_' + endpoint.operation_id)
    route.wrapper.handler = route.handler
    route.handler.identifier = swagger_to.capital_camel_case(identifier=endpoint.operation_id)

    return route


def to_routes(endpoints: List[swagger_to.intermediate.Endpoint], typedefs: MutableMapping[str, Typedef]) -> List[Route]:
    """
    Convert the intermediate representation of endpoints to muxing routes of a Go server stub.

    :param endpoints: intermediate representation of endpoints
    :param typedefs: table of type definitions
    :return: muxing routes of a Go server stub
    """
    routes = []  # type: List[Route]
    for endpoint in endpoints:
        routes.append(_to_route(endpoint=endpoint, typedefs=typedefs))

    return routes


@icontract.ensure(lambda result: not result.endswith('\n'))
def _comment(text: str) -> str:
    r"""
    Genearates a (possibly multi-line) comment from the text.

    >>> cmt = _comment("  testme\n  \nagain\n")
    >>> assert cmt == '//   testme\n//\n// again\n//'

    :param text: of the comment
    :return: Go code
    """
    out = []  # type: List[str]
    lines = text.split('\n')
    for line in lines:
        rstripped = line.rstrip()
        if len(rstripped) > 0:
            out.append('// {}'.format(rstripped))
        else:
            out.append('//')

    return '\n'.join(out)


@icontract.ensure(lambda result: result.startswith('"'))
@icontract.ensure(lambda result: result.endswith('"'))
def _escaped_str(text: str) -> str:
    """Escape the text and returns it as a valid Golang string."""
    return '"{}"'.format(
        text.replace('\\', '\\\\').replace('"', '\\"').replace('\a', '\\a').replace('\f', '\\f').replace('\t', '\\t')
        .replace('\n', '\\n').replace('\r', '\\r').replace('\v', '\\v'))


# Jinja2 environment
ENV = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, loader=jinja2.BaseLoader())
ENV.filters.update({
    'capital_camel_case': swagger_to.capital_camel_case,
    'comment': _comment,
    'escaped_str': _escaped_str
})

ENV.globals.update({'is_pointerdef': lambda typedef: isinstance(typedef, Pointerdef)})

_STRUCT_TPL = ENV.from_string('''\
struct {
{% for fielddef in typedef.fields.values() %}
{% if not loop.first %}


{% endif %}
{% if fielddef.description %}
    {{ fielddef.description|comment|indent }}
{% endif %}
{% set json_tags = fielddef.json_name %}
{% if fielddef.name not in typedef.required %}
{% set json_tags = json_tags + ',omitempty' %}
{% endif %}
    {{ fielddef.name }} {{ field_type[fielddef] }} `json:{{ json_tags|escaped_str }}`{% if loop.last %}}{% endif %}
{% endfor %}
''')


@icontract.ensure(lambda result: result == result.strip())
def _express_type(typedef: Typedef) -> str:
    """Express the type in Golang corresponding to the type definition."""
    if isinstance(typedef, Primitivedef):
        return typedef.type

    if isinstance(typedef, Pointerdef):
        return "*{}".format(_express_or_identify_type(typedef.pointed))

    if isinstance(typedef, Arraydef):
        return "[]{}".format(_express_or_identify_type(typedef.items))

    if isinstance(typedef, Mapdef):
        return "map[string]{}".format(_express_or_identify_type(typedef.values))

    if isinstance(typedef, Structdef):
        if len(typedef.fields) == 0:
            return "struct {}"

        return _STRUCT_TPL.render(
            typedef=typedef,
            field_type={fielddef: _express_or_identify_type(fielddef.typedef)
                        for fielddef in typedef.fields.values()}).strip()

    else:
        raise NotImplementedError("No Go type writing defined for typedef of type: {!r}".format(type(typedef)))


@icontract.ensure(lambda result: result == result.strip())
def _express_or_identify_type(typedef: Typedef) -> str:
    """Give the type identifier or expresses the type if the typedef lacks an identifier."""
    if typedef.identifier != '':
        return typedef.identifier

    return _express_type(typedef=typedef)


@icontract.require(lambda typedef: typedef.identifier != '')
@icontract.ensure(lambda result: result == result.strip())
def _define_type(typedef: Typedef) -> str:
    """Define the type in Golang code."""
    return 'type {} {}'.format(typedef.identifier, _express_type(typedef=typedef))


_IMPORTS_TPL = ENV.from_string('''\
{% if imports|length == 0 %}
{% elif imports|length == 1 %}
import "{{ imports[0] }}"{#
#}{% else %}
import (
{% for imprt in imports %}
    "{{ imprt }}"
{% endfor %}
){% endif %}''')


@icontract.ensure(lambda result: not result.endswith('\n'))
@icontract.ensure(lambda import_set, result: len(import_set) != 0 or result == '')
def _state_imports(import_set: Set[str]) -> str:
    """State the imports in Golang code."""
    return _IMPORTS_TPL.render(imports=sorted(import_set))


_TYPES_GO_TPL = ENV.from_string('''\
package {{ package }}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
{% if imports_code != '' %}

{{ imports_code }}
{% endif %}
{% for typedef in typedefs.values() %}

{% if typedef.description != '' %}
{{ '%s %s'|format(typedef.identifier, typedef.description)|comment }}
{% endif %}
type {{ typedef.identifier }} {{ type_expression[typedef] }}
{% endfor %}

''')


@icontract.ensure(lambda result: result.endswith('\n'), "final newline")
def generate_types_go(package: str, typedefs: Mapping[str, Typedef]) -> str:
    """
    Generate a file which defines all the involved types.

    :param package: name of the package
    :param typedefs: type definitions
    :return: Golang code
    """
    # imports
    import_set = set()  # type: Set[str]
    for typedef in typedefs.values():
        for _, another_typedef in _walk(typedef=typedef, parent=None):
            if isinstance(another_typedef, Primitivedef):
                if another_typedef.type == 'time.Time':
                    import_set.add('time')

    text = _TYPES_GO_TPL.render(
        package=package,
        imports_code=_state_imports(import_set=import_set),
        typedefs=typedefs,
        type_expression={typedef: _express_type(typedef)
                         for typedef in typedefs.values()})

    return swagger_to.indent.reindent(text=text, indention='\t')


_STRING_ARGUMENT_FROM_STRING_TPL = ENV.from_string('''\
{% if is_pointerdef(argument.typedef) %}
val := {{ string_identifier }}
{{ target_identifier }} = &val{#
#}{% else %}
{{ target_identifier }} = {{ string_identifier }}{#
#}{% endif %}''')

_INT_ARGUMENT_FROM_STRING_TPL = ENV.from_string('''\
{
    parsed, err := strconv.ParseInt({{ string_identifier }}, 10, 64)
    if err != nil {
{% set msg = "Parameter '%s': "|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}+err.Error(), http.StatusBadRequest)
        return
    }
    converted := int(parsed)
{% if is_pointerdef(argument.typedef) %}
    {{ target_identifier }} = &converted
{% else %}
    {{ target_identifier }} = converted
{% endif %}
}''')

_INT64_ARGUMENT_FROM_STRING_TPL = ENV.from_string('''\
{
    parsed, err := strconv.ParseInt({{ string_identifier }}, 10, 64)
    if err != nil {
{% set msg = "Parameter '%s': "|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}+err.Error(), http.StatusBadRequest)
        return
    }
    converted := int64(parsed)
{% if is_pointerdef(argument.typedef) %}
    {{ target_identifier }} = &converted
{% else %}
    {{ target_identifier }} = converted
{% endif %}
}''')

_INT32_ARGUMENT_FROM_STRING_TPL = ENV.from_string('''\
{
    parsed, err := strconv.ParseInt({{ string_identifier }}, 10, 32)
    if err != nil {
{% set msg = "Parameter '%s': "|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}+err.Error(), http.StatusBadRequest)
        return
    }
    converted := int32(parsed)
{% if is_pointerdef(argument.typedef) %}
    {{ target_identifier }} = &converted
{% else %}
    {{ target_identifier }} = converted
{% endif %}
}''')

_FLOAT32_ARGUMENT_FROM_STRING_TPL = ENV.from_string('''\
{
    parsed, err := strconv.ParseFloat({{ string_identifier }}, 32)
    if err != nil {
{% set msg = "Parameter '%s': "|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}+err.Error(), http.StatusBadRequest)
        return
    }
    converted := float32(parsed)
{% if is_pointerdef(argument.typedef) %}
    {{ target_identifier }} = &converted
{% else %}
    {{ target_identifier }} = converted
{% endif %}
}''')

_FLOAT64_ARGUMENT_FROM_STRING_TPL = ENV.from_string('''\
{
    parsed, err := strconv.ParseFloat({{ string_identifier }}, 64)
    if err != nil {
{% set msg = "Parameter '%s': "|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}+err.Error(), http.StatusBadRequest)
        return
    }
    converted := float64(parsed)
{% if is_pointerdef(argument.typedef) %}
    {{ target_identifier }} = &converted
{% else %}
    {{ target_identifier }} = converted
{% endif %}
}''')


@icontract.require(lambda string_identifier: string_identifier == string_identifier.strip())
@icontract.ensure(lambda result: not result.endswith('\n'))
def _argument_from_string(argument: Argument, string_identifier: str) -> str:
    """Generate the code to parse an argument from a string."""
    target_identifier = argument.parsing_identifier

    tajp = ''
    if isinstance(argument.typedef, Primitivedef):
        tajp = argument.typedef.type

    elif isinstance(argument.typedef, Pointerdef):
        if isinstance(argument.typedef.pointed, Primitivedef):
            tajp = argument.typedef.pointed.type
    else:
        raise NotImplementedError("Parsing argument from string {!r} of type: {!r}".format(
            string_identifier, type(argument)))

    assert tajp != '', 'Expected tajp to be set in the previous execution path.'

    if tajp == 'string':
        return _STRING_ARGUMENT_FROM_STRING_TPL.render(
            argument=argument, string_identifier=string_identifier, target_identifier=target_identifier)

    elif tajp == 'int':
        return _INT_ARGUMENT_FROM_STRING_TPL.render(
            argument=argument, string_identifier=string_identifier, target_identifier=target_identifier)

    elif tajp == 'int64':
        return _INT64_ARGUMENT_FROM_STRING_TPL.render(
            argument=argument, string_identifier=string_identifier, target_identifier=target_identifier)

    elif tajp == 'int32':
        return _INT32_ARGUMENT_FROM_STRING_TPL.render(
            argument=argument, string_identifier=string_identifier, target_identifier=target_identifier)

    elif tajp == 'float32':
        return _FLOAT32_ARGUMENT_FROM_STRING_TPL.render(
            argument=argument, string_identifier=string_identifier, target_identifier=target_identifier)

    elif tajp == 'float64':
        return _FLOAT64_ARGUMENT_FROM_STRING_TPL.render(
            argument=argument, string_identifier=string_identifier, target_identifier=target_identifier)

    else:
        raise NotImplementedError("Parsing argument from string {!r} of Go type: {!r}".format(string_identifier, tajp))


_ARGUMENT_FROM_BODY_TPL = ENV.from_string('''\
{
    var err error
    r.Body = http.MaxBytesReader(w, r.Body, 1024*1024)
    body, err := ioutil.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "Body unreadable: "+err.Error(), http.StatusBadRequest)
        return
    }

    err = ValidateAgainst{{ argument.json_schema.identifier|capital_camel_case }}Schema(body)
    if err != nil {
        http.Error(w, "Failed to validate against schema: "+err.Error(), http.StatusBadRequest)
        return
    }

    err = json.Unmarshal(body, &{{ argument.parsing_identifier }})
    if err != nil {
{% set msg = "Error JSON-decoding body parameter '%s': "|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}+err.Error(),
            http.StatusBadRequest)
        return
    }
}''')


@icontract.ensure(lambda result: not result.endswith('\n'))
def _argument_from_body(argument: Argument) -> str:
    """Generate the code to parse the argument from a request body."""
    return _ARGUMENT_FROM_BODY_TPL.render(argument=argument)


_WRAPPER_TPL = ENV.from_string('''\
{% set newliner = joiner("XXX") %}
{% set description %}
{{ route.wrapper.identifier }} wraps the path `{{ route.path }}` with the method "{{ route.method }}".
{% if route.description %}

Path description:
{{ route.description }}
{% endif %}
{% endset %}{# /set description #}
{{ description|trim|comment }}
func {{ route.wrapper.identifier }}(h Handler, w http.ResponseWriter, r *http.Request) {
{% if route.handler.arguments %}{# intermediate variables #}
{% if newliner() %}{{ '\n' }}{% endif %}
{% for argument in route.handler.arguments %}
    var {{ argument.parsing_identifier }} {{ express_or_identify_type[argument]|indent|indent }}
{% endfor %}{# /for argument in route.handler.arguments #}
{% endif %}{# /if intermediate variables #}
{% if route.wrapper.header_arguments %}{### Header arguments ###}
    {% if newliner() %}{{ '\n' }}{% endif %}
    hdr := r.Header
    {% for argument in route.wrapper.header_arguments %}

    {% if argument.required %}
    if _, ok := hdr[{{ argument.parameter_name|escaped_str }}]; !ok {
        {% set msg = "Parameter '%s' expected in header"|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}, http.StatusBadRequest)
        return
    }
    {{ argument_from_string(
        argument, "hdr.Get(%s)"|format(argument.parameter_name|escaped_str))|indent }}
    {% else %}
    if _, ok := hdr[{{ argument.parameter_name|escaped_str }}]; ok {
        {{ argument_from_string(
            argument, "hdr.Get(%s)"|format(argument.parameter_name|escaped_str))|indent|indent }}
    }
    {% endif %}{# /if argument.required #}
    {% endfor %}{# /for argument in route.wrapper.header_arguments #}
{% endif %}{# /if header arguments #}
{% if route.wrapper.query_arguments %}{### Query arguments ###}
    {% if newliner() %}{{ '\n' }}{% endif %}
    q := r.URL.Query()
    {% for argument in route.wrapper.query_arguments %}

    {% if argument.required %}
    if _, ok := q[{{ argument.parameter_name|escaped_str }}]; !ok {
        {% set msg = "Parameter '%s' expected in query"|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}, http.StatusBadRequest)
        return
    }
    {{ argument_from_string(
        argument, "q.Get(%s)"|format(argument.parameter_name|escaped_str))|indent }}
    {% else %}
    if _, ok := q[{{ argument.parameter_name|escaped_str }}]; ok {
        {{ argument_from_string(
            argument, "q.Get(%s)"|format(argument.parameter_name|escaped_str))|indent|indent }}
    }
    {% endif %}{# /if argument.required #}
    {% endfor %}{# /for query arguments #}
{% endif %}{# /if query arguments #}
{% if route.wrapper.path_arguments %}{### Path arguments ###}
    {% if newliner() %}{{ '\n' }}{% endif %}
    vars := mux.Vars(r)
    {% for argument in route.wrapper.path_arguments %}

    {% if argument.required %}
    if _, ok := vars[{{ argument.parameter_name|escaped_str }}]; !ok {
    {% set msg = "Parameter '%s' expected in path"|format(argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}, http.StatusBadRequest)
        return
    }
    {{ argument_from_string(argument, "vars[%s]"|format(argument.parameter_name|escaped_str))|indent }}
    {% else %}
    if value, ok := vars[{{ argument.parameter_name|escaped_str }}]; ok {
        {{ argument_from_string(argument, "vars[%s]"|format(argument.parameter_name|escaped_str))|indent|indent }}
    }
    {% endif %}
    {% endfor %}{# /path arguments #}
{% endif %}{# /if path arguments #}
{% if route.wrapper.body_argument is not none %}{### Body argument ###}
    {% if newliner() %}{{ '\n' }}{% endif %}
    {% if route.wrapper.body_argument.required %}
    if r.Body == nil {
    {% set msg = "Parameter '%s' expected in body, but got no body"|format(route.wrapper.body_argument.parameter_name)|escaped_str %}
        http.Error(w, {{ msg }}, http.StatusBadRequest)
        return
    }
    {{ argument_from_body(route.wrapper.body_argument)|indent }}
    {% else %}
    if r.Body != nil {
        {{ argument_from_body(route.wrapper.body_argument)|indent|indent }}
    }
    {% endif %}{# /if route.wrapper.body_argument.required #}
{% endif %}{# /if body argument #}
{% if newliner() %}{{ '\n' }}{% endif %}
{% if not route.handler.arguments %}
    h.{{ route.handler.identifier }}(w, r)
{% else %}
    h.{{ route.handler.identifier }}(w,
        r,
{% for argument in route.handler.arguments %}
        {{ argument.parsing_identifier }}{{ "," if not loop.last else ")" }}
{% endfor %}
{% endif %}
}
''')

_ROUTES_GO_TPL = ENV.from_string('''\
package {{ package }}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
{% if imports_code != '' %}

{{ imports_code }}
{% endif %}

// SetupRouter sets up a router. If you don't use any middleware, you are good to go.
// Otherwise, you need to maually re-implement this function with your middlewares.
func SetupRouter(h Handler) *mux.Router {
    r := mux.NewRouter()
{% for route in routes %}

    r.HandleFunc(`{{ route.path }}`,
        func(w http.ResponseWriter, r *http.Request) {
            {{ route.wrapper.identifier }}(h, w, r)
        }).Methods({{ route.method|escaped_str }})
{% endfor %}

    return r
}
{% if routes %}
{% for route in routes %}

{{ wrapper_code[route] }}
{% endfor %}

{% endif %}
// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

''')


@icontract.ensure(lambda result: result.endswith('\n'), "final new line")
def generate_routes_go(package: str, routes: List[Route]) -> str:
    """
    Generate the file which defines the router and the routes.

    :param package: name of the package
    :param routes: routes that the router will handle.
    :return: Golang code
    """
    # imports
    import_set = {"github.com/gorilla/mux", "net/http"}

    for route in routes:
        for argument in route.handler.arguments:
            if argument.in_what == 'body':
                import_set.add('io/ioutil')
                import_set.add('encoding/json')

            if argument.in_what == 'query' or argument.in_what == 'header':
                tajp = ''
                if isinstance(argument.typedef, Primitivedef):
                    tajp = argument.typedef.type
                elif isinstance(argument.typedef, Pointerdef):
                    if isinstance(argument.typedef.pointed, Primitivedef):
                        tajp = argument.typedef.pointed.type

                if tajp in ['int', 'int32', 'int64', 'float32', 'float64']:
                    import_set.add('strconv')

    imports_code = _state_imports(import_set=import_set)

    wrapper_code = {
        route: _WRAPPER_TPL.render(
            route=route,
            express_or_identify_type={
                argument: _express_or_identify_type(typedef=argument.typedef)
                for route in routes for argument in route.handler.arguments
            },
            argument_from_string=_argument_from_string,
            argument_from_body=_argument_from_body)
        for route in routes
    }

    text = _ROUTES_GO_TPL.render(package=package, imports_code=imports_code, routes=routes, wrapper_code=wrapper_code)

    return swagger_to.indent.reindent(text=text, indention='\t')


_HANDLER_IMPL_GO_TPL = ENV.from_string('''\
package {{ package }}

import (
    "net/http"
    "log"
)

// HandlerImpl implements the Handler.
type HandlerImpl struct {
    LogErr *log.Logger
    LogOut *log.Logger}
{% for route in routes %}

// {{ route.handler.identifier }} implements Handler.{{ route.handler.identifier }}.
{% if not route.handler.arguments %}
func (h *HandlerImpl) {{ route.handler.identifier }}(w http.ResponseWriter,
    r *http.Request) {
{% else %}
func (h *HandlerImpl) {{ route.handler.identifier }}(w http.ResponseWriter,
    r *http.Request,
{% for argument in route.handler.arguments %}
    {{ argument.identifier }} {{ argument_type[argument] }}{{ ',' if not loop.last else ') {' }}
{% endfor %}
{% endif %}{# /if not route.handler.arguments #}
    {% set msg = "Not implemented: %s"|format(route.handler.identifier)|escaped_str %}
    http.Error(w, {{ msg }}, http.StatusInternalServerError)
    h.LogErr.Printf({{ msg }})
}
{% endfor %}{# /routes #}
''')


@icontract.ensure(lambda result: result.endswith('\n'), "final newline")
def generate_handler_impl_go(package: str, routes: List[Route]) -> str:
    """
    Generate a file which implements the handler interface with empty methods.

    :param package: name of the package
    :param routes: that a handler will handle
    :return: Golang code
    """
    text = _HANDLER_IMPL_GO_TPL.render(
        package=package,
        routes=routes,
        argument_type={
            argument: _express_or_identify_type(argument.typedef)
            for route in routes for argument in route.handler.arguments
        })

    return swagger_to.indent.reindent(text=text, indention='\t')


_HANDLER_GO_TPL = ENV.from_string('''\
package {{ package }}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import "net/http"

// Handler defines an interface to handling the routes.
type Handler interface {
{% for route in routes %}
    {% if not loop.first %}

    {% endif %}
    {% set handler_description %}
{{ route.handler.identifier }} handles the path `{{ route.path }}` with the method "{{ route.method }}".
{% if route.description %}

Path description:
{{ route.description }}
{% endif %}{# /if route.description #}
    {% endset %}{# /set handler_description #}
    {{ handler_description|trim|comment|indent }}
    {% if not route.handler.arguments %}
    {{ route.handler.identifier }}(w http.ResponseWriter,
        r *http.Request)
    {% else %}
    {{ route.handler.identifier }}(w http.ResponseWriter,
        r *http.Request,
    {% for argument in route.handler.arguments %}
        {{ argument.identifier }} {{ argument_type[argument] }}{{ ',' if not loop.last else ')' }}
    {% endfor %}
    {% endif %}{# /if not route.handler.arguments #}
{% endfor %}
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

''')


@icontract.ensure(lambda result: result.endswith('\n'), "final newline")
def generate_handler_go(package: str, routes: List[Route]) -> str:
    """
    Generate a file which defines the handler interface.

    :param package: name of the package
    :param routes: that a handler will handle
    :return: Golang code
    """
    text = _HANDLER_GO_TPL.render(
        package=package,
        routes=routes,
        argument_type={
            argument: _express_or_identify_type(argument.typedef)
            for route in routes for argument in route.handler.arguments
        })

    return swagger_to.indent.reindent(text=text, indention='\t')


_JSON_SCHEMAS_GO_TPL = ENV.from_string('''\
{# This template must be indented with tabs since we need to include the schema as text and hence can not re-indent
   since re-indention . #}
package {{ package }}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

{% if not schemas %}
// No schemas are defined in the swagger.
{% else %}
import (
	"errors"
	"fmt"
	"github.com/xeipuuv/gojsonschema"
)

func mustNewJSONSchema(text string, name string) *gojsonschema.Schema {
	loader := gojsonschema.NewStringLoader(text)
	schema, err := gojsonschema.NewSchema(loader)
	if err != nil {
		panic(fmt.Sprintf("failed to load JSON Schema %#v: %s", text, err.Error()))
	}
	return schema
}
{% for schema in schemas.values() %}

var jsonSchema{{ schema.identifier|capital_camel_case }}Text = `{{ schema.text|replace('`', '` + "`" + `') }}`
{% endfor %}
{% for schema in schemas.values() %}

var jsonSchema{{ schema.identifier|capital_camel_case }} = mustNewJSONSchema(
	jsonSchema{{ schema.identifier|capital_camel_case }}Text,
	{{ schema.identifier|escaped_str }})
{% endfor %}
{% for schema in schemas.values() %}

{% set validateFuncName = "ValidateAgainst%sSchema"|format(schema.identifier|capital_camel_case) %}
// {{ validateFuncName }} validates a message coming from the client against {{ schema.identifier }} schema.
func {{ validateFuncName }}(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchema{{ schema.identifier|capital_camel_case }}.Validate(loader)
	if err != nil {
		return err
	}

	if result.Valid() {
		return nil
	}

	msg := ""
	for i, valErr := range result.Errors() {
		if i > 0 {
			msg += ", "
		}
		msg += valErr.String()
	}
	return errors.New(msg)
}
{% endfor %}
{% endif %}{# /if not schemas #}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

''')


@icontract.ensure(lambda result: result.endswith('\n'), "final newline")
def generate_json_schemas_go(package: str, routes: List[Route], typedefs: MutableMapping[str, Typedef]) -> str:
    """
    Represent the definitions as json schemas and hard-codes them as strings in Go.

    It is assumed that the Swagger definitions already represent a subset of JSON Schema.
    This is theoretically not the case (some formats are swagger-only), but in most cases
    the literal translation should work.

    :param package: package name
    :param routes: needed to generate the parameter schemas if they are not already defined in the definitions
    :param typedefs: type definitions to generate the schemas for
    :return: Golang code
    """
    schemas = collections.OrderedDict()  # type: MutableMapping[str, JsonSchema]

    for route in routes:
        if route.wrapper.body_argument is not None:
            if not route.wrapper.body_argument.json_schema.identifier in schemas:
                schemas[route.wrapper.body_argument.json_schema.identifier] = route.wrapper.body_argument.json_schema

    for typedef_id, typedef in typedefs.items():
        if typedef.json_schema is None:
            raise AssertionError("Missing JSON schema for typedef: {!r}".format(typedef_id))

        # Assume the typedef identifiers are unique accross routes and typedefs.
        if typedef.json_schema.identifier not in schemas:
            schemas[typedef.json_schema.identifier] = typedef.json_schema

    return _JSON_SCHEMAS_GO_TPL.render(package=package, schemas=schemas)
