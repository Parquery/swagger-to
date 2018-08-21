"""
Parses the Swagger specification to an intermediate representation. This intermediate representation should be easier
to translate to code than a direct Swagger spec translation.
For example, references are resolved and do not figure as strings.
"""

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches
# pylint: disable=too-many-statements

import collections
import json
from typing import List, MutableMapping, Union, Any, Optional  # pylint: disable=unused-import

import swagger_to.swagger

# see https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md for a list of types
PRIMITIVE_SWAGGER_TYPES = ['string', 'number', 'integer', 'boolean', 'file']


class Typedef:
    def __init__(self):
        self.identifier = ''
        self.description = ''
        self.json_schema = JsonSchema()
        self.line = 0


class Propertydef:
    def __init__(self):
        self.name = ''
        self.typedef = Typedef()
        self.description = ''
        self.required = False
        self.line = 0


class Objectdef(Typedef):
    def __init__(self):
        super().__init__()

        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Propertydef]
        self.required = []  # type: List[str]


class Arraydef(Typedef):
    def __init__(self):
        super().__init__()

        self.items = Typedef()


class Mapdef(Typedef):
    def __init__(self):
        super().__init__()

        self.values = Typedef()


class Primitivedef(Typedef):
    def __init__(self):
        super().__init__()

        self.type = ''
        self.format = ''
        self.pattern = ''


class JsonSchema:
    def __init__(self):
        self.identifier = ''
        self.text = ''


class Parameter:
    def __init__(self):
        self.name = ''
        self.in_what = ''
        self.typedef = Typedef()
        self.required = False
        self.json_schema = JsonSchema()
        self.description = None  # type: Optional[str]
        self.line = 0


class Response:
    def __init__(self) -> None:
        self.code = ''
        self.description = ''
        self.typedef = None  # type: Optional[Typedef]
        self.line = 0


class Endpoint:
    def __init__(self):
        self.path = ''
        self.method = ''
        self.operation_id = ''
        self.parameters = []  # type: List[Parameter]
        self.description = ''
        self.produces = []  # type: List[str]
        self.consumes = []  # type: List[str]
        self.responses = collections.OrderedDict()  # type: MutableMapping[str, Response]
        self.line = 0


def preallocate_named_typedefs(definition: swagger_to.swagger.Definition,
                               typedefs: MutableMapping[str, Typedef]) -> None:
    """
    Adds an entry in `typedefs` with the correct instance of the type definition.

    :param definition: original representation of the definition
    :param typedefs: named intermediate representations of type definitions
    :return:
    """
    typedef = None  # type: Union[None, Primitivedef, Arraydef, Mapdef, Objectdef]
    if definition.typedef.type in PRIMITIVE_SWAGGER_TYPES:
        typedef = Primitivedef()
        typedef.type = definition.typedef.type
        typedef.format = definition.typedef.format
        typedef.pattern = definition.typedef.pattern

    elif definition.typedef.type == 'array':
        typedef = Arraydef()

    elif definition.typedef.type == 'object':
        if definition.typedef.additional_properties is not None:
            typedef = Mapdef()

        else:
            typedef = Objectdef()
            typedef.required = definition.typedef.required
    else:
        raise ValueError("Unexpected type of a typedef in the definition {!r}: {!r}".format(
            definition.identifier, definition.typedef.type))

    typedef.identifier = definition.identifier
    typedef.line = definition.typedef.__lineno__
    typedef.description = definition.typedef.description
    typedefs[typedef.identifier] = typedef


def resolve_substructures(definition: swagger_to.swagger.Definition, typedefs: MutableMapping[str, Typedef]) -> None:
    """
    Resolves substructures (such as property typedefs, item typedefs etc.) of a pre-allocated definition typedef.

    :param definition: original representation of the definition
    :param typedefs: named intermediate representations of type definitions
    :return:
    """
    if definition.identifier not in typedefs:
        raise ValueError("The definition has not been previously allocated: {!r}".format(definition.identifier))

    typedef = typedefs[definition.identifier]

    if isinstance(typedef, Primitivedef):
        pass

    elif isinstance(typedef, Arraydef):
        typedef.items = anonymous_or_get_typedef(original_typedef=definition.typedef.items, typedefs=typedefs)

    elif isinstance(typedef, Mapdef):
        typedef.values = anonymous_or_get_typedef(
            original_typedef=definition.typedef.additional_properties, typedefs=typedefs)

    elif isinstance(typedef, Objectdef):
        for prop_name, prop_typedef in definition.typedef.properties.items():
            propdef = Propertydef()
            propdef.name = prop_name
            propdef.typedef = anonymous_or_get_typedef(original_typedef=prop_typedef, typedefs=typedefs)
            propdef.description = prop_typedef.description
            propdef.required = propdef.name in typedef.required

            typedef.properties[prop_name] = propdef
    else:
        raise ValueError("Unexpected type of the definition {!r}: {}".format(typedef.identifier, type(typedef)))


