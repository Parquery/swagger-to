#!/usr/bin/env python3
"""
Generates code for an TypeScript client with Angular5.
"""

import collections
from typing import MutableMapping, Optional, TextIO, List  # pylint: disable=unused-import

import swagger_to
import swagger_to.intermediate
import swagger_to.swagger

INDENT = ' ' * 4


class Typedef:
    """
    Represents a typescript type.
    """

    def __init__(self) -> None:
        self.description = ''
        self.identifier = ''

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.identifier)


class Booleandef(Typedef):
    """
    Represents typescript booleans.
    """
    pass


class Numberdef(Typedef):
    """
    Represents typescript numbers.
    """
    pass


class Stringdef(Typedef):
    """
    Represents typescript strings.
    """
    pass


class Arraydef(Typedef):
    """
    Represents typescript arrays.
    """

    def __init__(self) -> None:
        self.items = None  # type: Optional[Typedef]
        super().__init__()

    def __str__(self) -> str:
        return '{}({}, items: {})'.format(self.__class__.__name__, self.identifier, self.items)


class Mapdef(Typedef):
    """
    Represents typescript maps.
    """

    def __init__(self) -> None:
        self.values = None  # type: Optional[Typedef]
        super().__init__()

    def __str__(self) -> str:
        return '{}({}, values: {})'.format(self.__class__.__name__, self.identifier, self.values)


class Property:
    """
    Represents a typescript class property.
    """

    def __init__(self) -> None:
        self.name = ''
        self.description = ''
        self.typedef = None  # type: Optional[Typedef]
        self.required = False

    def __str__(self) -> str:
        return '{}: {}'.format(self.name, self.typedef)


class Classdef(Typedef):
    """
    Represents typescript classes.
    """

    def __init__(self) -> None:
        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Property]
        super().__init__()

    def __str__(self) -> str:
        return '{}({}, properties: {})'.format(self.__class__.__name__, self.identifier,
                                               ', '.join([str(val) for val in self.properties.values()]))


class Parameter:
    """
    Represents a parameter of a request.
    """

    def __init__(self) -> None:
        self.name = ''
        self.typedef = None  # type: Optional[Typedef]
        self.required = False


class Response:
    """
    Represents a response from a request.
    """

    def __init__(self) -> None:
        self.code = ''
        self.typedef = None  # type: Optional[Typedef]
        self.description = ''


