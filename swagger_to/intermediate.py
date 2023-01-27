"""
Parse the Swagger specification to an intermediate representation.

This intermediate representation is meant to be easier to translate to code than
to translate directly from a Swagger spec. For example, references are resolved to the actual type definitions and
do not figure as strings.
"""

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches
# pylint: disable=too-many-statements

import collections
import json
from typing import List, MutableMapping, Union, Any, Optional, \
    Mapping, Set  # pylint: disable=unused-import

import icontract

import swagger_to.swagger

# see https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md for a list of types
PRIMITIVE_SWAGGER_TYPES = ['string', 'number', 'integer', 'boolean', 'file']


class Typedef:
    """Represent an intermediate type definition."""

    def __init__(self):
        """Initialize with defaults."""
        self.identifier = ''
        self.description = ''
        self.json_schema = JsonSchema()
        self.line = 0


class Propertydef:
    """Represent a property of an object."""

    def __init__(self):
        """Initialize with default values."""
        self.name = ''
        self.typedef = Typedef()
        self.description = ''
        self.required = False
        self.line = 0


class Objectdef(Typedef):
    """Represent an object definition."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Propertydef]
        self.required = []  # type: List[str]


class Arraydef(Typedef):
    """Represent an array."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.items = Typedef()


class Mapdef(Typedef):
    """Represent a map (i.e. a dictionary)."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.values = Typedef()


class Primitivedef(Typedef):
    """Represent a primitive type (such as integer, floating-point number or a string)."""

    def __init__(self):
        """Initialize with default values."""
        super().__init__()

        self.type = ''
        self.format = None  # type: Optional[str]
        self.pattern = ''


class AnyValuedef(Typedef):
    """Represent a any value type for empty schema."""


class JsonSchema:
    """Represent a schema for validation of JSON."""

    def __init__(self):
        """Initialize with default values."""
        self.identifier = ''
        self.text = ''


class Parameter:
    """Represent a parameter of an endpoint."""

    def __init__(self):
        """Initialize with default values."""
        self.name = ''
        self.in_what = ''
        self.typedef = Typedef()
        self.required = False
        self.json_schema = JsonSchema()
        self.description = None  # type: Optional[str]
        self.line = 0


class Response:
    """Represent a response from an endpoint."""

    def __init__(self) -> None:
        """Initialize with default values."""
        self.code = ''
        self.description = ''
        self.typedef = None  # type: Optional[Typedef]
        self.line = 0


class Endpoint:
    """Represent an endpoint of a service."""

    def __init__(self):
        """Initialize with default values."""
        self.path = ''
        self.method = ''
        self.operation_id = ''
        self.parameters = []  # type: List[Parameter]
        self.description = ''
        self.produces = []  # type: List[str]
        self.consumes = []  # type: List[str]
        self.responses = collections.OrderedDict()  # type: MutableMapping[str, Response]
        self.line = 0


def _preallocate_named_typedefs(definition: swagger_to.swagger.Definition,
                                typedefs: MutableMapping[str, Typedef]) -> None:
    """
    Add an entry in `typedefs` with the correct instance of the type definition.

    :param definition: original representation of the definition
    :param typedefs: named intermediate representations of type definitions
    :return:
    """
    typedef = None  # type: Union[None, Primitivedef, Arraydef, Mapdef, Objectdef, AnyValuedef]
    if definition.typedef.type in PRIMITIVE_SWAGGER_TYPES:
        typedef = Primitivedef()
        typedef.type = definition.typedef.type
        typedef.format = definition.typedef.format
        typedef.pattern = definition.typedef.pattern

    elif definition.typedef.type == 'array':
        typedef = Arraydef()

    elif definition.typedef.type == 'object' or len(definition.typedef.properties) > 0 or \
            definition.typedef.all_of is not None:
        if definition.typedef.additional_properties is not None:
            typedef = Mapdef()

        else:
            typedef = Objectdef()
            typedef.required = definition.typedef.required
    elif definition.typedef.type == '':
        typedef = AnyValuedef()
    else:
        raise ValueError(("Could not determine the intermediate type "
                          "for a Swagger type definition {!r} (here given as JSON):\n{}").format(
                              definition.identifier, json.dumps(definition.typedef.raw_dict, indent=2)))

    typedef.identifier = definition.identifier
    typedef.line = definition.typedef.__lineno__
    typedef.description = definition.typedef.description
    typedefs[typedef.identifier] = typedef


@icontract.require(
    lambda definition, typedefs: definition.identifier in typedefs,
    "The definition must be previously allocated.",
    error=ValueError)
def _resolve_substructures(definition: swagger_to.swagger.Definition, typedefs: MutableMapping[str, Typedef]) -> None:
    """
    Resolve substructures (such as property typedefs, item typedefs etc.) of a pre-allocated definition typedef.

    :param definition: original representation of the definition
    :param typedefs: named intermediate representations of type definitions
    :return:
    """
    typedef = typedefs[definition.identifier]

    if isinstance(typedef, Primitivedef):
        pass

    elif isinstance(typedef, AnyValuedef):
        pass

    elif isinstance(typedef, Arraydef):
        if definition.typedef.items is None:
            raise ValueError("Unexpected None definition.typedef.items in an Arraydef")

        typedef.items = _anonymous_or_get_typedef(original_typedef=definition.typedef.items, typedefs=typedefs)

    elif isinstance(typedef, Mapdef):
        if definition.typedef.additional_properties is None:
            raise ValueError("Unexpected None definition.typedef.additional_properties in a Mapdef")

        typedef.values = _anonymous_or_get_typedef(
            original_typedef=definition.typedef.additional_properties, typedefs=typedefs)

    elif isinstance(typedef, Objectdef):
        properties = collections.OrderedDict()  # type: MutableMapping[str, Propertydef]

        # Handle first allOf, if available
        if definition.typedef.all_of is not None and len(definition.typedef.all_of) > 0:
            for original_superdef in definition.typedef.all_of:
                inter_typedef = _anonymous_or_get_typedef(original_typedef=original_superdef, typedefs=typedefs)
                if not isinstance(inter_typedef, Objectdef):
                    raise ValueError(
                        "Unexpected super definition in allOf which is not of type object on line {}: {!r}".format(
                            original_superdef.__lineno__, original_superdef.raw_dict))

                properties.update(inter_typedef.properties)

        # Then set the local properties, overriding any of the allOf on the way
        for prop_name, prop_typedef in definition.typedef.properties.items():
            propdef = Propertydef()
            propdef.name = prop_name
            propdef.typedef = _anonymous_or_get_typedef(original_typedef=prop_typedef, typedefs=typedefs)
            propdef.description = prop_typedef.description
            propdef.required = propdef.name in typedef.required

            properties[prop_name] = propdef

        typedef.properties = properties
    else:
        raise ValueError("Unexpected type of the definition {!r}: {}".format(typedef.identifier, type(typedef)))


def _anonymous_or_get_typedef(original_typedef: swagger_to.swagger.Typedef,
                              typedefs: MutableMapping[str, Typedef]) -> Typedef:
    """
    Create an anonymous (unnamed) intermediate type definition or resolve to an object pointed by the 'ref' property.

    :param original_typedef: original (Swagger) type definition
    :param typedefs: named intermediate type definitions
    :return: anonymous (created) or named (resolved) intermediate typedefinition
    """
    if original_typedef.ref != '':
        definition_name = swagger_to.parse_definition_ref(ref=original_typedef.ref)

        if definition_name not in typedefs:
            raise ValueError('The definition referenced from {!r} has not been previously defined'.format(
                original_typedef.ref))

        typedef = typedefs[definition_name]
        return typedef

    if original_typedef.type in PRIMITIVE_SWAGGER_TYPES:
        typedef = Primitivedef()
        typedef.type = original_typedef.type
        typedef.format = original_typedef.format
        typedef.pattern = original_typedef.pattern
        typedef.line = original_typedef.__lineno__

    elif original_typedef.type == 'array':
        typedef = Arraydef()

        if original_typedef.items is None:
            raise ValueError("Unexpected None items: {!r}".format(original_typedef.raw_dict))

        typedef.items = _anonymous_or_get_typedef(original_typedef=original_typedef.items, typedefs=typedefs)

    elif original_typedef.type == 'object' or len(original_typedef.properties) > 0:
        if original_typedef.additional_properties is not None:
            typedef = Mapdef()
            typedef.values = _anonymous_or_get_typedef(
                original_typedef=original_typedef.additional_properties, typedefs=typedefs)

        elif original_typedef.all_of is None and len(original_typedef.properties) == 0:
            typedef = AnyValuedef()

        else:
            typedef = Objectdef()
            typedef.required = original_typedef.required

            properties = collections.OrderedDict()  # type: MutableMapping[str, Propertydef]

            # Handle first allOf, if available
            if original_typedef.all_of is not None and len(original_typedef.all_of) > 0:
                for original_superdef in original_typedef.all_of:
                    inter_typedef = _anonymous_or_get_typedef(original_typedef=original_superdef, typedefs=typedefs)
                    if not isinstance(inter_typedef, Objectdef):
                        raise ValueError(
                            "Unexpected super definition in allOf which is not of type object on line {}: {!r}".format(
                                original_superdef.__lineno__, original_superdef.raw_dict))

                    properties.update(inter_typedef.properties)

            for prop_name, original_prop_typedef in original_typedef.properties.items():
                propdef = Propertydef()
                propdef.typedef = _anonymous_or_get_typedef(original_typedef=original_prop_typedef, typedefs=typedefs)
                propdef.description = original_prop_typedef.description
                propdef.name = prop_name
                propdef.required = propdef.name in original_typedef.required
                propdef.line = original_prop_typedef.__lineno__

                properties[prop_name] = propdef

            typedef.properties = properties

    elif original_typedef.type == '':
        typedef = AnyValuedef()
        typedef.line = original_typedef.__lineno__

    else:
        raise ValueError("Unexpected definition: {!r}".format(original_typedef.raw_dict))

    assert typedef is not None

    return typedef


def to_typedefs(swagger: swagger_to.swagger.Swagger) -> MutableMapping[str, Typedef]:
    """
    Translate all original (Swagger) definitions into intermediate type definitions.

    :param swagger: Swagger specification
    :return: intermediate type definitions
    """
    typedefs = collections.OrderedDict()  # type: MutableMapping[str, Typedef]

    # pre-allocate type definitions in the first pass so that we can resolve
    # all the references to intermediate typedefs.
    for defi in swagger.definitions.values():
        _preallocate_named_typedefs(definition=defi, typedefs=typedefs)

    # resolve references given as URIs to object pointers to intermediate type definitions in a second pass.
    for defi in swagger.definitions.values():
        _resolve_substructures(definition=defi, typedefs=typedefs)

    for typedef in typedefs.values():
        json_schema_identifier = typedef.identifier

        typedef.json_schema = _to_json_schema(
            identifier=json_schema_identifier,
            original_typedef=swagger.definitions[typedef.identifier].typedef,
            definitions=swagger.definitions)

    return typedefs


# yapf: disable
@icontract.ensure(
    lambda definitions, result:
    all(
        name in definitions
        for name in result
    ),
    enabled=icontract.SLOW
)
@icontract.ensure(
    lambda result: len(set(result)) == len(result),
    "No duplicates in the result" ,
    enabled=icontract.SLOW
)
# yapf: enable
def _collect_referenced_definitions(typedef: swagger_to.swagger.Typedef,
                                    definitions: MutableMapping[str, swagger_to.swagger.Definition]) -> List[str]:
    """
    Inspect the intermediate representation of a type definition and collect other type definitions referenced by it.

    :param typedef: type definition in the original Swagger spec
    :param definitions: table of type definitions in intermediate representation
    :return: referenced type definitions given as a list of their identifiers
    """
    result = []  # type: List[str]

    stack = [typedef]  # type: List[swagger_to.swagger.Typedef]

    # This set is necessary to prevent endless recursion. The set contains the names of the referenced definitions
    # which have been already included in the result.
    # See: https://github.com/Parquery/swagger-to/issues/129
    visited_definitions = set()  # type: Set[str]

    while len(stack) > 0:
        another_typedef = stack.pop()

        if another_typedef.ref != '':
            definition_name = swagger_to.parse_definition_ref(another_typedef.ref)

            # We need this check to avoid endless recursion.
            # See: https://github.com/Parquery/swagger-to/issues/129
            if definition_name not in visited_definitions:
                definition = definitions[definition_name]
                result.append(definition_name)

                stack.append(definition.typedef)
                visited_definitions.add(definition_name)

        else:
            for prop in another_typedef.properties.values():
                stack.append(prop)

            if another_typedef.items is not None:
                stack.append(another_typedef.items)

            if another_typedef.additional_properties is not None:
                stack.append(another_typedef.additional_properties)

            if another_typedef.all_of is not None:
                for superdef in another_typedef.all_of:
                    stack.append(superdef)

    return result


def _recursively_strip_descriptions(schema_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """
    Walk the dictionary and strip the value if the key is "description".

    :param schema_dict: JSON schema as a python dictionary.
    :return: modified ``schema_dict`` with all the descriptions stripped.
    """
    new_schema_dict = collections.OrderedDict()  # type: MutableMapping[str, Any]

    for key, value in schema_dict.items():
        if isinstance(value, list):
            lst = []  # type: List[Any]
            for item in value:
                if isinstance(item, (dict, collections.OrderedDict)):
                    lst.append(_recursively_strip_descriptions(schema_dict=item))
                else:
                    lst.append(item)

            new_schema_dict[key] = lst

        elif isinstance(value, (dict, collections.OrderedDict)):
            new_schema_dict[key] = _recursively_strip_descriptions(schema_dict=value)
        elif isinstance(value, swagger_to.swagger.RawDict):
            new_schema_dict[key] = _recursively_strip_descriptions(schema_dict=value)
        elif key.lower() == 'description':
            if not isinstance(value, str):
                raise ValueError("Expected the value in a schema to be a string, but got: {}".format(type(value)))

            new_schema_dict[key] = value.strip()
        else:
            new_schema_dict[key] = value

    return new_schema_dict


def _to_json_schema(identifier: str, original_typedef: swagger_to.swagger.Typedef,
                    definitions: MutableMapping[str, swagger_to.swagger.Definition]) -> JsonSchema:
    """
    Convert the JSON validation schema to an intermediate representation.

    :param identifier: identifier of the JSON validation schema
    :param original_typedef: original type definition from a Swagger spec
    :param definitions: table of original type definitions in the Swagger spec
    :return:
    """
    json_schema = JsonSchema()
    json_schema.identifier = identifier

    schema = collections.OrderedDict()  # type: MutableMapping[str, Any]

    schema['title'] = json_schema.identifier
    schema['$schema'] = "http://json-schema.org/draft-04/schema#"

    referenced_definitions = _collect_referenced_definitions(
        typedef=original_typedef, definitions=definitions)  # top-down
    referenced_definitions.reverse()  # bottom-up

    schema_definitions = collections.OrderedDict()  # type: MutableMapping[str, Any]

    for definition_name in referenced_definitions:
        if definition_name in schema_definitions:
            continue

        schema_definitions[definition_name] = definitions[definition_name].typedef.raw_dict

    if len(schema_definitions) > 0:
        schema['definitions'] = schema_definitions

    for key, value in original_typedef.raw_dict.items():
        schema[key] = value

    schema = _recursively_strip_descriptions(schema_dict=schema)

    json_schema.text = json.dumps(schema, indent=2)

    return json_schema


def _to_parameter(original_param: swagger_to.swagger.Parameter, typedefs: MutableMapping[str, Typedef]) -> Parameter:
    """
    Translate an original parameter from a Swagger spec to an intermediate parameter representation.

    :param original_param: parameter in the original (Swagger) representation
    :param typedefs: intermediate type definitions
    :return: intermediate representation of a parameter
    """
    if original_param.type != '':
        if original_param.type not in PRIMITIVE_SWAGGER_TYPES:
            raise ValueError("Expected type of a parameter to be one of {!r}, but got: {!r}".format(
                PRIMITIVE_SWAGGER_TYPES, original_param.type))

        original_typedef = swagger_to.swagger.Typedef()
        original_typedef.type = original_param.type
        original_typedef.format = original_param.format
        original_typedef.pattern = original_param.pattern
    elif original_param.schema is not None:
        original_typedef = original_param.schema
    else:
        raise ValueError(
            "Could not resolve the type of the parameter, neither 'type' nor 'schema' defined: {!r}".format(
                original_param.raw_dict))

    typedef = _anonymous_or_get_typedef(original_typedef=original_typedef, typedefs=typedefs)

    param = Parameter()
    param.typedef = typedef
    param.in_what = original_param.in_what
    param.name = original_param.name
    param.required = original_param.required
    param.description = original_param.description
    param.line = original_param.__lineno__

    return param


def to_parameters(swagger: swagger_to.swagger.Swagger,
                  typedefs: MutableMapping[str, Typedef]) -> MutableMapping[str, Parameter]:
    """
    Translate all the parameter _definitions_ in the Swagger spec to their intermediate representation.

    :param swagger: original Swagger spec
    :param typedefs: table of type definitions in intermediate representation
    :return: table of intermediate representation of parameter definitions
    """
    params = collections.OrderedDict()  # type: MutableMapping[str, Parameter]

    for key, original_param in swagger.parameters.items():
        if original_param.ref != '':
            raise ValueError("Expected no 'ref' property in a parameter definition {!r}, but got: {!r}".format(
                original_param.name, original_param.raw_dict))

        param = _to_parameter(original_param=original_param, typedefs=typedefs)
        params[key] = param

    return params


def _anonymous_or_get_parameter(original_param: swagger_to.swagger.Parameter, typedefs: MutableMapping[str, Typedef],
                                params: MutableMapping[str, Parameter]) -> Parameter:
    """
    Retrieve a parameter from the table if it's been defined or otherwise create a new parameter definition.

    :param original_param: parameter definition in the original Swagger spec
    :param typedefs: table of type definitions in intermediate representation
    :param params: table of parameter definitions in intermediate representation
    :return: parameter definition in intermediate representation
    """
    if original_param.ref != '':
        param_ref_name = swagger_to.parse_parameter_ref(ref=original_param.ref)
        if param_ref_name not in params:
            raise ValueError("The parameter referenced by the parameter {!r} has not been defined: {!r}".format(
                original_param.raw_dict, original_param.ref))

        return params[param_ref_name]

    return _to_parameter(original_param=original_param, typedefs=typedefs)


def _to_response(swagger_response: swagger_to.swagger.Response, typedefs: MutableMapping[str, Typedef]) -> Response:
    """
    Translate the endpoint response from the original Swagger spec to an intermediate representation.

    :param swagger_response: endpoint response in the original Swagger spec
    :param typedefs: table of type definitions in intermediate representation
    :return: intermediate representation of an endpoint response
    """
    resp = Response()
    resp.description = swagger_response.description
    resp.code = swagger_response.code
    resp.line = swagger_response.__lineno__

    swagger_typedef = None  # type: Optional[swagger_to.swagger.Typedef]

    if swagger_response.type != '':
        if swagger_response.type not in PRIMITIVE_SWAGGER_TYPES:
            raise ValueError("Expected type of a parameter to be one of {!r}, but got: {!r}".format(
                PRIMITIVE_SWAGGER_TYPES, swagger_response.type))

        swagger_typedef = swagger_to.swagger.Typedef()
        swagger_typedef.type = swagger_response.type
        swagger_typedef.format = swagger_response.format
        swagger_typedef.pattern = swagger_response.pattern

    elif swagger_response.schema is not None:
        swagger_typedef = swagger_response.schema
    else:
        # no typedef will be set for this response
        pass

    if swagger_typedef is not None:
        resp.typedef = _anonymous_or_get_typedef(original_typedef=swagger_typedef, typedefs=typedefs)

    return resp


def _to_endpoint(swagger: swagger_to.swagger.Swagger, method: swagger_to.swagger.Method,
                 typedefs: MutableMapping[str, Typedef], params: MutableMapping[str, Parameter]) -> Endpoint:
    """
    Translate the endpoint from the original Swagger spec to an intermediate representation.

    :param method: the method specification in the original Swagger spec
    :param typedefs: table of type definitions in intermediate representation
    :param params: table of parameter definitions in intermediate representation
    :return: intermediate representation of an endpoint
    """
    if method.path is None:
        raise ValueError("Unexpected None method.path")

    if method.path.swagger is None:
        raise ValueError("Unexpected None method.path.swagger")

    base_path = method.path.swagger.base_path
    if base_path != '':
        pth = '{}/{}'.format(base_path.rstrip('/'), method.path.identifier.lstrip('/'))
    else:
        pth = method.path.identifier

    endpt = Endpoint()
    endpt.path = pth
    endpt.method = method.identifier
    endpt.operation_id = method.operation_id
    endpt.description = method.description

    # Propagate the global consumes, if specified
    if method.consumes is None and swagger.consumes is None:
        endpt.consumes = []
    elif method.consumes is not None:
        endpt.consumes = method.consumes
    else:
        assert swagger.consumes is not None
        endpt.consumes = swagger.consumes

    # Propagate the global produces, if specified
    if method.produces is None and swagger.produces is None:
        endpt.produces = []
    elif method.produces is not None:
        endpt.produces = method.produces
    else:
        assert swagger.produces is not None
        endpt.produces = swagger.produces

    endpt.line = method.__lineno__

    # We need to join method parameters with the path's common parameters.
    # See https://swagger.io/docs/specification/2-0/describing-parameters/,
    # Section "Common Parameters"
    for original_param in method.parameters + method.path.parameters:
        param = _anonymous_or_get_parameter(original_param=original_param, typedefs=typedefs, params=params)

        if param.in_what == 'body':
            if param.typedef.identifier == '':
                if original_param.method is None:
                    raise ValueError("Unexpected None method in original_param {} on path {}".format(
                        original_param.name, pth))

                json_schema_identifier = original_param.method.operation_id + "_" + param.name
            else:
                json_schema_identifier = param.typedef.identifier

            if original_param.schema is None:
                raise ValueError('Unexpected None schema in original_param {} on path {}'.format(
                    original_param.name, pth))

            param.json_schema = _to_json_schema(
                identifier=json_schema_identifier,
                original_typedef=original_param.schema,
                definitions=method.path.swagger.definitions)

        endpt.parameters.append(param)

    for resp_code, swagger_resp in method.responses.items():
        endpt.responses[resp_code] = _to_response(swagger_response=swagger_resp, typedefs=typedefs)

    return endpt


def to_endpoints(swagger: swagger_to.swagger.Swagger, typedefs: MutableMapping[str, Typedef],
                 params: MutableMapping[str, Parameter]) -> List[Endpoint]:
    """
    Translate endpoints from the original Swagger spec to their intermediate representation.

    :param swagger: original Swagger spec
    :param typedefs: table of type definitions in intermediate representation
    :param params: table of parameter definitions in intermediate representation
    :return: intermediate representation of endpoints
    """
    endpoints = []  # type: List[Endpoint]
    for path in swagger.paths.values():
        for method in path.methods:
            if not method.x_swagger_to_skip:
                endpoint = _to_endpoint(swagger=swagger, method=method, typedefs=typedefs, params=params)
                endpoints.append(endpoint)

    return endpoints
