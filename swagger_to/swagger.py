"""
Swagger representation
"""
import collections
import sys
from typing import List, Optional, MutableMapping, Any, Tuple  # pylint: disable=unused-import

try:
    import yaml
except ImportError as err:
    print("Package pyyaml was not installed. pip3 install pyyaml?")
    sys.exit(1)

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors


class Typedef:
    def __init__(self):
        self.ref = ''
        self.description = ''
        self.type = ''
        self.format = ''
        self.pattern = ''
        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Typedef]
        self.required = []  # type: List[str]
        self.items = None  # type: Optional[Typedef]
        self.additional_properties = None  # type: Optional[Typedef]

        # original specification dictionary, if available; not deep-copied, do not modify
        self.adict = collections.OrderedDict()  # type: MutableMapping[str, Any]


class Definition:
    def __init__(self):
        self.identifier = ''
        self.typedef = None  # type: Optional[Typedef]
        self.swagger = None  # type: Optional[Swagger]

        # original specification dictionary, if available; not deep-copied, do not modify
        self.adict = collections.OrderedDict()  # type: MutableMapping[str, Any]


class Parameter:
    def __init__(self):
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

        # original specification dictionary, if available; not deep-copied, do not modify
        self.adict = collections.OrderedDict()  # type: MutableMapping[str, Any]


class Response:
    def __init__(self):
        self.code = ''
        self.description = ''
        self.schema = None  # type: Optional[Typedef]
        self.type = ''
        self.format = ''
        self.pattern = ''

        # original specification dictionary, if available; not deep-copied, do not modify
        self.adict = collections.OrderedDict()  # type: MutableMapping[str, Any]


class Method:
    def __init__(self):
        self.identifier = ''
        self.operation_id = ''
        self.tags = []  # type: List[str]
        self.description = ''
        self.parameters = []  # type: List[Parameter]
        self.responses = collections.OrderedDict()  # type: MutableMapping[str, Response]
        self.path = None  # type: Optional[Path]
        self.produces = []  # type: List[str]
        self.consumes = []  # type: List[str]
        self.x_pqry_no_go = False

        # original specification dictionary, if available; not deep-copied, do not modify
        self.adict = collections.OrderedDict()  # type: MutableMapping[str, Any]


class Path:
    def __init__(self):
        self.identifier = ''
        self.methods = []  # type: List[Method]
        self.swagger = None  # type: Optional[Swagger]

        # original specification dictionary, if available; not deep-copied, do not modify
        self.adict = collections.OrderedDict()  # type: MutableMapping[str, Any]


class Swagger:
    def __init__(self):
        self.name = ""
        self.base_path = ""
        self.description = ""
        self.paths = collections.OrderedDict()  # type: MutableMapping[str, Path]
        self.definitions = collections.OrderedDict()  # type: MutableMapping[str, Definition]
        self.parameters = collections.OrderedDict()  # type: MutableMapping[str, Parameter]

        self.adict = collections.OrderedDict()  # type: MutableMapping[str, Any]


def parse_typedef(adict: MutableMapping[str, Any]) -> Tuple[Typedef, List[str]]:
    typedef = Typedef()
    typedef.ref = adict.get('$ref', '')
    typedef.description = adict.get('description', '').strip()
    typedef.type = adict.get('type', '')
    typedef.format = adict.get('format', '')
    typedef.pattern = adict.get('pattern', '')

    errors = []  # type: List[str]

    for prop_name, prop_dict in adict.get('properties', collections.OrderedDict()).items():
        prop_typedef, prop_errors = parse_typedef(adict=prop_dict)

        errors.extend(['in property {!r}: {}'.format(prop_name, error) for error in prop_errors])
        typedef.properties[prop_name] = prop_typedef

    typedef.required = adict.get('required', [])

    # check that all the required are well-defined
    for prop_name in typedef.required:
        if prop_name not in typedef.properties:
            errors.append("required property not defined: {!r}".format(prop_name))

    if 'additionalProperties' in adict:
        add_prop_dict = adict['additionalProperties']
        add_prop_typedef, add_prop_errors = parse_typedef(adict=add_prop_dict)

        errors.extend(['in additionalProperties: {}'.format(error) for error in add_prop_errors])
        typedef.additional_properties = add_prop_typedef

    if 'items' in adict:
        items_dict = adict['items']
        items_typedef, items_errors = parse_typedef(adict=items_dict)

        errors.extend(['in items: {}'.format(error) for error in items_errors])
        typedef.items = items_typedef

    if typedef.type == 'number':
        if typedef.format not in ['float', 'double']:
            errors.append("Unexpected format for type 'number': {!r}".format(typedef.format))

    elif typedef.type == 'integer':
        if typedef.format not in ['int32', 'int64']:
            errors.append("Unexpected format for type 'integer': {!r}".format(typedef.format))

    typedef.adict = adict

    return typedef, errors