def anonymous_or_get_typedef(original_typedef: swagger_to.swagger.Typedef,
                             typedefs: MutableMapping[str, Typedef]) -> Typedef:
    """
    Creates an anonymous (unnamed) intermediate type definition or resolves to an object pointed by the 'ref' property.

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
            raise ValueError("Unexpected None items: {!r}".format(original_typedef.raw_dict.adict))

        typedef.items = anonymous_or_get_typedef(original_typedef=original_typedef.items, typedefs=typedefs)

    elif original_typedef.type == 'object':
        if original_typedef.additional_properties is not None:
            typedef = Mapdef()

            typedef.values = anonymous_or_get_typedef(
                original_typedef=original_typedef.additional_properties, typedefs=typedefs)
        else:
            typedef = Objectdef()
            typedef.required = original_typedef.required

            for prop_name, prop_typedef in typedef.properties.items():
                propdef = Propertydef()
                propdef.typedef = anonymous_or_get_typedef(original_typedef=prop_typedef.typedef, typedefs=typedefs)
                propdef.description = prop_typedef.description
                propdef.name = prop_name
                propdef.required = propdef.name in typedef.required
                propdef.line = propdef.typedef.line

                typedef.properties[prop_name] = propdef

    else:
        raise ValueError("Unexpected definition: {!r}".format(original_typedef.raw_dict.adict))

    assert typedef is not None

    return typedef


def to_typedefs(swagger: swagger_to.swagger.Swagger) -> MutableMapping[str, Typedef]:
    """
    Translates all original (Swagger) definitions into intermediate type definitions.

    :param swagger: Swagger specification
    :return: intermediate type definitions
    """
    typedefs = collections.OrderedDict()  # type: MutableMapping[str, Typedef]

    # pre-allocate type definitions in the first pass so that we can resolve
    # all the references to intermediate typedefs.
    for defi in swagger.definitions.values():
        preallocate_named_typedefs(definition=defi, typedefs=typedefs)

    # resolve references given as URIs to object pointers to intermediate type definitions in a second pass.
    for defi in swagger.definitions.values():
        resolve_substructures(definition=defi, typedefs=typedefs)

    for typedef in typedefs.values():
        json_schema_identifier = typedef.identifier

        typedef.json_schema = to_json_schema(
            identifier=json_schema_identifier,
            original_typedef=swagger.definitions[typedef.identifier].typedef,
            definitions=swagger.definitions)

    return typedefs


def collect_referenced_definitions(typedef: swagger_to.swagger.Typedef,
                                   definitions: MutableMapping[str, swagger_to.swagger.Definition]) -> List[str]:
    if typedef.ref != '':
        definition_name = swagger_to.parse_definition_ref(typedef.ref)
        definition = definitions[definition_name]

        return [definition_name] + collect_referenced_definitions(typedef=definition.typedef, definitions=definitions)

    referenced_definitions = []  # type: List[str]

    for prop in typedef.properties.values():
        referenced_definitions.extend(collect_referenced_definitions(typedef=prop, definitions=definitions))

    if typedef.items is not None:
        referenced_definitions.extend(collect_referenced_definitions(typedef=typedef.items, definitions=definitions))

    if typedef.additional_properties is not None:
        referenced_definitions.extend(
            collect_referenced_definitions(typedef=typedef.additional_properties, definitions=definitions))

    return referenced_definitions


def recursively_strip_descriptions(schema_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """
    Strips the value if the key is "description" in-place.

    :param schema_dict: JSON schema as a python dictionary.
    :return:
    """
    new_schema_dict = collections.OrderedDict()  # type: MutableMapping[str, Any]

    for key, value in schema_dict.items():
        if key.lower() == 'description':
            if not isinstance(value, str):
                raise ValueError("Expected the value in a schema to be a string, but got: {}".format(type(value)))

            new_schema_dict[key] = value.strip()
        elif isinstance(value, list):
            lst = []  # type: List[Any]
            for item in value:
                if isinstance(item, (dict, collections.OrderedDict)):
                    lst.append(recursively_strip_descriptions(schema_dict=item))
                else:
                    lst.append(item)

            new_schema_dict[key] = lst

        elif isinstance(value, (dict, collections.OrderedDict)):
            new_schema_dict[key] = recursively_strip_descriptions(schema_dict=value)
        elif isinstance(value, swagger_to.swagger.RawDict):
            new_schema_dict[key] = recursively_strip_descriptions(schema_dict=value.adict)
        else:
            new_schema_dict[key] = value

    return new_schema_dict


def to_json_schema(identifier: str, original_typedef: swagger_to.swagger.Typedef,
                   definitions: MutableMapping[str, swagger_to.swagger.Definition]) -> JsonSchema:
    json_schema = JsonSchema()
    json_schema.identifier = identifier

    schema = collections.OrderedDict()  # type: MutableMapping[str, Any]

    schema['title'] = json_schema.identifier
    schema['$schema'] = "http://json-schema.org/draft-04/schema#"

    referenced_definitions = collect_referenced_definitions(
        typedef=original_typedef, definitions=definitions)  # top-down
    referenced_definitions.reverse()  # bottom-up

    schema_definitions = collections.OrderedDict()  # type: MutableMapping[str, Any]

    for definition_name in referenced_definitions:
        if definition_name in schema_definitions:
            continue

        schema_definitions[definition_name] = definitions[definition_name].typedef.raw_dict.adict

    if len(schema_definitions) > 0:
        schema['definitions'] = schema_definitions

    for key, value in original_typedef.raw_dict.adict.items():
        schema[key] = value

    schema = recursively_strip_descriptions(schema_dict=schema)

    json_schema.text = json.dumps(schema, indent=2)

    return json_schema


def to_parameter(original_param: swagger_to.swagger.Parameter, typedefs: MutableMapping[str, Typedef]) -> Parameter:
    """
    Translates an original parameter to an intermediate parameter representation.

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
                original_param.raw_dict.adict))

    typedef = anonymous_or_get_typedef(original_typedef=original_typedef, typedefs=typedefs)

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
    params = collections.OrderedDict()  # type: MutableMapping[str, Parameter]

    for original_param in swagger.parameters.values():
        if original_param.ref != '':
            raise ValueError("Expected no 'ref' property in a parameter definition {!r}, but got: {!r}".format(
                original_param.name, original_param.raw_dict.adict))

        param = to_parameter(original_param=original_param, typedefs=typedefs)
        params[param.name] = param

    return params


