#!/usr/bin/env python3
"""Generate code for an TypeScript client with Angular5."""

from typing import MutableMapping, Optional, TextIO, List  # pylint: disable=unused-import

import collections
import icontract

import swagger_to
import swagger_to.intermediate
import swagger_to.swagger

INDENT = ' ' * 4


class Typedef:
    """Represent the type definition in Typescript."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.description = ''
        self.identifier = ''

    def __str__(self) -> str:
        """Represent the type definition as its class name and the identifier."""
        return '{}({})'.format(self.__class__.__name__, self.identifier)


class Booleandef(Typedef):
    """Represent a Typescript boolean."""

    pass


class Numberdef(Typedef):
    """Represent a Typescript number."""

    pass


class Stringdef(Typedef):
    """Represent a Typescript string."""

    pass


class Arraydef(Typedef):
    """Represents a Typescript array."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.items = None  # type: Optional[Typedef]
        super().__init__()

    def __str__(self) -> str:
        """Represent the array as its class name, identifier and the recursive representation of the items type."""
        return '{}({}, items: {})'.format(self.__class__.__name__, self.identifier, self.items)


class Mapdef(Typedef):
    """Represents a Typescript map."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.values = None  # type: Optional[Typedef]
        super().__init__()

    def __str__(self) -> str:
        """Represent the array as its class name, identifier and the recursive representation of the values type."""
        return '{}({}, values: {})'.format(self.__class__.__name__, self.identifier, self.values)


class Property:
    """Represents a Typescript class property."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.name = ''
        self.description = ''
        self.typedef = None  # type: Optional[Typedef]
        self.required = False

    def __str__(self) -> str:
        """Represent the property as its name and the type."""
        return '{}: {}'.format(self.name, self.typedef)


class Classdef(Typedef):
    """Represent a Typescript class."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Property]
        super().__init__()

    def __str__(self) -> str:
        """Represent the class as its class name, identifier and the list of properties."""
        return '{}({}, properties: {})'.format(self.__class__.__name__, self.identifier,
                                               ', '.join([str(val) for val in self.properties.values()]))


class Parameter:
    """Represent a parameter of a request function in Typescript."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.name = ''
        self.typedef = None  # type: Optional[Typedef]
        self.required = False