def parse_parameter(adict: MutableMapping[str, Any]) -> Tuple[Parameter, List[str]]:
    """
    Parses a parameter from the dictionary.

    :param adict: to be parsed
    :return: parameter, list of errors
    """

    param = Parameter()
    param.name = adict.get('name', '')
    param.in_what = adict.get('in', '')
    param.description = adict.get('description', '').strip()
    param.required = adict.get('required', False)
    param.type = adict.get('type', '')
    param.format = adict.get('format', '')
    param.pattern = adict.get('pattern', '')
    param.ref = adict.get('$ref', '')

    errors = []  # type: List[str]

    if 'schema' in adict:
        schema_dict = adict['schema']

        typedef, schema_errors = parse_typedef(adict=schema_dict)
        param.schema = typedef
        errors.extend(['in schema: {}'.format(error) for error in schema_errors])

    param.adict = adict

    if param.in_what == 'body' and param.schema is None:
        errors.append('parameter in body, but no schema')

    return param, errors


def parse_response(adict: MutableMapping[str, Any]) -> Tuple[Response, List[str]]:
    """
    Parses a response from the dictionary.

    :param adict: to be parsed
    :return: response, list of errors
    """
    resp = Response()
    errors = []  # type: List[str]

    resp.description = adict.get('description', '').strip()
    resp.type = adict.get('type', '')
    resp.format = adict.get('format', '')
    resp.pattern = adict.get('pattern', '')

    if 'schema' in adict:
        schema_dict = adict['schema']

        typedef, schema_errors = parse_typedef(adict=schema_dict)
        resp.schema = typedef
        errors.extend(['in schema: {}'.format(error) for error in schema_errors])

    resp.adict = adict

    return resp, errors


def parse_method(adict: MutableMapping[str, Any]) -> Tuple[Method, List[str]]:
    """
    Parses a method from the dictionary.

    :param adict: to be parsed
    :return: method, list of errors
    """
    mth = Method()
    errors = []  # type: List[str]

    mth.operation_id = adict.get('operationId', '')
    if mth.operation_id == '':
        errors.append('missing operationId')

    mth.tags = adict.get('tags', [])
    mth.description = adict.get('description', '').strip()
    mth.x_pqry_no_go = adict.get('x-pqry-no-go', False)

    mth.produces = adict.get('produces', [])
    mth.consumes = adict.get('consumes', [])

    for i, param_dict in enumerate(adict.get('parameters', [])):
        param, param_errors = parse_parameter(adict=param_dict)
        errors.extend(['in parameter {} (name: {!r}): {}'.format(i, param.name, error) for error in param_errors])

        mth.parameters.append(param)

    for resp_code, resp_dict in adict.get('responses', collections.OrderedDict()).items():
        resp, resp_errors = parse_response(adict=resp_dict)
        errors.extend(['in response {!r}: {}'.format(resp_code, error) for error in resp_errors])

        resp.code = resp_code
        mth.responses[str(resp_code)] = resp

    mth.adict = adict

    return mth, errors


def parse_path(adict: MutableMapping[str, Any]) -> Tuple[Path, List[str]]:
    """
    Parses a path from the dictionary.

    :param path_id: identifier
    :param adict: to be parsed
    :return: path, list of errors
    """
    pth = Path()
    errors = []  # type: List[str]

    for method_id, method_dict in adict.items():
        method, method_errors = parse_method(adict=method_dict)
        method.identifier = method_id
        method.path = pth
        errors.extend(['in method {!r}: {}'.format(method_id, error) for error in method_errors])

        if not method_errors:
            pth.methods.append(method)

    pth.adict = adict

    return pth, errors


def parse_yaml(stream: Any) -> Tuple[Swagger, List[str]]:
    """
    Parses the Swagger specification from the given text.

    :param stream: YAML representation of the Swagger spec satisfying file interface
    :return: Swagger specification, list of errors
    """
    # adapted from https://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
    object_pairs_hook = collections.OrderedDict

    class OrderedLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

    adict = yaml.load(stream, OrderedLoader)

    swagger = Swagger()

    errors = []  # type: List[str]

    if 'tags' in adict:
        if len(adict['tags']) > 0:
            for tag in adict['tags']:
                for key, value in tag.items():
                    if key == 'name':
                        swagger.name = value

    if swagger.name == '':
        errors.append('missing tag "name" in the swagger specification')

    swagger.base_path = adict.get('basePath', '')

    for path_id, path_dict in adict.get('paths', collections.OrderedDict()).items():
        path, path_errors = parse_path(adict=path_dict)
        path.identifier = path_id
        path.swagger = swagger

        errors.extend(['in path {!r}: {}'.format(path_id, error) for error in path_errors])

        if not path_errors:
            swagger.paths[path_id] = path

    for def_id, def_dict in adict.get('definitions', collections.OrderedDict()).items():
        typedef, def_errors = parse_typedef(adict=def_dict)

        errors.extend(['in definition {!r}: {}'.format(def_id, error) for error in def_errors])

        adef = Definition()
        adef.swagger = swagger
        adef.identifier = def_id
        adef.typedef = typedef

        if not def_errors:
            swagger.definitions[def_id] = adef

    for param_id, param_dict in adict.get('parameters', collections.OrderedDict()).items():
        param, param_errors = parse_parameter(adict=param_dict)

        errors.extend(['in parameter {!r}: {}'.format(param_id, error) for error in param_errors])

        if not param_errors:
            swagger.parameters[param_id] = param

    swagger.adict = adict

    return swagger, errors


def parse_yaml_file(path: str) -> Tuple[Swagger, List[str]]:
    """
    Parses the Swagger specification from the given file.

    :param path: to the .yaml file
    :return: Swagger specification, list of errors
    """
    with open(path, 'rt') as fid:
        return parse_yaml(stream=fid)