def anonymous_or_get_parameter(original_param: swagger_to.swagger.Parameter, typedefs: MutableMapping[str, Typedef],
                               params: MutableMapping[str, Parameter]) -> Parameter:
    if original_param.ref != '':
        param_ref_name = swagger_to.parse_parameter_ref(ref=original_param.ref)
        if param_ref_name not in params:
            raise ValueError("The parameter referenced by the parameter {!r} has not been defined: {!r}".format(
                original_param.raw_dict.adict, original_param.ref))

        return params[param_ref_name]

    return to_parameter(original_param=original_param, typedefs=typedefs)


def to_response(swagger_response: swagger_to.swagger.Response, typedefs: MutableMapping[str, Typedef]) -> Response:
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
        resp.typedef = anonymous_or_get_typedef(original_typedef=swagger_typedef, typedefs=typedefs)

    return resp


def to_endpoint(method: swagger_to.swagger.Method, typedefs: MutableMapping[str, Typedef],
                params: MutableMapping[str, Parameter]) -> Endpoint:
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
    endpt.consumes = method.consumes
    endpt.produces = method.produces
    endpt.line = method.__lineno__

    for original_param in method.parameters:
        param = anonymous_or_get_parameter(original_param=original_param, typedefs=typedefs, params=params)

        if param.in_what == 'body':
            if param.typedef.identifier == '':
                json_schema_identifier = original_param.method.operation_id + "_" + param.name
            else:
                json_schema_identifier = param.typedef.identifier

            param.json_schema = to_json_schema(
                identifier=json_schema_identifier,
                original_typedef=original_param.schema,
                definitions=method.path.swagger.definitions)

        endpt.parameters.append(param)

    for resp_code, swagger_resp in method.responses.items():
        endpt.responses[resp_code] = to_response(swagger_response=swagger_resp, typedefs=typedefs)

    return endpt


def to_endpoints(swagger: swagger_to.swagger.Swagger, typedefs: MutableMapping[str, Typedef],
                 params: MutableMapping[str, Parameter]) -> List[Endpoint]:
    endpoints = []  # type: List[Endpoint]
    for path in swagger.paths.values():
        for method in path.methods:
            if not method.x_swagger_to_skip:
                endpoint = to_endpoint(method=method, typedefs=typedefs, params=params)
                endpoints.append(endpoint)

    return endpoints