class Request:
    """
    Represents a request function of the client.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
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


def to_typedef(intermediate_typedef: swagger_to.intermediate.Typedef) -> Typedef:
    """
    Translates the intermediate typedef to a typescript typedef.

    :param intermediate_typedef: to be translated
    :return:
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
        typedef.items = to_typedef(intermediate_typedef=intermediate_typedef.items)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Mapdef()
        typedef.values = to_typedef(intermediate_typedef=intermediate_typedef.values)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Classdef()

        for intermediate_prop in intermediate_typedef.properties.values():
            prop = Property()
            prop.description = intermediate_prop.description
            prop.name = intermediate_prop.name
            prop.typedef = to_typedef(intermediate_typedef=intermediate_prop.typedef)
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
    Translates the intermediate typedefs to typescript typedefs.

    :param intermediate_typedefs: to be translated
    :return: translated typedefs
    """
    typedefs = collections.OrderedDict()  # type: MutableMapping[str, Typedef]

    for intermediate_typedef in intermediate_typedefs.values():
        assert intermediate_typedef is not None

        typedef = to_typedef(intermediate_typedef=intermediate_typedef)
        typedefs[typedef.identifier] = typedef

    return typedefs


def anonymous_or_get_typedef(intermediate_typedef: swagger_to.intermediate.Typedef,
                             typedefs: MutableMapping[str, Typedef]) -> Typedef:
    """
    If the type has an identifier, it is retrieved from the translated typedefs.

    Otherwise, it is translated on the spot to the corresponding typescript type.

    :param intermediate_typedef: to be translated
    :param typedefs: translated type definitions
    :return: translated type
    """
    if intermediate_typedef.identifier:
        if intermediate_typedef.identifier not in typedefs:
            raise KeyError("Intermediate typedef not found in the translated typedefs: {!r}".format(
                intermediate_typedef.identifier))

        return typedefs[intermediate_typedef.identifier]

    return to_typedef(intermediate_typedef=intermediate_typedef)


def to_parameter(intermediate_parameter: swagger_to.intermediate.Parameter,
                 typedefs: MutableMapping[str, Typedef]) -> Parameter:
    """
    Translates an intermediate parameter to a typescript parameter.

    :param intermediate_parameter: to be translated
    :param typedefs: translated type definitions
    :return: translated parameter
    """
    param = Parameter()
    param.name = intermediate_parameter.name
    param.typedef = anonymous_or_get_typedef(intermediate_typedef=intermediate_parameter.typedef, typedefs=typedefs)
    param.required = intermediate_parameter.required
    return param


def to_response(intermediate_response: swagger_to.intermediate.Response,
                typedefs: MutableMapping[str, Typedef]) -> Response:
    """
    Translates an intermediate response to a typescript response.

    :param intermediate_response: to be translated
    :param typedefs: translated type definitions
    :return: translated response
    """
    resp = Response()
    resp.code = intermediate_response.code
    resp.typedef = None if intermediate_response.typedef is None else \
        anonymous_or_get_typedef(intermediate_typedef=intermediate_response.typedef, typedefs=typedefs)
    resp.description = intermediate_response.description
    return resp


def to_request(endpoint: swagger_to.intermediate.Endpoint, typedefs: MutableMapping[str, Typedef]) -> Request:
    """
    Translates an endpoint to a client request function.

    :param endpoint: to be translated
    :param typedefs: translated type definitions
    :return: request function
    """
    if endpoint.produces != ['application/json']:
        raise ValueError("Can not translate an end point to typescript client "
                         "which does not produces strictly application/json: {} {}".format(
                             endpoint.path, endpoint.method))

    req = Request()
    req.description = endpoint.description
    req.method = endpoint.method
    req.operation_id = endpoint.operation_id
    req.path = endpoint.path

    for intermediate_param in endpoint.parameters:
        param = to_parameter(intermediate_parameter=intermediate_param, typedefs=typedefs)

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

    # parameters are sorted so that first come the required ones; typescript requires the optional ones to come
    # at the end.
    req.parameters.sort(key=lambda param: not param.required)

    for code, intermediate_resp in endpoint.responses.items():
        req.responses[code] = to_response(intermediate_response=intermediate_resp, typedefs=typedefs)

    return req


def to_requests(endpoints: List[swagger_to.intermediate.Endpoint],
                typedefs: MutableMapping[str, Typedef]) -> List[Request]:
    """
    Translates the endpoints to typescript request functions.

    Endpoints which do not produce strictly 'application/json' are ignored.

    :param endpoints: to be translated
    :param typedefs: translated type definitions
    :return: translated request functions
    """
    requests = []  # type: List[Request]
    for endpoint in endpoints:
        if endpoint.produces != ['application/json']:
            continue

        requests.append(to_request(endpoint=endpoint, typedefs=typedefs))

    return requests


def write_header(fid: TextIO) -> None:
    """
    Writes the header (same for all the typescript clients).

    :param fid: target
    :return:
    """
    fid.write("// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n\n")

    fid.write("import { Injectable } from '@angular/core';\n"
              "import { Http } from '@angular/http';\n"
              "import { HttpErrorResponse } from '@angular/common/http';\n"
              "import { Observable } from 'rxjs/Rx';\n"
              "import { RequestOptions } from '@angular/http';\n\n")


def write_footer(fid: TextIO) -> None:
    """
    Writes the footer (same for all the typescript clients).

    :param fid: target
    :return:
    """

    fid.write("\n\n// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n")


def type_expression(typedef: Typedef, path: Optional[str] = None) -> str:
    """
    Translates the typedef to a type expression.

    :param typedef: to be translated
    :param path: path in the intermediate representation
    :return: type expression
    """
    if isinstance(typedef, Booleandef):
        return 'boolean'
    elif isinstance(typedef, Numberdef):
        return 'number'
    elif isinstance(typedef, Stringdef):
        return 'string'
    elif isinstance(typedef, Arraydef):
        return 'Array<' + type_expression(typedef=typedef.items, path=str(path) + '.items') + ">"
    elif isinstance(typedef, Mapdef):
        return 'Map<string, ' + type_expression(typedef=typedef.values, path=str(path) + '.values') + ">"
    elif isinstance(typedef, Classdef):
        if typedef.identifier == '':
            raise NotImplementedError(
                "Translating an anonymous class to a Typescript type expression is not supported: {}".format(path))

        return typedef.identifier
    else:
        raise NotImplementedError("Translating the typedef to a type expression is not supported: {!r}: {}".format(
            type(typedef), path))


def write_description(description: str, indent: str, fid: TextIO) -> None:
    """
    Writes a description as // comment block.
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


