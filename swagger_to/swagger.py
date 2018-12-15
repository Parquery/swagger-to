"""Parse Swagger spec."""

import collections
import pathlib
from typing import List, Optional, MutableMapping, Any, Tuple, Union  # pylint: disable=unused-import

import yaml
from yaml.composer import Composer
from yaml.constructor import Constructor

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches


class RawDict:
    """Represent a raw dictionary from a Swagger spec file."""

    def __init__(self, adict: MutableMapping[str, Any] = collections.OrderedDict(), source: str = '',
                 lineno: int = 0) -> None:
        """Initialize with the given values."""
        self.adict = adict
        self.source = source
        self.lineno = lineno


class Typedef:
    """Represent a type definition in a Swagger spec."""

    def __init__(self):
        """Initialize with defaults."""
        self.ref = ''
        self.description = ''
        self.type = ''
        self.format = ''
        self.pattern = ''
        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Typedef]
        self.required = []  # type: List[str]
        self.items = None  # type: Optional[Typedef]
        self.additional_properties = None  # type: Optional[Typedef]
        self.__lineno__ = 0

        # original specification dictionary, if available; not deep-copied, do not modify
        self.raw_dict = None  # type: RawDict


class Definition:
    """Represent an identifiable data type from the Swagger spec."""

    def __init__(self):
        """Initialize with defaults."""
        self.identifier = ''
        self.typedef = None  # type: Optional[Typedef]
        self.swagger = None  # type: Optional[Swagger]

        # original specification dictionary, if available; not deep-copied, do not modify
        self.raw_dict = None  # type: Optional[RawDict]


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
        self.produces = []  # type: List[str]
        self.consumes = []  # type: List[str]
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

        self.raw_dict = None  # type: Optional[RawDict]


def _parse_typedef(raw_dict: RawDict) -> Tuple[Typedef, List[str]]:
    """
    Parse the type definition from the raw dictionary in the Swagger spec.

    :param raw_dict: raw dictionary of the Swagger spec
    :return: (parsed type definition, parsing errors if any)
    """
    adict = raw_dict.adict

    typedef = Typedef()
    typedef.ref = adict.get('$ref', '')
    typedef.description = adict.get('description', '').strip()
    typedef.type = adict.get('type', '')
    typedef.format = adict.get('format', '')
    typedef.pattern = adict.get('pattern', '')
    typedef.__lineno__ = raw_dict.lineno

    errors = []  # type: List[str]

    for prop_name, prop_dict in adict.get('properties', RawDict()).adict.items():
        prop_typedef, prop_errors = _parse_typedef(raw_dict=prop_dict)

        errors.extend(['in property {!r}: {}'.format(prop_name, error) for error in prop_errors])
        typedef.properties[prop_name] = prop_typedef

    typedef.required = adict.get('required', [])

    # check that all the required are well-defined
    for prop_name in typedef.required:
        if prop_name not in typedef.properties:
            errors.append("required property not defined: {!r}".format(prop_name))

    if 'additionalProperties' in adict:
        add_prop_dict = adict['additionalProperties']
        add_prop_typedef, add_prop_errors = _parse_typedef(raw_dict=add_prop_dict)

        errors.extend(['in additionalProperties: {}'.format(error) for error in add_prop_errors])
        typedef.additional_properties = add_prop_typedef

    if 'items' in adict:
        items_dict = adict['items']
        items_typedef, items_errors = _parse_typedef(raw_dict=items_dict)

        errors.extend(['in items: {}'.format(error) for error in items_errors])
        typedef.items = items_typedef

    if typedef.type == 'number':
        if typedef.format not in ['float', 'double']:
            errors.append("Unexpected format for type 'number': {!r}".format(typedef.format))

    elif typedef.type == 'integer':
        if typedef.format not in ['int32', 'int64']:
            errors.append("Unexpected format for type 'integer': {!r}".format(typedef.format))

    typedef.raw_dict = raw_dict

    return typedef, errors


def _parse_parameter(raw_dict: RawDict) -> Tuple[Parameter, List[str]]:
    """
    Parse a parameter from the raw dictionary of the Swagger spec.

    :param raw_dict: raw dictionary of the Swagger spec
    :return: (parsed parameter, parsing errors if any)
    """
    adict = raw_dict.adict

    param = Parameter()
    param.name = adict.get('name', '')
    param.in_what = adict.get('in', '')
    param.description = adict.get('description', '').strip()
    param.required = adict.get('required', False)
    param.type = adict.get('type', '')
    param.format = adict.get('format', '')
    param.pattern = adict.get('pattern', '')
    param.ref = adict.get('$ref', '')
    param.__lineno__ = raw_dict.lineno

    errors = []  # type: List[str]

    if 'schema' in adict:
        schema_dict = adict['schema']

        typedef, schema_errors = _parse_typedef(raw_dict=schema_dict)
        param.schema = typedef
        errors.extend(['in schema: {}'.format(error) for error in schema_errors])

    param.raw_dict = raw_dict

    if param.in_what == 'body' and param.schema is None:
        errors.append('parameter in body, but no schema')

    if 'default' in adict:
        errors.append('default values for parameters are not supported')

    return param, errors


