"""Parse Swagger spec."""

import collections
import json
import pathlib
from typing import List, Optional, MutableMapping, Any, Tuple, Union, cast  # pylint: disable=unused-import

import jsonschema
import yaml
import yaml.resolver
import yaml.constructor

import swagger_to.swaggerjsonschema

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches


class RawDict(collections.OrderedDict):
    """Represent a raw dictionary from a Swagger spec file."""

    assert not hasattr(dict, "source"), "dict class has unexpectedly an attribute 'source'."
    assert not hasattr(dict, "lineno"), "dict class has unexpectedly an attribute 'lineno'."

    def __init__(self, adict: MutableMapping[str, Any] = None, source: str = '', lineno: int = 0) -> None:
        """Initialize with the given values."""
        self.source = source
        self.lineno = lineno

        super().__init__(adict if adict is not None else collections.OrderedDict())


class Typedef:
    """Represent a type definition in a Swagger spec."""

    def __init__(self):
        """Initialize with defaults."""
        self.ref = ''
        self.description = ''
        self.type = ''
        self.format = None  # type: Optional[str]
        self.pattern = ''
        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Typedef]
        self.required = []  # type: List[str]
        self.items = None  # type: Optional[Typedef]
        self.additional_properties = None  # type: Optional[Typedef]
        self.all_of = None  # type: Optional[List[Typedef]]
        self.__lineno__ = 0

        # original specification dictionary, if available; not deep-copied, do not modify
        self.raw_dict = None  # type: RawDict


class Definition:
    """Represent an identifiable data type from the Swagger spec."""

    def __init__(self, identifier: str, typedef: Typedef, swagger: 'Swagger'):
        """
        Initialize with the given values.

        :param identifier: identifies the definition
        :param typedef: parsed type definition
        :param swagger: original Swagger spec
        """
        self.identifier = identifier
        self.typedef = typedef
        self.swagger = swagger


class Parameter:
    """Represent a parameer of a method in Swagger spec."""

    def __init__(self):
        """Initialize with defaults."""
        self.method = None  # type: Optional[Method]
        self.name = ''
        self.in_what = ''
        self.description = ''
        self.required = False
        self.type = ''
        self.format = ''
        self.pattern = ''
        self.schema = None  # type: Optional[Typedef]
        self.ref = ''
        self.__lineno__ = 0

        # original specification dictionary, if available; not deep-copied, do not modify
        self.raw_dict = None  # type: Optional[RawDict]


class Response:
    """Represent an endpoint response in Swagger spec."""

    def __init__(self):
        """Initialize with defaults."""
        self.code = ''
        self.description = ''
        self.schema = None  # type: Optional[Typedef]
        self.type = ''
        self.format = ''
        self.pattern = ''
        self.__lineno__ = 0

        # original specification dictionary, if available; not deep-copied, do not modify
        self.raw_dict = None  # type: Optional[RawDict]


class Method:
    """Represent an endpoint method in Swagger spec."""

    def __init__(self):
        """Initialize with defaults."""
        self.identifier = ''
        self.operation_id = ''
        self.tags = []  # type: List[str]
        self.description = ''
        self.parameters = []  # type: List[Parameter]
        self.responses = collections.OrderedDict()  # type: MutableMapping[str, Response]
        self.path = None  # type: Optional[Path]
        self.produces = None  # type: Optional[List[str]]
        self.consumes = None  # type: Optional[List[str]]
        self.x_swagger_to_skip = False
        self.__lineno__ = 0

        # original specification dictionary, if available; not deep-copied, do not modify
        self.raw_dict = None  # type: Optional[RawDict]


class Path:
    """Represent an endpoint path in Swagger spec."""

    def __init__(self):
        """Initialize with defaults."""
        self.identifier = ''
        self.methods = []  # type: List[Method]
        self.swagger = None  # type: Optional[Swagger]
        self.__lineno__ = 0

        # These are common parameters for all the methods of the path,
        # see https://swagger.io/docs/specification/2-0/describing-parameters/,
        # Section "Common Parameters"
        self.parameters = []  # type: List[Parameter]

        # original specification dictionary, if available; not deep-copied, do not modify
        self.raw_dict = None  # type: Optional[RawDict]