class Response:
    """Represent a response from a request in Typescript."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.code = ''
        self.typedef = None  # type: Optional[Typedef]
        self.description = ''


class Request:
    """Represent a request function of the client."""

    # pylint: disable=too-many-instance-attributes
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

        self.responses = collections.OrderedDict()  # type: MutableMapping[str, Response]


def _to_typedef(intermediate_typedef: swagger_to.intermediate.Typedef) -> Typedef:
    """
    Translate the type definition in intermediate representation to Typescript.

    :param intermediate_typedef: type definition in intermediate representation
    :return: type definition in Typescript representation
    """
    typedef = None  # type: Optional[Typedef]

    if isinstance(intermediate_typedef, swagger_to.intermediate.Primitivedef):
        if intermediate_typedef.type == 'boolean':
            typedef = Booleandef()
        elif intermediate_typedef.type == 'number' or intermediate_typedef.type == 'integer':
            typedef = Numberdef()
        elif intermediate_typedef.type == 'string':
            typedef = Stringdef()
        else:
            raise NotImplementedError("Converting intermediate type to Typescript is not supported: {}".format(
                intermediate_typedef.type))

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Arraydef):
        typedef = Arraydef()
        typedef.items = _to_typedef(intermediate_typedef=intermediate_typedef.items)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Mapdef()
        typedef.values = _to_typedef(intermediate_typedef=intermediate_typedef.values)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Classdef()

        for intermediate_prop in intermediate_typedef.properties.values():
            prop = Property()
            prop.description = intermediate_prop.description
            prop.name = intermediate_prop.name
            prop.typedef = _to_typedef(intermediate_typedef=intermediate_prop.typedef)
            prop.required = intermediate_prop.required

            typedef.properties[prop.name] = prop
    else:
        raise NotImplementedError("Converting intermediate typedef to Typescript is not supported: {!r}".format(
            type(intermediate_typedef)))

    typedef.description = intermediate_typedef.description
    typedef.identifier = intermediate_typedef.identifier

    assert typedef is not None

    return typedef


def to_typedefs(
        intermediate_typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> MutableMapping[str, Typedef]:
    """
    Translate type definitions from intermediate representation to Typescript.

    :param intermediate_typedefs: table of type definitions in intermediate representation
    :return: table of type definitions in Typescript representation
    """
    typedefs = collections.OrderedDict()  # type: MutableMapping[str, Typedef]

    for intermediate_typedef in intermediate_typedefs.values():
        assert intermediate_typedef is not None

        typedef = _to_typedef(intermediate_typedef=intermediate_typedef)
        typedefs[typedef.identifier] = typedef

    return typedefs


def _anonymous_or_get_typedef(intermediate_typedef: swagger_to.intermediate.Typedef,
                              typedefs: MutableMapping[str, Typedef]) -> Typedef:
    """
    Get the Typescript type definition from the table of Typescript type definitions by its identifier.

    If the type definition has no identifier, it is translated on the spot
    to the corresponding Typescript type definition.

    :param intermediate_typedef: intermediate representation of the type definition
    :param typedefs: table of type definitions in Typescript representation
    :return: type definition in Typescript representation
    """
    if intermediate_typedef.identifier:
        if intermediate_typedef.identifier not in typedefs:
            raise KeyError("Intermediate typedef not found in the translated typedefs: {!r}".format(
                intermediate_typedef.identifier))

        return typedefs[intermediate_typedef.identifier]

    return _to_typedef(intermediate_typedef=intermediate_typedef)


def _to_parameter(intermediate_parameter: swagger_to.intermediate.Parameter,
                  typedefs: MutableMapping[str, Typedef]) -> Parameter:
    """
    Translate an endpoint parameter from the intermediate to a Typescript representation.

    :param intermediate_parameter: intermediate representation of a parameter
    :param typedefs: table of type definitions in Typescript representation
    :return: Typescript representation of the parameter
    """
    param = Parameter()
    param.name = intermediate_parameter.name
    param.typedef = _anonymous_or_get_typedef(intermediate_typedef=intermediate_parameter.typedef, typedefs=typedefs)
    param.required = intermediate_parameter.required
    return param


def _to_response(intermediate_response: swagger_to.intermediate.Response,
                 typedefs: MutableMapping[str, Typedef]) -> Response:
    """
    Translate an endpoint response from the intermediate to a Typescript representation.

    :param intermediate_response: intermediate representation of a response
    :param typedefs: table of type definitions in Typescript representation
    :return: Typescript representation of the response
    """
    resp = Response()
    resp.code = intermediate_response.code
    resp.typedef = None if intermediate_response.typedef is None else \
        _anonymous_or_get_typedef(intermediate_typedef=intermediate_response.typedef, typedefs=typedefs)
    resp.description = intermediate_response.description
    return resp


def _to_request(endpoint: swagger_to.intermediate.Endpoint, typedefs: MutableMapping[str, Typedef]) -> Request:
    """
    Translate an endpoint from an intermediate representation to a Typescript client request function.

    :param endpoint: intermediate representation of the endpoint
    :param typedefs: table of type definitions in Typescript representation
    :return: Typescript representation of the client request function
    """
    if endpoint.produces != ['application/json']:
        raise ValueError("Can not translate an endpoint to Typescript client "
                         "which does not produces strictly application/json: {} {}".format(
                             endpoint.path, endpoint.method))

    req = Request()
    req.description = endpoint.description
    req.method = endpoint.method
    req.operation_id = endpoint.operation_id
    req.path = endpoint.path

    for intermediate_param in endpoint.parameters:
        param = _to_parameter(intermediate_parameter=intermediate_param, typedefs=typedefs)

        if intermediate_param.in_what == 'body':
            if req.body_parameter is not None:
                raise KeyError("Duplicate body parameters in an endpoint: {} {}".format(
                    req.body_parameter.name, intermediate_param.name))

            req.body_parameter = param
        elif intermediate_param.in_what == 'query':
            req.query_parameters.append(param)
        elif intermediate_param.in_what == 'path':
            req.path_parameters.append(param)
        else:
            raise NotImplementedError("Unsupported parameter 'in' to Typescript translation: {}".format(
                intermediate_param.in_what))

        req.parameters.append(param)

    # parameters are sorted so that first come the required ones; Typescript requires the optional ones to come
    # at the end.
    req.parameters.sort(key=lambda param: not param.required)

    for code, intermediate_resp in endpoint.responses.items():
        req.responses[code] = _to_response(intermediate_response=intermediate_resp, typedefs=typedefs)

    return req


@icontract.ensure(
    lambda endpoints, result:
    len(result) == len([endpoint for endpoint in endpoints if endpoint.produces == ['application/json']]))
def to_requests(endpoints: List[swagger_to.intermediate.Endpoint],
                typedefs: MutableMapping[str, Typedef]) -> List[Request]:
    """
    Translate endpoints from intermediate representation to Typescript client request functions.

    Endpoints which do not produce strictly 'application/json' are ignored.

    :param endpoints: intermediate representation of the endpoints
    :param typedefs: table of type definitions in Typescript representation
    :return: Typescript representation of client's request functions corresponding to the endpoints
    """
    requests = []  # type: List[Request]
    for endpoint in endpoints:
        if endpoint.produces != ['application/json']:
            continue

        requests.append(_to_request(endpoint=endpoint, typedefs=typedefs))

    return requests


def _write_header(fid: TextIO) -> None:
    """
    Write the header of the client file.

    :param fid: target
    :return:
    """
    fid.write("// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n\n")

    fid.write("import { Injectable } from '@angular/core';\n"
              "import { Http } from '@angular/http';\n"
              "import { HttpErrorResponse } from '@angular/common/http';\n"
              "import { Observable } from 'rxjs/Rx';\n"
              "import { RequestOptions } from '@angular/http';\n\n")


def _write_footer(fid: TextIO) -> None:
    """
    Write the footer of the client file.

    :param fid: target
    :return:
    """
    fid.write("\n\n// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n")


def _type_expression(typedef: Typedef, path: Optional[str] = None) -> str:
    """
    Translate the type definition in Typescript representation to a type expression as Typescript code.

    :param typedef: Typescript representation of the type definition
    :param path: path in the Swagger spec
    :return: Typescript code
    """
    if isinstance(typedef, Booleandef):
        return 'boolean'
    elif isinstance(typedef, Numberdef):
        return 'number'
    elif isinstance(typedef, Stringdef):
        return 'string'
    elif isinstance(typedef, Arraydef):
        return 'Array<' + _type_expression(typedef=typedef.items, path=str(path) + '.items') + ">"
    elif isinstance(typedef, Mapdef):
        return 'Map<string, ' + _type_expression(typedef=typedef.values, path=str(path) + '.values') + ">"
    elif isinstance(typedef, Classdef):
        if typedef.identifier == '':
            raise NotImplementedError(
                "Translating an anonymous class to a Typescript type expression is not supported: {}".format(path))

        return typedef.identifier
    else:
        raise NotImplementedError("Translating the typedef to a type expression is not supported: {!r}: {}".format(
            type(typedef), path))


def _write_description(description: str, indent: str, fid: TextIO) -> None:
    """
    Write a description as // comment block.

    :param description: to be written
    :param indent: indention as prefix to each line
    :param fid: target
    :return:
    """
    lines = description.strip().splitlines()
    for i, line in enumerate(lines):
        rstripped = line.rstrip()
        if len(rstripped) > 0:
            fid.write(indent + '// {}'.format(rstripped))
        else:
            fid.write(indent + '//')

        if i < len(lines) - 1:
            fid.write('\n')


def _write_type_definition(typedef: Typedef, fid: TextIO) -> None:
    """
    Write the type definition in the Typescript code.

    :param typedef: to be declared
    :param fid: target
    :return:
    """
    if typedef.identifier == '':
        raise ValueError("Expected a typedef with an identifier, but got a typedef with an empty identifier.")

    if typedef.description:
        _write_description(description=typedef.description, indent='', fid=fid)
        fid.write('\n')

    if isinstance(typedef, Classdef):
        fid.write("export interface {} {{\n".format(typedef.identifier))
        for i, prop in enumerate(typedef.properties.values()):
            if i > 0:
                fid.write('\n')

            if prop.description:
                _write_description(description=prop.description, indent=INDENT, fid=fid)
                fid.write("\n")

            type_expr = _type_expression(typedef=prop.typedef, path='{}.{}'.format(typedef.identifier, prop.name))

            if not prop.required:
                fid.write(INDENT + '{}?: {};\n'.format(prop.name, type_expr))
            else:
                fid.write(INDENT + '{}: {};\n'.format(prop.name, type_expr))

        fid.write("}")
    else:
        fid.write("type {} = {};".format(typedef.identifier, _type_expression(typedef=typedef,
                                                                              path=typedef.identifier)))


def _write_type_definitions(typedefs: MutableMapping[str, Typedef], fid: TextIO) -> None:
    """
    Write all type definitions as Typescript code.

    :param typedefs: type definitions to be declared
    :param fid: target
    :return:
    """
    for i, typedef in enumerate(typedefs.values()):
        if i > 0:
            fid.write('\n\n')

        _write_type_definition(typedef=typedef, fid=fid)


def _to_string_expression(typedef: Typedef, variable: str) -> str:
    """
    Wrap the variable with .toString() if necessary.

    :param typedef: type definition of the variable in Typescript representation
    :param variable: variable to be converted to string in the generated code
    :return: Typescript code
    """
    if isinstance(typedef, Stringdef):
        return variable

    return '{}.toString()'.format(variable)


def _write_request(request: Request, fid: TextIO) -> None:
    """
    Generate the code of the request function.

    :param request: function definition
    :param fid: target
    :return:
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    # pylint: disable=too-many-branches
    description = 'Sends a request to the endpoint: {} {}'.format(request.path, request.method)
    if request.description:
        description += '\n\n' + request.description
    _write_description(description, INDENT, fid)
    fid.write('\n')

    prefix = INDENT + 'public {}('.format(request.operation_id)

    args = []  # type: List[str]
    for param in request.parameters:
        args.append('{}{}: {}'.format(
            param.name, '?' if not param.required else '', _type_expression(typedef=param.typedef)))

    return_type = ''
    if '200' in request.responses:
        resp = request.responses['200']
        if resp.typedef is not None:
            return_type = _type_expression(typedef=resp.typedef)

    if not return_type:
        return_type = 'any'

    suffix = '): Observable<{} | HttpErrorResponse> {{'.format(return_type)

    line = prefix + ', '.join(args) + suffix
    if len(line) <= 120:
        fid.write(line)
    else:
        fid.write(prefix)
        fid.write('\n')

        for i, arg in enumerate(args):
            fid.write(3 * INDENT + arg)

            if i < len(args) - 1:
                fid.write(',\n')

        fid.write(suffix)
    fid.write('\n')

    name_to_parameters = dict([(param.name, param) for param in request.parameters])

    rel_path = request.path[1:] if request.path.startswith('/') else request.path

    # path parameters
    token_pth = swagger_to.tokenize_path(path=rel_path)

    if not token_pth.parameter_to_token_indices and not request.query_parameters:
        fid.write(INDENT * 2 + 'const url = this.url_prefix + "{}";\n'.format(rel_path))
    else:
        if not token_pth.parameter_to_token_indices:
            fid.write(INDENT * 2 + 'let url = this.url_prefix + "{}";'.format(rel_path))
        else:
            fid.write(INDENT * 2 + 'let url = this.url_prefix;')
            for i, tkn in enumerate(token_pth.tokens):
                fid.write("\n")

                if i in token_pth.token_index_to_parameter:
                    param_name = token_pth.token_index_to_parameter[i]
                    param = name_to_parameters[param_name]

                    fid.write(INDENT * 2 + 'url += encodeURIComponent({});'.format(
                        _to_string_expression(typedef=param.typedef, variable=param.name)))
                else:
                    fid.write(INDENT * 2 + 'url += encodeURIComponent("{}");'.format(
                        tkn.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')))

    if request.path_parameters and request.query_parameters:
        fid.write("\n")

    # query parameters
    if request.query_parameters:
        fid.write('\n')
        fid.write(INDENT * 2 + 'url += "?";\n')

        for i, param in enumerate(request.query_parameters):
            amp = ''  # used to concatenate query parameters
            if i > 0:
                fid.write("\n\n")
                amp = '&'

            if param.required:
                fid.write(INDENT * 2 + 'url += "{}{}=" + encodeURIComponent({});'.format(
                    amp, param.name, _to_string_expression(typedef=param.typedef, variable=param.name)))
            else:
                fid.write(INDENT * 2 + 'if ({}) {{\n'.format(param.name))
                fid.write(INDENT * 3 + 'url += "{}{}=" + encodeURIComponent({});\n'.format(
                    amp, param.name, _to_string_expression(typedef=param.typedef, variable=param.name)))
                fid.write(INDENT * 2 + '}')

        fid.write('\n')

    fid.write('\n')

    mth = request.method.lower()
    if request.body_parameter is not None:
        if request.body_parameter.required:
            fid.write(INDENT * 2 + 'let observable = this.http.request(url, \n')
            fid.write(INDENT * 3 + 'new RequestOptions({{method: "{0}", body: JSON.stringify({1})}}));\n'.format(
                mth, request.body_parameter.name))
        else:
            fid.write(INDENT * 2 + 'let observable: Observable<any>;\n')
            fid.write(INDENT * 2 + 'if ({}) {{\n'.format(request.body_parameter.name))
            fid.write(INDENT * 3 + 'this.http.request(url, \n')
            fid.write(INDENT * 4 + 'new RequestOptions({{method: "{0}", body: JSON.stringify({1})}}));\n'.format(
                mth, request.body_parameter.name))
            fid.write(INDENT * 2 + '} else {\n')
            fid.write(INDENT * 3 + 'observable = this.http.request(url, '
                      'new RequestOptions({{method: "{0}"}}));\n'.format(mth))
            fid.write(INDENT * 2 + '}\n')
    else:
        fid.write(INDENT * 2 + 'let observable = this.http.{}(url);\n'.format(mth))

    return_var = 'observable'
    if return_type != 'any':
        fid.write(
            INDENT * 2 + 'let typed_observable = observable.map(res => (res.json() as {}));\n'.format(return_type))
        return_var = 'typed_observable'

    fid.write(INDENT * 2 + 'if (this.on_error) {\n')
    fid.write(INDENT * 3 + 'return {0}.catch(err => this.on_error(err))\n'.format(return_var))
    fid.write(INDENT * 2 + '}\n')
    fid.write(INDENT * 2 + 'return {};\n'.format(return_var))

    fid.write(INDENT + '}')


def _write_client(requests: List[Request], fid: TextIO) -> None:
    """
    Generate the client.

    :param requests: translated request functions
    :param fid: target
    :return:
    """
    fid.write("@Injectable()\n")
    fid.write("export class RemoteCaller {\n")
    fid.write(INDENT + "public url_prefix: string;\n")
    fid.write(INDENT + "public on_error: (error: HttpErrorResponse) => Observable<HttpErrorResponse> | null;\n")
    fid.write("\n")
    fid.write(INDENT + "constructor(private http: Http) {\n")
    fid.write(INDENT * 2 + 'this.url_prefix = "";\n')
    fid.write(INDENT * 2 + 'this.on_error = null;\n')
    fid.write(INDENT + '}\n\n')
    fid.write(INDENT + "public set_url_prefix(url_prefix: string) {\n")
    fid.write(INDENT * 2 + "this.url_prefix = url_prefix;\n")
    fid.write(INDENT + '}\n\n')
    fid.write(INDENT + "public set_on_error("
              "on_error: (error: HttpErrorResponse) => Observable<HttpErrorResponse> | null) {\n")
    fid.write(INDENT * 2 + "this.on_error = on_error;\n")
    fid.write(INDENT + '}')

    for request in requests:
        fid.write('\n\n')
        _write_request(request=request, fid=fid)

    fid.write("\n}")


def write_client_ts(typedefs: MutableMapping[str, Typedef], requests: List[Request], fid: TextIO) -> None:
    """
    Generate the file with the client code.

    :param typedefs: table of type definitions in Typescript representation
    :param requests: request functions in Typescript representation
    :param fid: target
    :return:
    """
    _write_header(fid=fid)

    if typedefs:
        _write_type_definitions(typedefs=typedefs, fid=fid)

    if requests and typedefs:
        fid.write('\n\n')

    if requests:
        _write_client(requests=requests, fid=fid)
        _write_footer(fid=fid)