def _parse_response(raw_dict: RawDict) -> Tuple[Response, List[str]]:
    """
    Parse an endpoint response from the raw dictionary of the Swagger spec.

    :param raw_dict: raw dictionary of the Swagger spec
    :return: (parsed response, parsing errors if any)
    """
    adict = raw_dict.adict

    resp = Response()
    errors = []  # type: List[str]

    resp.description = adict.get('description', '').strip()
    resp.type = adict.get('type', '')
    resp.format = adict.get('format', '')
    resp.pattern = adict.get('pattern', '')
    resp.__lineno__ = raw_dict.lineno

    if 'schema' in adict:
        schema_dict = adict['schema']

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
    adict = raw_dict.adict

    mth.operation_id = adict.get('operationId', '')
    if mth.operation_id == '':
        errors.append('missing operationId')

    mth.tags = adict.get('tags', [])
    mth.description = adict.get('description', '').strip()
    mth.x_swagger_to_skip = adict.get('x-swagger-to-skip', False)

    mth.produces = adict.get('produces', [])
    mth.consumes = adict.get('consumes', [])
    mth.__lineno__ = raw_dict.lineno

    for i, param_dict in enumerate(adict.get('parameters', [])):
        param, param_errors = _parse_parameter(raw_dict=param_dict)
        errors.extend(['in parameter {} (name: {!r}): {}'.format(i, param.name, error) for error in param_errors])

        param.method = mth

        mth.parameters.append(param)

    for resp_code, resp_dict in adict.get('responses', RawDict()).adict.items():
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

    for method_id, method_dict in raw_dict.adict.items():
        method, method_errors = _parse_method(raw_dict=method_dict)
        method.identifier = method_id
        method.path = pth
        errors.extend(['in method {!r}: {}'.format(method_id, error) for error in method_errors])

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
    # adapted from https://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
    # and https://stackoverflow.com/questions/13319067/parsing-yaml-return-with-line-number

    object_pairs_hook = collections.OrderedDict

    class OrderedLoader(yaml.SafeLoader):
        def compose_node(self, parent, index):
            # the line number where the previous token has ended (plus empty lines)
            node = Composer.compose_node(self, parent, index)
            node.__lineno__ = self.line + 1
            return node

    def construct_mapping(loader, node, deep=False):
        loader.flatten_mapping(node)
        mapping = Constructor.construct_pairs(loader, node, deep=deep)

        ordered_hook = object_pairs_hook(mapping)

        # assert not hasattr(ordered_hook, "__lineno__"), \
        #     "Expected ordered mapping to have no __lineno__ attribute set before"
        # setattr(ordered_hook, "__lineno__", node.__lineno__)

        return RawDict(adict=ordered_hook, source=stream.name, lineno=node.__lineno__)

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

    raw_dict = yaml.load(stream, OrderedLoader)
    swagger = Swagger()

    errors = []  # type: List[str]

    adict = raw_dict.adict
    if 'tags' in adict:
        if len(adict['tags']) > 0:
            for tag in adict['tags']:
                for key, value in tag.adict.items():
                    if key == 'name':
                        swagger.name = value

    if swagger.name == '':
        errors.append('missing tag "name" in the swagger specification')

    swagger.base_path = adict.get('basePath', '')

    for path_id, path_dict in adict.get('paths', RawDict()).adict.items():
        path, path_errors = _parse_path(raw_dict=path_dict)
        path.identifier = path_id
        path.swagger = swagger

        errors.extend(['in path {!r}: {}'.format(path_id, error) for error in path_errors])

        if not path_errors:
            swagger.paths[path_id] = path

    for def_id, def_dict in adict.get('definitions', RawDict()).adict.items():
        typedef, def_errors = _parse_typedef(raw_dict=def_dict)

        errors.extend(['in definition {!r}: {}'.format(def_id, error) for error in def_errors])

        adef = Definition()
        adef.swagger = swagger
        adef.identifier = def_id
        adef.typedef = typedef

        if not def_errors:
            swagger.definitions[def_id] = adef

    for param_id, param_dict in adict.get('parameters', RawDict()).adict.items():
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
    with open(str(path), 'rt') as fid:
        return parse_yaml(stream=fid)