def write_type_definition(typedef: Typedef, fid: TextIO) -> None:
    """
    Writes the type definition in the Typescript code.

    :param typedef: to be declared
    :param fid: target
    :return:
    """
    if typedef.identifier == '':
        raise ValueError("Expected a typedef with an identifier, but got a typedef with an empty identifier.")

    if typedef.description:
        write_description(description=typedef.description, indent='', fid=fid)
        fid.write('\n')

    if isinstance(typedef, Classdef):
        fid.write("export interface {} {{\n".format(typedef.identifier))
        for i, prop in enumerate(typedef.properties.values()):
            if i > 0:
                fid.write('\n')

            if prop.description:
                write_description(description=prop.description, indent=INDENT, fid=fid)
                fid.write("\n")

            type_expr = type_expression(typedef=prop.typedef, path='{}.{}'.format(typedef.identifier, prop.name))

            if not prop.required:
                fid.write(INDENT + '{}?: {};\n'.format(prop.name, type_expr))
            else:
                fid.write(INDENT + '{}: {};\n'.format(prop.name, type_expr))

        fid.write("}")
    else:
        fid.write("type {} = {};".format(typedef.identifier, type_expression(typedef=typedef, path=typedef.identifier)))


def write_type_definitions(typedefs: MutableMapping[str, Typedef], fid: TextIO) -> None:
    """
    Writes all type definitions as Typescript code.

    :param typedefs: type definitions to be declared
    :param fid: target
    :return:
    """
    for i, typedef in enumerate(typedefs.values()):
        if i > 0:
            fid.write('\n\n')

        write_type_definition(typedef=typedef, fid=fid)


def to_string_expression(typedef: Typedef, variable: str) -> str:
    """
    Wraps the variable with .toString() if necessary.

    :param typedef: type definition of the variable
    :param variable: to be converted to string in the generated code
    :return: typescript expression
    """
    if isinstance(typedef, Stringdef):
        return variable

    return '{}.toString()'.format(variable)


def write_request(request: Request, fid: TextIO) -> None:
    """
    Generates the code of the request function.

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
    write_description(description, INDENT, fid)
    fid.write('\n')

    prefix = INDENT + 'public {}('.format(request.operation_id)

    args = []  # type: List[str]
    for param in request.parameters:
        args.append('{}{}: {}'.format(
            param.name, '?' if not param.required else '', type_expression(typedef=param.typedef)))

    return_type = ''
    if '200' in request.responses:
        resp = request.responses['200']
        if resp.typedef is not None:
            return_type = type_expression(typedef=resp.typedef)

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
                        to_string_expression(typedef=param.typedef, variable=param.name)))
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
                    amp, param.name, to_string_expression(typedef=param.typedef, variable=param.name)))
            else:
                fid.write(INDENT * 2 + 'if ({}) {{\n'.format(param.name))
                fid.write(INDENT * 3 + 'url += "{}{}=" + encodeURIComponent({});\n'.format(
                    amp, param.name, to_string_expression(typedef=param.typedef, variable=param.name)))
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


def write_client(requests: List[Request], fid: TextIO) -> None:
    """
    Generates the client.

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
        write_request(request=request, fid=fid)

    fid.write("\n}")


def write_client_ts(typedefs: MutableMapping[str, Typedef], requests: List[Request], fid: TextIO) -> None:
    """
    Generates the file with the client code.

    :param typedefs: translated type definitions
    :param requests: translated request functions
    :param fid: target
    :return:
    """
    write_header(fid=fid)

    if typedefs:
        write_type_definitions(typedefs=typedefs, fid=fid)

    if requests and typedefs:
        fid.write('\n\n')

    if requests:
        write_client(requests=requests, fid=fid)
        write_footer(fid=fid)
