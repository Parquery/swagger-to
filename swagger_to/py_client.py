#!/usr/bin/env python3
"""Generate a Python client from Swagger specification."""

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches
# pylint: disable=too-many-statements,too-many-lines

import collections
from typing import MutableMapping, Union, Set, List, TextIO, Optional  # pylint: disable=unused-import

import icontract

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
        self.name = ''
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
        self.query_parameters = []  # type: List[Parameter]
        self.path_parameters = []  # type: List[Parameter]
        self.formdata_parameters = []  # type: List[Parameter]
        self.file_parameters = []  # type: List[Parameter]

        self.responses = collections.OrderedDict()  # type: MutableMapping[str, Response]
        self.produces = []  # type: List[str]


def anonymous_or_get_typedef(intermediate_typedef: swagger_to.intermediate.Typedef,
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
            raise KeyError("Intermediate typedef not found in the translated typedefs: {!r}".format(
                intermediate_typedef.identifier))

        return typedefs[intermediate_typedef.identifier]

    return to_typedef(intermediate_typedef=intermediate_typedef)


def to_typedef(intermediate_typedef: swagger_to.intermediate.Typedef) -> Typedef:
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
            raise NotImplementedError("Converting intermediate type to Python is not supported: {}".format(
                intermediate_typedef.type))

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Arraydef):
        typedef = Listdef()
        typedef.items = to_typedef(intermediate_typedef=intermediate_typedef.items)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Dictdef()
        typedef.values = to_typedef(intermediate_typedef=intermediate_typedef.values)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Classdef()

        for intermediate_prop in intermediate_typedef.properties.values():
            attr = Attribute()
            attr.description = intermediate_prop.description
            attr.name = intermediate_prop.name
            attr.typedef = to_typedef(intermediate_typedef=intermediate_prop.typedef)
            attr.required = intermediate_prop.required
            attr.classdef = typedef

            typedef.attributes[attr.name] = attr

        typedef.attributes = collections.OrderedDict(
            sorted(list(typedef.attributes.items()), key=lambda kv: not kv[1].required))
    else:
        raise NotImplementedError("Converting intermediate typedef to Python is not supported: {!r}".format(
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

        typedef = to_typedef(intermediate_typedef=intermediate_typedef)
        typedefs[typedef.identifier] = typedef

    return typedefs


def to_parameter(intermediate_parameter: swagger_to.intermediate.Parameter,
                 typedefs: MutableMapping[str, Typedef]) -> Parameter:
    """
    Translate an endpoint parameter from the intermediate to a Python representation.

    :param intermediate_parameter: intermediate representation of a parameter
    :param typedefs: table of type definitions in Python representation
    :return: Python representation of the parameter
    """
    param = Parameter()
    param.name = intermediate_parameter.name
    param.typedef = anonymous_or_get_typedef(intermediate_typedef=intermediate_parameter.typedef, typedefs=typedefs)
    param.required = intermediate_parameter.required
    param.description = intermediate_parameter.description
    return param


def to_response(intermediate_response: swagger_to.intermediate.Response,
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
        anonymous_or_get_typedef(intermediate_typedef=intermediate_response.typedef, typedefs=typedefs)
    resp.description = intermediate_response.description
    return resp


def to_request(endpoint: swagger_to.intermediate.Endpoint, typedefs: MutableMapping[str, Typedef]) -> Request:
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

    for intermediate_param in endpoint.parameters:
        param = to_parameter(intermediate_parameter=intermediate_param, typedefs=typedefs)

        if isinstance(param.typedef, Filedef):
            req.file_parameters.append(param)
        elif intermediate_param.in_what == 'body':
            if req.body_parameter is not None:
                raise KeyError("Duplicate body parameters in an endpoint: {} {}".format(
                    req.body_parameter.name, intermediate_param.name))

            req.body_parameter = param
        elif intermediate_param.in_what == 'query':
            req.query_parameters.append(param)
        elif intermediate_param.in_what == 'path':
            req.path_parameters.append(param)
        elif intermediate_param.in_what == 'formData':
            req.formdata_parameters.append(param)
        else:
            raise NotImplementedError("Unsupported parameter 'in' to Python translation: {}".format(
                intermediate_param.in_what))

        req.parameters.append(param)

    # parameters are sorted so that first come the required ones; python requires the optional parameters to come
    # at the end.
    req.parameters.sort(key=lambda param: not param.required)

    for code, intermediate_resp in endpoint.responses.items():
        req.responses[code] = to_response(intermediate_response=intermediate_resp, typedefs=typedefs)

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
        requests.append(to_request(endpoint=endpoint, typedefs=typedefs))

    return requests


INDENT = ' ' * 4


def write_imports(import_set: Set[str], fid: TextIO) -> None:
    """Write import statements."""
    import_lst = sorted(list(import_set))
    for import_stmt in sorted(import_lst):
        fid.write('import ' + '{}\n'.format(import_stmt))
    if len(import_lst) > 0:
        fid.write("\n\n")


def type_expression(typedef: Typedef, path: Optional[str] = None) -> str:
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
        return 'List[' + type_expression(typedef=typedef.items, path=str(path) + '.items') + "]"
    elif isinstance(typedef, Dictdef):
        return 'Dict[str, ' + type_expression(typedef=typedef.values, path=str(path) + '.values') + "]"
    elif isinstance(typedef, Classdef):
        if typedef.identifier == '':
            raise NotImplementedError(
                "Translating an anonymous class to a type expression is not supported: {}".format(path))

        return typedef.identifier
    else:
        raise NotImplementedError("Translating the typedef to a type expression is not supported: {!r}: {}".format(
            type(typedef), path))


def attribute_as_argument(attribute: Attribute) -> str:
    """
    Represent the instance attribute of a class as an argument to a function (e.g., ``__init__``).

    :param attribute: Python representation of the instance attribute of a class
    :return: Python code
    """
    argtype = type_expression(typedef=attribute.typedef, path=attribute.classdef.identifier + "." + attribute.name)

    if not attribute.required:
        return '{}: Optional[{}] = None'.format(attribute.name, argtype)

    return '{}: {}'.format(attribute.name, argtype)


def write_header(service_name: str, fid: TextIO) -> None:
    """Write the header of the client module."""
    fid.write('#!bin/bash/python3\n')
    fid.write('# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n')
    fid.write('"""Implements the client for {}."""\n\n'.format(service_name))
    fid.write("# pylint: skip-file\n")
    fid.write("# pydocstyle: add-ignore=D105,D107,D401\n\n")

    fid.write('import contextlib\n')
    fid.write("from typing import Any, BinaryIO, Dict, List, Optional\n\n")
    fid.write("import requests\n")
    fid.write("import requests.auth\n")


def write_footer(fid: TextIO) -> None:
    """Write the footer of the client module."""
    fid.write('# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!')


def write_comment(comment: str, indent: str, fid: TextIO) -> None:
    """Write the comment at the given indention."""
    lines = comment.strip().splitlines()
    for i, line in enumerate(lines):
        rstripped = line.rstrip()
        if len(rstripped) > 0:
            fid.write(indent + '# {}'.format(rstripped))
        else:
            fid.write(indent + '#')

        if i < len(lines) - 1:
            fid.write('\n')


def write_docstring(docstring: str, indent: str, fid: TextIO) -> None:
    """Write the docstring at the given indention."""
    if not docstring:
        raise ValueError("Unexpected empty docstring")

    docstring = docstring[0].upper() + docstring[1:]
    docstring_lines = docstring.splitlines()

    if len(docstring_lines) == 1:
        fid.write(''.join([indent, '"""', docstring, '"""']))
        return

    fid.write(indent + '"""\n')
    for line in docstring_lines:
        if line.strip():
            fid.write(indent)
            fid.write(line)
        fid.write('\n')

    fid.write('\n')
    fid.write(indent + '"""')


def write_class(classdef: Classdef, fid: TextIO) -> None:
    """Write the class defintiion to the client module."""
    if classdef.identifier == '':
        raise ValueError("Expected a classdef with an identifier, but got a classdef with an empty identifier.")

    fid.write("class {}:\n".format(classdef.identifier))
    if classdef.description:
        write_docstring(docstring=classdef.description, indent=INDENT, fid=fid)
        fid.write('\n\n')

    if not classdef.attributes:
        fid.write(INDENT + 'pass')
        return

    prefix = INDENT + 'def __init__(self'
    suffix = ') -> None:'

    args = []  # type: List[str]
    for attr in classdef.attributes.values():
        args.append(attribute_as_argument(attribute=attr))

    line = prefix + ', ' + ', '.join(args) + suffix
    if len(line) <= 80:
        fid.write(line)
    else:
        fid.write(prefix)
        for arg in args:
            fid.write(',\n')

            fid.write(' ' * (len(prefix) - len('self')) + arg)

        fid.write(suffix)

    fid.write('\n')

    for i, attr in enumerate(classdef.attributes.values()):
        if i > 0:
            fid.write('\n\n')

        if attr.description:
            write_comment(comment=attr.description, indent=INDENT * 2, fid=fid)
            fid.write('\n')
        fid.write(INDENT * 2 + 'self.{0} = {0}'.format(attr.name))

    fid.write('\n\n')
    fid.write(INDENT + 'def to_jsonable(self) -> Dict[str, Any]:\n')
    fid.write(INDENT * 2 + '"""\n')
    fid.write(INDENT * 2 + 'Dispatches the conversion to {}_to_jsonable.\n\n'.format(
        swagger_to.snake_case(identifier=classdef.identifier)))

    fid.write(INDENT * 2 + ':return: JSON-able representation\n\n')
    fid.write(INDENT * 2 + '"""\n')

    fid.write(INDENT * 2 + 'return {}_to_jsonable(self)'.format(swagger_to.snake_case(identifier=classdef.identifier)))


def default_attribute_value(typedef: Typedef) -> str:
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
        return "[]"
    elif isinstance(typedef, Dictdef):
        return "dict()"
    elif isinstance(typedef, Classdef):
        return "new_{}()".format(swagger_to.snake_case(identifier=typedef.identifier))
    else:
        raise NotImplementedError("Translating the typedef to a default value is not supported: {}".format(typedef))


def write_class_factory_method(classdef: Classdef, fid: TextIO) -> None:
    """Write the class factory method in the client module."""
    fid.write('def new_{}() -> {}:\n'.format(
        swagger_to.snake_case(identifier=classdef.identifier), classdef.identifier))

    fid.write(INDENT + '"""Generates a default instance of {}."""\n'.format(classdef.identifier))

    if not classdef.attributes:
        fid.write(INDENT + "return {}()".format(classdef.identifier))
        return

    prefix = INDENT + 'return {}('.format(classdef.identifier)
    suffix = ')'
    args = []  # type: List[str]
    for attr in classdef.attributes.values():
        if attr.required:
            args.append('{}={}'.format(attr.name, default_attribute_value(typedef=attr.typedef)))

    line = prefix + ', '.join(args) + suffix
    if len(line) <= 80:
        fid.write(line)
    else:
        fid.write(prefix)
        fid.write(args[0])

        for arg in args[1:]:
            fid.write(',\n')
            fid.write(' ' * len(prefix) + arg)

        fid.write(suffix)


def write_from_obj(classdefs: List[Classdef], fid: TextIO):
    """Write the code of the ``from_obj`` function."""
    # yapf: disable
    fid.write('''def from_obj(obj: Any, expected: List[type], path: str = '') -> Any:
    """
    Checks and converts the given obj along the expected types.

    :param obj: to be converted
    :param expected: list of types representing the (nested) structure
    :param path: to the object from the root object
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

        raise ValueError("Expected object of type int or float at {!r}, but got {}.".format(path, type(obj)))

    if exp in [bool, int, str, list, dict]:
        if not isinstance(obj, exp):
            raise ValueError("Expected object of type {} at {!r}, but got {}.".format(exp, path, type(obj)))

    if exp in [bool, int, float, str]:
        return obj

    if exp == list:
        lst = []  # type: List[Any]
        for i, value in enumerate(obj):
            lst.append(from_obj(value, expected=expected[1:], path=path + '[{}]'.format(i)))

        return lst

    if exp == dict:
        adict = dict()  # type: Dict[str, Any]
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError("Expected a key of type str at path {!r}, got: {}".format(path, type(key)))

            adict[key] = from_obj(value, expected=expected[1:], path=path + '["{}"]'.format(key))

        return adict'''.replace(' ' * 4, INDENT))

    for classdef in classdefs:
        fid.write('\n\n')
        fid.write(INDENT + 'if exp == {}:\n'.format(classdef.identifier))
        fid.write(INDENT * 2 + 'return {}_from_obj(obj, path=path)'.format(
            swagger_to.snake_case(classdef.identifier)))

    fid.write('\n\n')

    fid.write(INDENT + 'raise ValueError("Unexpected `expected` type: {}".format(exp))')


def expected_type_expression(typedef: Typedef) -> str:
    """
    Determine the type expression corresponding to the type definition.

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
        return "str"
    elif isinstance(typedef, Bytesdef):
        return "bytes"
    elif isinstance(typedef, Listdef):
        return "list, {}".format(expected_type_expression(typedef=typedef.items))
    elif isinstance(typedef, Dictdef):
        return "dict, {}".format(expected_type_expression(typedef=typedef.values))
    elif isinstance(typedef, Classdef):
        return typedef.identifier
    else:
        raise NotImplementedError(
            "Translating the typedef to an expected type is not supported: {}".format(typedef))


def write_class_from_obj(classdef: Classdef, fid: TextIO) -> None:
    """Write the code of ``{class}_from_obj`` function."""
    fid.write('def {}_from_obj(obj: Any, path: str = "") -> {}:\n'.format(
        swagger_to.snake_case(identifier=classdef.identifier), classdef.identifier))

    fid.write(INDENT + '"""Generates an instance of {} from a dictionary object."""\n'.format(
        classdef.identifier))

    # yapf: disable
    fid.write(INDENT + 'if not isinstance(obj, dict):\n' +
              INDENT * 2 +
              'raise ValueError("Expected a dict at path {}, but got: {}".format(path, type(obj)))\n\n')
    fid.write(INDENT + 'for key in obj:\n' +
              INDENT * 2 + 'if not isinstance(key, str):\n' +
              INDENT * 3 +
              'raise ValueError("Expected a key of type str at path {}, but got: {}".format(path, type(key)))\n\n')
    # yapf: enable

    if not classdef.attributes:
        fid.write(INDENT + "return {}()".format(classdef.identifier))
        return

    def write_set_attr_stmt(indention: str, set_attr_stmt_parts: List[str]) -> None:
        prefix, value, expected, path, type_suffix = set_attr_stmt_parts

        line = indention + prefix + ', '.join([value, expected, path]) + type_suffix
        if len(line) <= 80:
            fid.write(line)
            return

        fid.write(indention + prefix + value + ',\n')
        fid.write(' ' * len(indention + prefix) + expected + ',\n')
        fid.write(' ' * len(indention + prefix) + path + type_suffix)

    for i, attr in enumerate(classdef.attributes.values()):
        if i > 0:
            fid.write('\n\n')

        attr_type_expr = type_expression(typedef=attr.typedef, path=attr.classdef.identifier + "." + attr.name)

        if not attr.required:
            attr_type_expr = "Optional[{}]".format(attr_type_expr)

        # yapf: disable
        set_attr_stmt_parts = [
            '{}_from_obj = from_obj('.format(attr.name),
            'obj["{0}"]'.format(attr.name),
            'expected=[{}]'.format(
                expected_type_expression(typedef=attr.typedef)),
            'path=path + ".{}")'.format(attr.name),
            '  # type: {}'.format(attr_type_expr)
        ]
        # yapf: enable

        if attr.required:
            write_set_attr_stmt(indention=INDENT, set_attr_stmt_parts=set_attr_stmt_parts)
        else:
            fid.write(INDENT + 'if "{}" in obj:\n'.format(attr.name))
            write_set_attr_stmt(indention=INDENT * 2, set_attr_stmt_parts=set_attr_stmt_parts)
            fid.write("\n")
            fid.write(INDENT + "else:\n")
            fid.write(INDENT * 2 + '''{}_from_obj = None'''.format(attr.name))

    fid.write('\n\n')

    prefix = INDENT + 'return {}('.format(classdef.identifier)
    suffix = ')'
    args = []  # type: List[str]
    for attr in classdef.attributes.values():
        args.append('{0}={0}_from_obj'.format(attr.name))

    line = prefix + ', '.join(args) + suffix
    if len(line) <= 80:
        fid.write(line)
    else:
        fid.write(prefix)
        fid.write(args[0])

        for arg in args[1:]:
            fid.write(',\n')
            fid.write(' ' * len(prefix) + arg)

        fid.write(suffix)


def write_to_jsonable(classdefs: List[Classdef], fid: TextIO):
    """Write ``to_jsonable`` function."""
    # yapf: disable
    fid.write('''def to_jsonable(obj: Any, expected: List[type], path: str = "") -> Any:
    """
    Checks and converts the given object along the expected types to a JSON-able representation.

    :param obj: to be converted
    :param expected: list of types representing the (nested) structure
    :return: JSON-able representation of the object

    """
    if not expected:
        raise ValueError("`expected` is empty, but at least one type needs to be specified.")

    exp = expected[0]
    if not isinstance(obj, exp):
        raise ValueError("Expected object of type {} at path {!r}, but got {}.".format(exp, path, type(obj)))

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
            lst.append(to_jsonable(value, expected=expected[1:], path=''.join([path, '[', str(i), ']'])))

        return lst

    if exp == dict:
        assert isinstance(obj, dict)

        adict = dict()  # type: Dict[str, Any]
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError("Expected a key of type str at path {!r}, got: {}".format(path, type(key)))

            adict[key] = to_jsonable(value, expected=expected[1:], path=''.join([path, '[', key, ']']))

        return adict'''.replace(' ' * 4, INDENT))

    for classdef in classdefs:
        fid.write('\n\n')
        fid.write(INDENT + 'if exp == {}:\n'.format(classdef.identifier))
        fid.write(INDENT * 2 + 'assert isinstance(obj, {})\n'.format(classdef.identifier))
        fid.write(INDENT * 2 + 'return {}_to_jsonable(obj, path=path)'.format(
            swagger_to.snake_case(classdef.identifier)))

    fid.write('\n\n')

    fid.write(INDENT + 'raise ValueError("Unexpected `expected` type: {}".format(exp))')


def write_class_to_jsonable(classdef: Classdef, fid: TextIO) -> None:
    """Write ``{class}_to_jsonable`` function."""
    fid.write('def {0}_to_jsonable({0}: {1}, path: str = "") -> Dict[str, Any]:\n'.format(
        swagger_to.snake_case(identifier=classdef.identifier), classdef.identifier))

    fid.write(INDENT + '"""Generates a dictionary JSON-able object from an instance of {}."""\n'.format(
        classdef.identifier))

    if not classdef.attributes:
        fid.write(INDENT + 'return dict()')
        return

    fid.write(INDENT + 'res = dict()  # type: Dict[str, Any]\n')
    fid.write('\n')

    variable = swagger_to.snake_case(identifier=classdef.identifier)

    for i, attr in enumerate(classdef.attributes.values()):
        if i > 0:
            fid.write('\n\n')

        if attr.required:
            indent = INDENT
        else:
            fid.write(INDENT + 'if {}.{} is not None:\n'.format(variable, attr.name))
            indent = INDENT * 2

        if isinstance(attr.typedef, (Booldef, Intdef, Floatdef, Strdef)):
            fid.write(indent + 'res["{0}"] = {1}.{0}'.format(attr.name, variable))
        else:
            prefix = indent + 'res["{}"] = to_jsonable('.format(attr.name)
            value = '{}.{}'.format(variable, attr.name)
            expected = '[{}]'.format(expected_type_expression(typedef=attr.typedef))
            path = '"{{}}.{}".format(path))'.format(attr.name)

            line = prefix + ', '.join([value, expected, path])
            if len(line) <= 80:
                fid.write(line)
            else:
                fid.write(prefix + value + ',\n')
                fid.write(' ' * len(prefix) + expected + ',\n')
                fid.write(' ' * len(prefix) + path)

    fid.write('\n')
    fid.write(INDENT + 'return res')


def to_string_expression(typedef: Typedef, expression: str) -> str:
    """
    Wrap the expression in str() if necessary.

    :param typedef: type definition of the variable
    :param expression: Python expression to be converted to string in the generated code
    :return: Python code
    """
    if isinstance(typedef, Strdef):
        return expression

    return 'str({})'.format(expression)

@icontract.ensure(lambda result: not result.startswith('"""'))
@icontract.ensure(lambda result: not result.endswith('"""'))
def request_docstring(request: Request) -> str:
    """
    Assemble the docstring of the given client request function.

    :param request: client request function to be documented
    :return: docstring of the request function
    """
    docstring_lines = []  # type: List[str]
    if request.description:
        docstring_lines += request.description.splitlines()
        if request.parameters:
            docstring_lines += ['']

    for param in request.parameters:
        if not param.description:
            docstring_lines += [':param {}:'.format(param.name)]
        else:
            description_lines = param.description.splitlines()
            if len(description_lines) == 1:
                docstring_lines += [':param {}: {}'.format(param.name, param.description)]
            else:
                docstring_lines += [':param {}:'.format(param.name)]
                for line in description_lines:
                    docstring_lines += [INDENT * 2 + line]

    return '\n'.join(docstring_lines)


def write_request(request: Request, fid: TextIO) -> None:
    """Write the client request function."""
    resp = None  # type: Optional[Response]
    return_type = 'bytes'
    if request.produces == ['application/json']:
        if '200' in request.responses:
            resp = request.responses['200']
            if resp.typedef is not None:
                return_type = type_expression(typedef=resp.typedef, path=request.operation_id + '.' + str(resp.code))
            else:
                # The schema for the response has not been defined. Hence we can not parse the response.
                resp = None
                return_type = 'Any'

    prefix = INDENT + 'def {}('.format(request.operation_id)
    suffix = ') -> {}:'.format(return_type)

    args = ['self']  # type: List[str]
    for param in request.parameters:
        param_type = type_expression(typedef=param.typedef, path=request.operation_id + '.' + param.name)

        if not param.required:
            args.append('{}: Optional[{}] = None'.format(param.name, param_type))
        else:
            args.append('{}: {}'.format(param.name, param_type))

    line = prefix + ', '.join(args) + suffix
    if len(line) <= 80:
        fid.write(line)
    else:
        fid.write(prefix)
        for i, arg in enumerate(args):
            if i > 0:
                fid.write(',\n')
                fid.write(' ' * len(prefix))
            fid.write(arg)

        fid.write(suffix)
    fid.write('\n')

    # assemble the docstring
    docstring = request_docstring(request=request)
    write_docstring(docstring=docstring, indent=INDENT * 2, fid=fid)
    fid.write('\n')

    # path parameters
    name_to_parameters = dict([(param.name, param) for param in request.parameters])

    token_pth = swagger_to.tokenize_path(path=request.path)

    if not token_pth.parameter_to_token_indices:
        fid.write(INDENT * 2 + 'url = self.url_prefix + "{}"'.format(request.path))
    else:
        fid.write(INDENT * 2 + 'url_parts = [self.url_prefix]')
        for i, tkn in enumerate(token_pth.tokens):
            fid.write("\n")

            if i in token_pth.token_index_to_parameter:
                param_name = token_pth.token_index_to_parameter[i]
                param = name_to_parameters[param_name]

                fid.write(
                    INDENT * 2 + 'url_parts.append({})'.format(
                        to_string_expression(typedef=param.typedef, expression=param.name)))
            else:
                fid.write(INDENT * 2 + 'url_parts.append("{}")'.format(
                    tkn.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')))

        fid.write('\n')
        fid.write(INDENT * 2 + 'url = "".join(url_parts)')

    if request.query_parameters:
        fid.write('\n\n')
        fid.write(INDENT * 2 + 'params = {\n')

        for i, param in enumerate(request.query_parameters):
            if i > 0:
                fid.write(',\n')
            if isinstance(param.typedef, (Booldef, Intdef, Floatdef, Strdef)):
                fid.write(INDENT * 3 + '"{0}": {0}'.format(param.name))
            else:
                fid.write(INDENT * 3 + '"{0}": to_jsonable({0}, expected=[{1}])'.format(
                    param.name, expected_type_expression(typedef=param.typedef)))

        fid.write('}')

    if request.body_parameter and request.formdata_parameters:
        raise KeyError("Both body parameter and form-data parameters are specified. "
                       "The python client does not know how to resolve this request.")

    if request.body_parameter:
        fid.write('\n\n')
        if isinstance(request.body_parameter.typedef, (Booldef, Intdef, Floatdef, Strdef)):
            fid.write(INDENT * 2 + 'data = {}'.format(request.body_parameter.name))
        else:
            fid.write(INDENT * 2 + 'data = to_jsonable({0}, expected=[{1}])'.format(
                request.body_parameter.name,
                expected_type_expression(typedef=request.body_parameter.typedef)))

    if request.formdata_parameters:
        fid.write('\n\n')
        fid.write(INDENT * 2 + 'data = {\n')

        for i, param in enumerate(request.formdata_parameters):
            if i > 0:
                fid.write(',\n')

            if isinstance(param.typedef, (Booldef, Intdef, Floatdef, Strdef)):
                fid.write(INDENT * 3 + '"{0}": {0}'.format(param.name))
            else:
                fid.write(INDENT * 3 + '"{0}": to_jsonable({0}, expected=[{1}])'.format(
                    param.name, expected_type_expression(typedef=param.typedef)))

        fid.write('}')

    if request.file_parameters:
        fid.write('\n\n')
        fid.write(INDENT * 2 + 'files = {\n')

        for i, param in enumerate(request.file_parameters):
            if i > 0:
                fid.write(',\n')

            assert isinstance(param.typedef, Filedef), \
                "Expected parameter {} of path {}.{} to be Filedef, but got: {}".format(
                    param.name, request.path, request.method, type(param.typedef))

            fid.write(INDENT * 3 + '"{0}": {0}'.format(param.name))

        fid.write('}')

    fid.write('\n\n')

    fid.write(INDENT * 2 + 'resp = requests.request(method={!r}, url=url'.format(request.method))
    if request.query_parameters:
        fid.write(', params=params')

    if request.body_parameter:
        fid.write(', json=data')
    elif request.formdata_parameters:
        fid.write(', data=data')
    else:
        # ignore the parameter which we don't know how to handle.
        pass

    if request.file_parameters:
        fid.write(', files=files')

    fid.write(', auth=self.auth)\n')
    fid.write(INDENT * 2 + 'with contextlib.closing(resp):\n')
    fid.write(INDENT * 3 + 'resp.raise_for_status()\n')

    if resp is None:
        if return_type == 'bytes':
            fid.write(INDENT * 3 + 'return resp.content')
        elif return_type == 'Any':
            fid.write(INDENT * 3 + 'return resp.json()')
        else:
            raise NotImplementedError("Unhandled return type of the request {}.{}: {!r}".format(
                request.path, request.method, return_type))
    else:
        fid.write(INDENT * 3 + 'return from_obj(obj=resp.json(), expected=[{}], path="")'.format(
            expected_type_expression(typedef=resp.typedef)))


def write_client(requests: List[Request],
                 fid: TextIO) -> None:
    """Write the client class."""
    fid.write("class RemoteCaller:\n")
    fid.write(INDENT + '"""Executes the remote calls to the server."""\n')
    fid.write('\n')

    fid.write(INDENT + 'def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:\n')
    fid.write(INDENT * 2 + "self.url_prefix = url_prefix\n")
    fid.write(INDENT * 2 + "self.auth = auth")

    if requests:
        fid.write('\n\n')

    for i, request in enumerate(requests):
        if i > 0:
            fid.write('\n\n')
        write_request(request=request, fid=fid)


def write_client_py(service_name: str,
                    typedefs: MutableMapping[str, Typedef],
                    requests: List[Request],
                    fid: TextIO) -> None:
    """
    Generate the file with the client code.

    :param service_name: used to designate the service that client connects to
    :param typedefs: table of type definitions in Python representation
    :param requests: request functions in Python representation
    :param fid: target
    :return:
    """
    write_header(service_name=service_name, fid=fid)

    if typedefs:
        classdefs = [typedef for typedef in typedefs.values() if isinstance(typedef, Classdef)]

        if classdefs:
            fid.write('\n\n')
            write_from_obj(classdefs=classdefs, fid=fid)
            fid.write('\n\n\n')
            write_to_jsonable(classdefs=classdefs, fid=fid)
            fid.write('\n\n\n')

        for i, classdef in enumerate(classdefs):
            if i > 0:
                fid.write('\n\n\n')
            write_class(classdef=classdef, fid=fid)
            fid.write('\n\n\n')
            write_class_factory_method(classdef=classdef, fid=fid)
            fid.write('\n\n\n')
            write_class_from_obj(classdef=classdef, fid=fid)
            fid.write('\n\n\n')
            write_class_to_jsonable(classdef=classdef, fid=fid)

    if typedefs:
        fid.write('\n\n\n')

    write_client(requests=requests, fid=fid)

    if requests and typedefs:
        fid.write('\n\n\n')

    write_footer(fid=fid)
    fid.write('\n')