class Swagger:
    """Represent a parsed Swagger specification."""

    def __init__(self):
        """Initialize with defaults."""
        self.name = ""
        self.base_path = ""
        self.description = ""
        self.paths = collections.OrderedDict()  # type: MutableMapping[str, Path]
        self.definitions = collections.OrderedDict()  # type: MutableMapping[str, Definition]
        self.parameters = collections.OrderedDict()  # type: MutableMapping[str, Parameter]

        # These are global produces and consumes which are, if specified, propagated to
        # endpoints.
        self.produces = None  # type: Optional[List[str]]
        self.consumes = None  # type: Optional[List[str]]

        self.raw_dict = None  # type: Optional[RawDict]


def _parse_typedef(raw_dict: RawDict) -> Tuple[Typedef, List[str]]:
    """
    Parse the type definition from the raw dictionary in the Swagger spec.

    :param raw_dict: raw dictionary of the Swagger spec
    :return: (parsed type definition, parsing errors if any)
    """
    typedef = Typedef()
    typedef.ref = raw_dict.get('$ref', '')
    typedef.description = raw_dict.get('description', '').strip()
    typedef.type = raw_dict.get('type', '')
    typedef.format = raw_dict.get('format', None)
    typedef.pattern = raw_dict.get('pattern', '')
    typedef.__lineno__ = raw_dict.lineno

    errors = []  # type: List[str]

    for prop_name, prop_dict in raw_dict.get('properties', RawDict()).items():
        prop_typedef, prop_errors = _parse_typedef(raw_dict=prop_dict)

        errors.extend(['in property {!r}: {}'.format(prop_name, error) for error in prop_errors])
        typedef.properties[prop_name] = prop_typedef

    typedef.required = raw_dict.get('required', [])

    # check that all the required are well-defined
    for prop_name in typedef.required:
        if prop_name not in typedef.properties:
            errors.append("required property not defined: {!r}".format(prop_name))

    if 'additionalProperties' in raw_dict:
        add_prop_dict = raw_dict['additionalProperties']
        add_prop_typedef, add_prop_errors = _parse_typedef(raw_dict=add_prop_dict)

        errors.extend(['in additionalProperties: {}'.format(error) for error in add_prop_errors])
        typedef.additional_properties = add_prop_typedef

    if 'items' in raw_dict:
        items_dict = raw_dict['items']
        items_typedef, items_errors = _parse_typedef(raw_dict=items_dict)

        errors.extend(['in items: {}'.format(error) for error in items_errors])
        typedef.items = items_typedef

    if 'allOf' in raw_dict:
        all_of_list = raw_dict['allOf']
        assert isinstance(all_of_list, list), \
            "Unexpected non-list allOf: {!r}; is there a problem with Swagger JSON schema?".format(all_of_list)

        super_typedefs = []  # type: List[Typedef]
        for i, super_typedef_raw in enumerate(all_of_list):
            super_typedef, super_typedef_errors = _parse_typedef(raw_dict=super_typedef_raw)
            if super_typedef_errors:
                errors.extend("In super definition {} of allOf: {}".format(i, err) for err in super_typedef_errors)
            else:
                super_typedefs.append(super_typedef)

        typedef.all_of = super_typedefs

    if typedef.type == 'number':
        if typedef.format is not None and typedef.format not in ['float', 'double']:
            errors.append("Unexpected format for type 'number': {!r}".format(typedef.format))

    elif typedef.type == 'integer':
        if typedef.format is not None and typedef.format not in ['int32', 'int64']:
            errors.append("Unexpected format for type 'integer': {!r}".format(typedef.format))

    typedef.raw_dict = raw_dict

    return typedef, errors


def _parse_parameter(raw_dict: RawDict) -> Tuple[Parameter, List[str]]:
    """
    Parse a parameter from the raw dictionary of the Swagger spec.

    :param raw_dict: raw dictionary of the Swagger spec
    :return: (parsed parameter, parsing errors if any)
    """
    param = Parameter()
    param.name = raw_dict.get('name', '')
    param.in_what = raw_dict.get('in', '')
    param.description = raw_dict.get('description', '').strip()
    param.required = raw_dict.get('required', False)
    param.type = raw_dict.get('type', '')
    param.format = raw_dict.get('format', '')
    param.pattern = raw_dict.get('pattern', '')
    param.ref = raw_dict.get('$ref', '')
    param.__lineno__ = raw_dict.lineno

    errors = []  # type: List[str]

    if 'schema' in raw_dict:
        schema_dict = raw_dict['schema']

        typedef, schema_errors = _parse_typedef(raw_dict=schema_dict)
        param.schema = typedef
        errors.extend(['in schema: {}'.format(error) for error in schema_errors])

    param.raw_dict = raw_dict

    if param.in_what == 'body' and param.schema is None:
        errors.append('parameter in body, but no schema')

    if 'default' in raw_dict:
        errors.append('default values for parameters are not supported')

    return param, errors


def _parse_response(raw_dict: RawDict) -> Tuple[Response, List[str]]:
    """
    Parse an endpoint response from the raw dictionary of the Swagger spec.

    :param raw_dict: raw dictionary of the Swagger spec
    :return: (parsed response, parsing errors if any)
    """
    resp = Response()
    errors = []  # type: List[str]

    resp.description = raw_dict.get('description', '').strip()
    resp.type = raw_dict.get('type', '')
    resp.format = raw_dict.get('format', '')
    resp.pattern = raw_dict.get('pattern', '')
    resp.__lineno__ = raw_dict.lineno

    if 'schema' in raw_dict:
        schema_dict = raw_dict['schema']

        typedef, schema_errors = _parse_typedef(raw_dict=schema_dict)
        resp.schema = typedef
        errors.extend(['in schema: {}'.format(error) for error in schema_errors])

    resp.raw_dict = raw_dict

    return resp, errors


def _parse_method(raw_dict: RawDict) -> Tuple[Method, List[str]]:
    """
    Parse an endpoint method from the raw dictionary of the Swagger spec.

    :param raw_dict: raw dictionary of the Swagger spec
    :return: (parsed method, parsing errors if any)
    """
    mth = Method()
    errors = []  # type: List[str]

    mth.operation_id = raw_dict.get('operationId', '')
    if mth.operation_id == '':
        errors.append('missing operationId')

    mth.tags = raw_dict.get('tags', [])
    mth.description = raw_dict.get('description', '').strip()
    mth.x_swagger_to_skip = raw_dict.get('x-swagger-to-skip', False)

    mth.produces = raw_dict.get('produces', None)
    mth.consumes = raw_dict.get('consumes', None)
    mth.__lineno__ = raw_dict.lineno

    for i, param_dict in enumerate(raw_dict.get('parameters', [])):
        param, param_errors = _parse_parameter(raw_dict=param_dict)
        errors.extend(['in parameter {} (name: {!r}): {}'.format(i, param.name, error) for error in param_errors])

        param.method = mth

        mth.parameters.append(param)

    for resp_code, resp_dict in raw_dict.get('responses', RawDict()).items():
        resp, resp_errors = _parse_response(raw_dict=resp_dict)
        errors.extend(['in response {!r}: {}'.format(resp_code, error) for error in resp_errors])

        resp.code = resp_code
        mth.responses[str(resp_code)] = resp

    mth.raw_dict = raw_dict

    return mth, errors


def _parse_path(raw_dict: RawDict) -> Tuple[Path, List[str]]:
    """
    Parse an endpoint path from the dictionary.

    :param path_id: path identifier
    :param raw_dict: raw dictionary of the Swagger spec
    :return: (parsed path, parsing errors if any)
    """
    pth = Path()
    errors = []  # type: List[str]

    for key, value in raw_dict.items():
        # These are common parameters for all the methods of the path,
        # see https://swagger.io/docs/specification/2-0/describing-parameters/,
        # Section "Common Parameters"
        if key == 'parameters':
            assert isinstance(value, list), \
                'Expected a list for the common parameters, but got: {}'.format(json.dumps(value))

            for i, param_raw_dict in enumerate(value):
                param, param_errors = _parse_parameter(raw_dict=param_raw_dict)
                errors.extend([
                    'in common parameter {} {}: {}'.format(i, json.dumps(param_raw_dict), err) for err in param_errors
                ])
                if not param_errors:
                    pth.parameters.append(param)
        else:
            method, method_errors = _parse_method(raw_dict=value)
            method.identifier = key
            method.path = pth
            errors.extend(['in method {!r}: {}'.format(key, error) for error in method_errors])

            if not method_errors:
                pth.methods.append(method)

    pth.raw_dict = raw_dict

    return pth, errors


def parse_yaml(stream: Any) -> Tuple[Swagger, List[str]]:
    """
    Parse the Swagger specification from the given text.

    :param stream: YAML representation of the Swagger spec satisfying file interface
    :return: (parsed Swagger specification, parsing errors if any)
    """
    pass  # needed for pydocstyle

    # Adapted from https://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
    # and https://stackoverflow.com/questions/13319067/parsing-yaml-return-with-line-number

    class Loader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node, deep=False):
        loader.flatten_mapping(node)
        mapping = yaml.constructor.Constructor.construct_pairs(loader, node, deep=deep)

        # Enforce keys to be strings,
        # see https://stackoverflow.com/questions/50045617/yaml-load-force-dict-keys-to-strings

        data = collections.OrderedDict([(str(k), v) for k, v in mapping])

        return RawDict(adict=data, source=stream.name, lineno=node.start_mark.line)

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

    raw_dict = cast(RawDict, yaml.load(stream, Loader))

    ##
    # Validate the raw dict against the JSON schema
    ##

    try:
        jsonschema.Draft4Validator.check_schema(swagger_to.swaggerjsonschema.SCHEMA)
        jsonschema.Draft4Validator(swagger_to.swaggerjsonschema.SCHEMA).validate(raw_dict)
    except jsonschema.exceptions.ValidationError as err:
        jsonized_parts = map(json.dumps, list(err.relative_path))
        # yapf: disable
        return (
            Swagger(),
            [
                '{}:{}\n\n{}'.format(
                    '/'.join(jsonized_parts), str(err),
                    ("We used the JSON schema of OpenAPI 2 from: "
                     "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/"
                     "88cd94419e117b154b67b834fa8e471bb98bd346/schemas/v2.0/schema.json"
                    )
                )
            ]
        ) # yapf: enable

    ##
    # Parse
    ##

    swagger = Swagger()

    errors = []  # type: List[str]

    if 'tags' in raw_dict:
        if len(raw_dict['tags']) > 0:
            for tag in raw_dict['tags']:
                for key, value in tag.items():
                    if key == 'name':
                        swagger.name = value

    if swagger.name == '':
        errors.append('missing tag "name" in the swagger specification')

    swagger.base_path = raw_dict.get('basePath', '')

    swagger.produces = raw_dict.get('produces', None)
    swagger.consumes = raw_dict.get('consumes', None)

    for path_id, path_dict in raw_dict.get('paths', RawDict()).items():
        path, path_errors = _parse_path(raw_dict=path_dict)
        path.identifier = path_id
        path.swagger = swagger

        errors.extend(['in path {!r}: {}'.format(path_id, error) for error in path_errors])

        if not path_errors:
            swagger.paths[path_id] = path

    for def_id, def_dict in raw_dict.get('definitions', RawDict()).items():
        typedef, def_errors = _parse_typedef(raw_dict=def_dict)

        errors.extend(['in definition {!r}: {}'.format(def_id, error) for error in def_errors])

        if not def_errors:
            swagger.definitions[def_id] = Definition(identifier=def_id, typedef=typedef, swagger=swagger)

    for param_id, param_dict in raw_dict.get('parameters', RawDict()).items():
        param, param_errors = _parse_parameter(raw_dict=param_dict)

        errors.extend(['in parameter {!r}: {}'.format(param_id, error) for error in param_errors])

        if not param_errors:
            swagger.parameters[param_id] = param

    swagger.raw_dict = raw_dict

    return swagger, errors


def parse_yaml_file(path: Union[str, pathlib.Path]) -> Tuple[Swagger, List[str]]:
    """
    Parse the Swagger specification from the given file.

    :param path: path to the .yaml file
    :return: (parsed Swagger specification, parsing errors if any)
    """
    with open(str(path), 'rt', encoding='utf-8') as fid:
        return parse_yaml(stream=fid)
