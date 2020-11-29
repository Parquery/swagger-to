#!/usr/bin/env python3
"""Generate code for an Elm client."""
# pylint: disable=too-many-lines
from typing import Optional, MutableMapping, List, Dict, TextIO, Any  # pylint: disable=unused-import

import collections

import icontract
import swagger_to
import swagger_to.intermediate

INDENT = ' ' * 4


class Typedef:
    """Represent an Elm type."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.description = ''
        self.identifier = ''

    def __str__(self) -> str:
        """Represent the type definition by its class and the identifier."""
        return '{}({})'.format(self.__class__.__name__, self.identifier)


class BracketedTypedef(Typedef):
    """Represent an Elm type wrapped in brackets."""

    def __str__(self) -> str:
        """Represent the type definition by its class name."""
        return '({})'.format(self.__class__.__name__)


class Booldef(Typedef):
    """Represent an Elm boolean."""

    pass


class Intdef(Typedef):
    """Represent an Elm integer."""

    pass


class Floatdef(Typedef):
    """Represent an Elm floating-point number."""

    pass


class Stringdef(Typedef):
    """Represent an Elm string."""

    pass


class Listdef(BracketedTypedef):
    """Represent an Elm list."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.items = None  # type: Optional[Typedef]
        super().__init__()


class Dictdef(BracketedTypedef):
    """Represent an Elm dictionary."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.values = None  # type: Optional[Typedef]
        super().__init__()


class Property:
    """Represent a property of an Elm record."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.name = ''
        self.description = ''
        self.typedef = None  # type: Optional[Typedef]
        self.required = False

    def __str__(self) -> str:
        """Represent the property by its name and type definition."""
        return '{}: {}'.format(self.name, self.typedef)


class Recorddef(Typedef):
    """Represent an Elm record."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Property]
        super().__init__()


class Parameter:
    """Represent a prameter of a request."""

    def __init__(self) -> None:
        """Initialize with defaults."""
        self.name = ''
        self.typedef = None  # type: Optional[Typedef]
        self.required = False


class Response:
    """Represent a response from a request."""

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
    """Translate the intermediate type definition to a definition of an Elm type.

    :param intermediate_typedef: intermediate type definition
    :return: definition of an Elm type
    """
    # pylint: disable=too-many-branches
    typedef = None  # type: Optional[Typedef]

    if isinstance(intermediate_typedef, swagger_to.intermediate.Primitivedef):
        if intermediate_typedef.type == 'boolean':
            typedef = Booldef()
        elif intermediate_typedef.type == "integer":
            if intermediate_typedef.format is None or intermediate_typedef.format in ["int32", "int64"]:
                typedef = Intdef()
            else:
                raise NotImplementedError("Unhandled format of a swagger intermediate type 'integer': {}".format(
                    intermediate_typedef.format))
        elif intermediate_typedef.type == 'number':
            typedef = Floatdef()
        elif intermediate_typedef.type == 'string':
            typedef = Stringdef()
        else:
            raise NotImplementedError("Converting intermediate type to Elm is not supported: {}".format(
                intermediate_typedef.type))

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Arraydef):
        typedef = Listdef()
        typedef.items = _to_typedef(intermediate_typedef=intermediate_typedef.items)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Dictdef()
        typedef.values = _to_typedef(intermediate_typedef=intermediate_typedef.values)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Recorddef()

        for intermediate_prop in intermediate_typedef.properties.values():
            prop = Property()
            prop.description = intermediate_prop.description
            prop.name = intermediate_prop.name
            prop.typedef = _to_typedef(intermediate_typedef=intermediate_prop.typedef)
            prop.required = intermediate_prop.required

            typedef.properties[prop.name] = prop
    else:
        raise NotImplementedError("Converting intermediate typedef to Elm is not supported: {!r}".format(
            type(intermediate_typedef)))

    typedef.description = intermediate_typedef.description
    typedef.identifier = intermediate_typedef.identifier

    assert typedef is not None

    return typedef


def to_typedefs(
        intermediate_typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> MutableMapping[str, Typedef]:
    """
    Translate a table of the intermediate type definitions to a table of definitions of Elm types.

    :param intermediate_typedefs: table of intermediate type definitions
    :return: table of Elm type definitions
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
    Create an anonyomus type definition or get the type definition from the table of Elm type definitions, if available.

    :param intermediate_typedef: intermediate type definition
    :param typedefs: table of Elm type definitions
    :return: Elm type definition
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
    Translate an intermediate representation of an endpoint parameter to an Elm parameter.

    :param intermediate_parameter: intermediate representation of an endpoint parameter
    :param typedefs: table of Elm type definitions
    :return: representation of the parameter suitable for generating Elm client code
    """
    param = Parameter()
    param.name = intermediate_parameter.name
    param.typedef = _anonymous_or_get_typedef(intermediate_typedef=intermediate_parameter.typedef, typedefs=typedefs)
    param.required = intermediate_parameter.required
    return param


def _to_response(intermediate_response: swagger_to.intermediate.Response,
                 typedefs: MutableMapping[str, Typedef]) -> Response:
    """
    Translate an intermediate response to an Elm response.

    :param intermediate_response: intermediate representation of the endpoint response
    :param typedefs: table of Elm type definitions
    :return: representation of the response suitable for generating Elm client code
    """
    resp = Response()
    resp.code = intermediate_response.code
    resp.typedef = None if intermediate_response.typedef is None else \
        _anonymous_or_get_typedef(intermediate_typedef=intermediate_response.typedef, typedefs=typedefs)
    resp.description = intermediate_response.description
    return resp


def _to_request(endpoint: swagger_to.intermediate.Endpoint, typedefs: MutableMapping[str, Typedef]) -> Request:
    """
    Translate an endpoint to a client request function.

    :param endpoint: to be translated
    :param typedefs: table of Elm type definitions
    :return: representation of the request function suitable for generating Elm client code
    """
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
            raise NotImplementedError("Unsupported parameter 'in' to Elm translation: {}".format(
                intermediate_param.in_what))

        req.parameters.append(param)

    # Parameters are sorted so that first come the required ones; Elm requires the optional ones to come
    # at the end.
    req.parameters.sort(key=lambda param: not param.required)

    for code, intermediate_resp in endpoint.responses.items():
        req.responses[code] = _to_response(intermediate_response=intermediate_resp, typedefs=typedefs)

    return req


def to_requests(endpoints: List[swagger_to.intermediate.Endpoint],
                typedefs: MutableMapping[str, Typedef]) -> List[Request]:
    """
    Translate the endpoints to Elm request functions, ignoring endpoints consuming formData.

    :param endpoints: to be translated
    :param typedefs: table of Elm type definitions
    :return: translated request functions
    """
    requests = []  # type: List[Request]
    for endpoint in endpoints:
        has_form_data = False
        for param in endpoint.parameters:
            if param.in_what == 'formData':
                has_form_data = True

        if not has_form_data:
            requests.append(_to_request(endpoint=endpoint, typedefs=typedefs))

    return requests


def _write_description(description: str, indent: str, fid: TextIO) -> None:
    """
    Write a description as -- comment block.

    :param description: to be written
    :param indent: indention as prefix to each line
    :param fid: target
    :return:
    """
    lines = description.strip().splitlines()
    for i, line in enumerate(lines):
        rstripped = line.rstrip()
        if len(rstripped) > 0:
            fid.write(indent + '-- {}'.format(rstripped))
        else:
            fid.write(indent + '-- ')

        if i < len(lines) - 1:
            fid.write('\n')


def _write_top_level_description(description: str, fid: TextIO) -> None:
    """
    Write a top level description as {|- -} comment block.

    :param description: to be written
    :param fid: target
    :return:
    """
    lines = description.strip().splitlines()
    fid.write('{-| ')
    for i, line in enumerate(lines):
        if i > 0:
            fid.write('    ')
        fid.write('{}\n'.format(line.rstrip()))

    fid.write('-}')


def _argument_expression(typedef: Typedef, path: Optional[str] = None) -> str:
    """
    Translate the typedef to an argument expression for an Elm function signature.

    Notably, add brackets where they are due.

    :param typedef: to be translated
    :param path: path in the intermediate representation
    :return: type expression
    """
    if isinstance(typedef, BracketedTypedef):
        return '(' + _type_expression(typedef=typedef, path=path) + ')'

    return _type_expression(typedef=typedef, path=path)


def _argument_decoder_expression(typedef: Typedef, path: Optional[str] = None) -> str:
    """
    Translate the typedef to a argument decoder expression for an Elm function signature.

    Notably, add brackets where they are due.

    :param typedef: to be translated
    :param path: path in the intermediate representation
    :return: type expression
    """
    if isinstance(typedef, BracketedTypedef):
        return '(' + _type_decoder(typedef=typedef, path=path) + ')'

    return _type_decoder(typedef=typedef, path=path)


def _write_type_definition(typedef: Typedef, fid: TextIO) -> None:
    """
    Write the type definition in the Elm code.

    :param typedef: to be declared
    :param fid: target
    :return:
    """
    if typedef.identifier == '':
        raise ValueError("Expected a typedef with an identifier, but got a typedef with an empty identifier.")

    if typedef.description:
        _write_top_level_description(description=typedef.description, fid=fid)
        fid.write('\n')

    if isinstance(typedef, Recorddef):
        fid.write("type alias {} = \n".format(typedef.identifier))
        prefix = '{ '
        for prop in typedef.properties.values():
            if prop.description:
                _write_description(description=prop.description, indent=INDENT, fid=fid)
                fid.write("\n")

            if prop.typedef is None:
                raise ValueError("Unexpected None typedef of prop {!r} in type {!r}".format(
                    prop.name, typedef.identifier))

            type_expr = _type_expression(typedef=prop.typedef, path='{}.{}'.format(typedef.identifier, prop.name))
            camel_case_name = swagger_to.camel_case(identifier=prop.name)
            if not prop.required:
                fid.write(INDENT + prefix + '{} : Maybe ({})\n'.format(camel_case_name, type_expr))
            else:
                fid.write(INDENT + prefix + '{} : {}\n'.format(camel_case_name, type_expr))
            prefix = ', '

        fid.write(INDENT + "}")
    else:
        fid.write("type alias {} = \n".format(typedef.identifier))
        fid.write(INDENT + "{}".format(_type_expression(typedef=typedef, path=typedef.identifier)))


def _write_encoder(typedef: Typedef, fid: TextIO) -> None:
    """
    Write the Encoder in the Elm code.

    :param typedef: to be encoded
    :param fid: target
    :return:
    """
    if typedef.identifier == '':
        raise ValueError("Expected a typedef with an identifier, but got a typedef with an empty identifier.")

    if isinstance(typedef, Recorddef):
        obj_name = 'a' + typedef.identifier
        fid.write("encode{0} : {0} -> Json.Encode.Value\n".format(typedef.identifier))
        fid.write("encode{} {} =\n".format(typedef.identifier, obj_name))
        fid.write(INDENT + 'Json.Encode.object\n')
        prefix = 2 * INDENT + '[ '
        for prop in typedef.properties.values():
            fid.write(prefix + '( "{}", '.format(swagger_to.snake_case(identifier=prop.name)))

            if prop.typedef is None:
                raise ValueError("Unexpected None typedef of prop {!r} in type {!r}".format(
                    prop.name, typedef.identifier))

            encoder = _type_encoder(typedef=prop.typedef, path='{}.{}'.format(typedef.identifier, prop.name))
            if not prop.required:
                fid.write('Json.Encode.Extra.maybe ({}) '.format(encoder))
            else:
                fid.write('{} '.format(encoder))
            fid.write('<| {}.{} )\n'.format(obj_name, swagger_to.camel_case(identifier=prop.name)))
            prefix = 2 * INDENT + ', '

        fid.write(2 * INDENT + "]")

    elif isinstance(typedef, (Booldef, Intdef, Floatdef, Stringdef, Listdef, Dictdef)):
        bracketed_type_expression = _argument_expression(typedef=typedef, path=typedef.identifier)
        var_name = 'a' + typedef.identifier

        fid.write("encode{} : {} -> Json.Encode.Value \n".format(typedef.identifier, bracketed_type_expression))
        fid.write("encode{} {} =\n".format(typedef.identifier, var_name))
        fid.write(INDENT + "{}".format(_type_encoder(typedef=typedef, path=typedef.identifier)))
        fid.write(" <| {}".format(var_name))

    else:
        raise AssertionError("Unexpected type {}.".format(typedef.__class__))


def _write_decoder(typedef: Typedef, fid: TextIO) -> None:
    """
    Write the Decoder in the Elm code.

    :param typedef: to be decoded
    :param fid: target
    :return:
    """
    if typedef.identifier == '':
        raise ValueError("Expected a typedef with an identifier, but got a typedef with an empty identifier.")

    if isinstance(typedef, Recorddef):
        record_id = typedef.identifier
        fid.write("decode{0} : Json.Decode.Decoder {0}\n".format(record_id))
        fid.write("decode{} =\n".format(record_id))
        fid.write(INDENT + 'Json.Decode.Pipeline.decode {}\n'.format(record_id))
        prefix = 2 * INDENT + '|> '

        for prop in typedef.properties.values():
            snake_case_name = swagger_to.snake_case(identifier=prop.name)

            if prop.typedef is None:
                raise ValueError("Unexpected None typedef of prop {!r} in type {!r}".format(
                    prop.name, typedef.identifier))

            decoder = _argument_decoder_expression(typedef=prop.typedef, path='{}.{}'.format(record_id, prop.name))
            if prop.required:
                fid.write(prefix + 'Json.Decode.Pipeline.required "{}" {}\n'.format(snake_case_name, decoder))
            else:
                fid.write(prefix + 'Json.Decode.Pipeline.optional "{}" (Json.Decode.nullable {}) Nothing\n'.format(
                    snake_case_name, decoder))

    elif isinstance(typedef, (Booldef, Intdef, Floatdef, Stringdef, Listdef, Dictdef)):
        bracketed_type_expression = _argument_expression(typedef=typedef, path=typedef.identifier)
        fid.write("decode{} : Json.Decode.Decoder {}\n".format(typedef.identifier, bracketed_type_expression))
        fid.write("decode{} =\n".format(typedef.identifier))
        fid.write(INDENT + "{}".format(_type_decoder(typedef=typedef, path=typedef.identifier)))

    else:
        raise AssertionError("Unexpected type {}.".format(typedef.__class__))


def _escape_string(text: str) -> str:
    """
    Escape special characters in the given string.

    :param text: string to escape
    :return: the string with all Elm special characters escaped
    """
    text.replace('\\', '\\\\')
    text.replace('\n', '\\n')
    text.replace('\r', '\\r')
    text.replace('\t', '\\t')
    text.replace("\'", "\\'")
    text.replace('\"', '\\"')

    return text


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
    description = 'Contains a "{}" request to the endpoint: `{}`, to be sent with Http.send'.format(
        request.method, request.path)
    if request.description:
        description += '\n\n' + request.description
    _write_top_level_description(description=description, fid=fid)
    fid.write('\n')

    types = []  # type List[str]
    names = []  # type List[str]
    for param in request.parameters:
        if param.typedef is None:
            raise ValueError("Unexpected None typedef of param {!r} in request {!r}".format(
                param.name, request.operation_id))

        if param.required:
            types.append(_type_expression(typedef=param.typedef))
            names.append(swagger_to.camel_case(identifier=param.name))
        else:
            types.append('Maybe {}'.format(_type_expression(typedef=param.typedef)))
            names.append('maybe{}'.format(swagger_to.capital_camel_case(param.name)))

    return_type = None  # type: Optional[str]
    return_type_decoder = None  # type: Optional[str]
    if '200' in request.responses:
        resp = request.responses['200']
        if resp.typedef is not None:
            return_type = _argument_expression(typedef=resp.typedef)
            return_type_decoder = _argument_decoder_expression(typedef=resp.typedef)

    # function signature and arguments
    function_name = '{}Request'.format(_request_function_name(request.operation_id))
    types = ["String", "Maybe Time.Time", "Bool"] + types
    names = ["prefix", "maybeTimeout", "withCredentials"] + names
    types_str = ' -> '.join(types)
    types_str += ' -> '
    names_str = ' '.join(names)

    line1 = function_name + ' : ' + types_str
    if return_type is None:
        line1 += 'Http.Request String\n'
    else:
        line1 += 'Http.Request {}\n'.format(return_type)
    line2 = function_name + ' ' + names_str + ' ='
    indent = 1

    if len(line1) <= 120:
        fid.write(line1)
        fid.write(line2)
    else:
        fid.write(function_name + ' :\n')
        join_str = '\n' + INDENT + '-> '

        fid.write(INDENT + '{}\n'.format(join_str.join(types)))
        if return_type is None:
            fid.write(INDENT + '-> Http.Request String\n')
        else:
            fid.write(INDENT + '-> Http.Request {}\n'.format(return_type))

        if len(line2) > 120:
            fid.write(function_name)
            join_str = '\n' + INDENT
            fid.write('\n' + INDENT + '{}'.format(join_str.join(names)))

            fid.write(' =')
            indent = 2
        else:
            fid.write(line2)
    fid.write('\n')

    name_to_parameters = {param.name: param for param in request.parameters}

    rel_path = request.path[1:] if request.path.startswith('/') else request.path

    fid.write(INDENT * indent + 'let\n')

    # path parameters
    token_pth = swagger_to.tokenize_path(path=rel_path)
    url_name = 'baseUrl' if request.query_parameters else 'url'
    if not token_pth.parameter_to_token_indices:
        fid.write(INDENT * (indent + 1) + '{} = prefix ++ "{}"\n'.format(url_name, rel_path))
    else:
        fid.write(INDENT * (indent + 1) + '{} = prefix'.format(url_name))
        for i, tkn in enumerate(token_pth.tokens):
            fid.write("\n")

            if i in token_pth.token_index_to_parameter:
                param_name = token_pth.token_index_to_parameter[i]
                param = name_to_parameters[param_name]
                camel_case_name = swagger_to.camel_case(identifier=param.name)
                if not isinstance(param.typedef, Stringdef):
                    camel_case_name = '(toString {})'.format(camel_case_name)

                fid.write(INDENT * (indent + 2) + '++ {}'.format(camel_case_name))
            else:
                # escape special characters
                fid.write(INDENT * (indent + 2) + '++ "{}"'.format(_escape_string(text=tkn)))

    if request.path_parameters and request.query_parameters:
        fid.write("\n")

    # query parameters
    if request.query_parameters:
        required = []  # type: List[str]
        not_required = []  # type: List[str]

        for i, param in enumerate(request.query_parameters):
            if param.required:
                arg_name = swagger_to.camel_case(identifier=param.name)
                arg = arg_name
                if not isinstance(param.typedef, Stringdef):
                    arg = '(toString {})'.format(arg_name)

                required.append('("' + param.name + '", ' + arg + ')')
            else:
                arg_name = 'maybe{}'.format(swagger_to.capital_camel_case(identifier=param.name))
                arg = arg_name
                if not isinstance(param.typedef, Stringdef):
                    arg = '(Maybe.map toString {})'.format(arg_name)

                not_required.append('("' + param.name + '", ' + arg + ')')

        fid.write(INDENT * (indent + 1) + 'queryString = \n')
        fid.write(INDENT * (indent + 2) + 'paramsToQuery\n')

        if required:
            fid.write((INDENT * (indent + 3)) + "[ ")
            for i, tuple_str in enumerate(required):
                if i == 0:
                    fid.write(tuple_str + "\n")
                else:
                    fid.write((INDENT * (indent + 3)) + ", " + tuple_str + "\n")
            fid.write((INDENT * (indent + 3)) + "]\n")
        else:
            fid.write((INDENT * (indent + 3)) + '[]\n')

        if not_required:
            fid.write((INDENT * (indent + 3)) + "[ ")
            for i, tuple_str in enumerate(not_required):
                if i == 0:
                    fid.write(tuple_str + "\n")
                else:
                    fid.write((INDENT * (indent + 3)) + ", " + tuple_str + "\n")
            fid.write((INDENT * (indent + 3)) + "]\n")
        else:
            fid.write((INDENT * (indent + 3)) + '[]\n')

        fid.write(INDENT * (indent + 1) + 'url = baseUrl ++ queryString\n')

    fid.write(indent * INDENT + 'in\n')

    mth = request.method.upper()

    fid.write(INDENT * indent + 'Http.request\n')
    fid.write(INDENT * (indent + 1) + '{ body = ')
    if request.body_parameter is not None:
        if request.body_parameter.typedef is None:
            raise ValueError("Unexpected None typedef of body_parameter in request {!r}".format(request.operation_id))

        if not request.body_parameter.required:
            fid.write('Json.Encode.Extra.maybe ({}'.format(_type_encoder(request.body_parameter.typedef)))
        fid.write('({}'.format(_type_encoder(request.body_parameter.typedef)))

        fid.write(' {}) |> Http.jsonBody'.format(swagger_to.camel_case(identifier=request.body_parameter.name)))
    else:
        fid.write('Http.emptyBody')
    fid.write('\n')
    if return_type is None:
        fid.write(INDENT * (indent + 1) + ', expect = Http.expectString\n')
    else:
        fid.write(INDENT * (indent + 1) + ', expect = Http.expectJson {}\n'.format(return_type_decoder))
    fid.write(INDENT * (indent + 1) + ', headers = []\n')
    fid.write(INDENT * (indent + 1) + ', method = "{}"\n'.format(mth))
    fid.write(INDENT * (indent + 1) + ', timeout = maybeTimeout\n')
    fid.write(INDENT * (indent + 1) + ', url = url\n')
    fid.write(INDENT * (indent + 1) + ', withCredentials = withCredentials\n')
    fid.write(INDENT * (indent + 1) + '}\n')


def _write_type_definitions(typedefs: MutableMapping[str, Typedef], fid: TextIO) -> None:
    """
    Write all type definitions as Elm code.

    :param typedefs: type definitions to be declared
    :param fid: target
    :return:
    """
    assert typedefs
    fid.write('-- Models\n\n\n')
    for i, typedef in enumerate(typedefs.values()):
        if i > 0:
            fid.write('\n\n\n')

        _write_type_definition(typedef=typedef, fid=fid)
    fid.write('\n\n\n')


def _write_encoders(typedefs: MutableMapping[str, Typedef], fid: TextIO) -> None:
    """
    Write all JSON encoders as Elm code.

    :param typedefs: type definitions to be encoded
    :param fid: target
    :return:
    """
    assert typedefs
    fid.write('-- Encoders\n\n\n')
    for i, typedef in enumerate(typedefs.values()):
        if i > 0:
            fid.write('\n\n\n')

        _write_encoder(typedef=typedef, fid=fid)

    fid.write('\n\n\n')


def _write_decoders(typedefs: MutableMapping[str, Typedef], fid: TextIO) -> None:
    """
    Write all JSON decoders as Elm code.

    :param typedefs: type definitions to be decoded
    :param fid: target
    :return:
    """
    assert typedefs
    fid.write('-- Decoders\n\n\n')
    for i, typedef in enumerate(typedefs.values()):
        if i > 0:
            fid.write('\n\n\n')

        _write_decoder(typedef=typedef, fid=fid)

    fid.write('\n\n\n')


def _write_client(requests: List[Request], fid: TextIO) -> None:
    """
    Generate the client.

    :param requests: translated request functions
    :param fid: target
    :return:
    """
    assert requests
    fid.write("-- Remote Calls\n\n")

    for request in requests:
        fid.write('\n\n')
        _write_request(request=request, fid=fid)

    fid.write("\n\n\n")


def _write_header(fid: TextIO, typedefs: MutableMapping[str, Typedef], requests: List[Request]) -> None:
    """
    Write the header.

    :param fid: target
    :param typedefs: translated type definitions
    :param requests: translated request functions
    :return:
    """
    fid.write("-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n\n\n")

    to_expose = []  # Type: List[str]

    for typedef in typedefs.values():
        to_expose.append(typedef.identifier)
        to_expose.append('decode{}'.format(typedef.identifier))
        to_expose.append('encode{}'.format(typedef.identifier))

    for request in requests:
        to_expose.append('{}Request'.format(_request_function_name(request.operation_id)))

    to_expose.sort()
    joinstr = '\n' + INDENT * 2 + ', '
    fid.write("module Client \n")
    fid.write(INDENT + "exposing\n")
    fid.write(INDENT * 2 + "( {}\n".format(joinstr.join(to_expose)))
    fid.write(INDENT * 2 + ")\n\n")
    fid.write("import Dict exposing (Dict)\n"
              "import Http\n"
              "import Json.Decode\n"
              "import Json.Decode.Pipeline\n"
              "import Json.Encode\n"
              "import Json.Encode.Extra\n"
              "import Time\n\n\n")


def _write_footer(fid: TextIO) -> None:
    """
    Write the footer (same for all the Elm clients).

    :param fid: target
    :return:
    """
    fid.write("-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n")


def _write_query_function(fid: TextIO) -> None:
    """
    Write the function needed to translate query parameters into a string.

    :param fid: target
    :return:
    """
    fid.write('{-| Translates a list of (name, parameter) and a list of (name, optional parameter) to a\n')
    fid.write('well-formatted query string.\n')
    fid.write('-}\n')
    fid.write('paramsToQuery : List ( String, String ) -> List ( String, Maybe String ) -> String\n')
    fid.write('paramsToQuery params maybeParams =\n')

    fid.write(INDENT + 'let\n')
    fid.write(INDENT * 2 + 'queryParams : List String\n')
    fid.write(INDENT * 2 + 'queryParams =\n')
    fid.write(INDENT * 3 + 'List.map (\\( name, value ) -> name ++ "=" ++ Http.encodeUri value) params\n\n')
    fid.write(INDENT * 2 + 'filteredParams : List String\n')
    fid.write(INDENT * 2 + 'filteredParams =\n')
    fid.write(INDENT * 3 + 'List.filter (\\( _, maybeValue ) -> maybeValue /= Nothing) maybeParams\n')
    fid.write(INDENT * 4 + '|> List.map (\\( name, maybeValue ) -> ( name, Maybe.withDefault "" maybeValue ))\n')
    fid.write(INDENT * 4 + '|> List.map (\\( name, value ) -> name ++ "=" ++ Http.encodeUri value)\n')

    fid.write(INDENT + 'in\n')
    fid.write(INDENT + 'List.concat [queryParams, filteredParams]\n')
    fid.write(INDENT * 2 + '|> String.join "&"\n')
    fid.write(INDENT * 2 + '|> \\str ->\n')
    fid.write(INDENT * 3 + 'if String.isEmpty str then\n')
    fid.write(INDENT * 4 + '""\n')
    fid.write(INDENT * 3 + 'else\n')
    fid.write(INDENT * 4 + '"?" ++ str\n')


def _type_expression(typedef: Typedef, path: Optional[str] = None) -> str:
    """
    Translate the typedef to a type expression.

    :param typedef: to be translated
    :param path: path in the intermediate representation
    :return: type expression
    """
    # pylint: disable=too-many-return-statements

    if isinstance(typedef, Booldef):
        return 'Bool'
    elif isinstance(typedef, Floatdef):
        return 'Float'
    elif isinstance(typedef, Intdef):
        return 'Int'
    elif isinstance(typedef, Stringdef):
        return 'String'
    elif isinstance(typedef, Listdef):
        if typedef.items is None:
            raise ValueError("Unexpected None items in typedef {!r}".format(typedef.identifier))

        return 'List ' + _type_expression(typedef=typedef.items, path=str(path) + '.items')
    elif isinstance(typedef, Dictdef):
        if typedef.values is None:
            raise ValueError("Unexpected None values in typedef {!r}".format(typedef.identifier))

        return 'Dict String ' + _type_expression(typedef=typedef.values, path=str(path) + '.values')
    elif isinstance(typedef, Recorddef):
        if typedef.identifier == '':
            raise NotImplementedError(
                "Translating an anonymous class to an Elm type expression is not supported: {}".format(path))

        return typedef.identifier
    else:
        raise NotImplementedError("Translating the typedef to a type expression is not supported: {!r}: {}".format(
            type(typedef), path))


def _type_encoder(typedef: Typedef, path: Optional[str] = None) -> str:
    """
    Translate the typedef to a type encoder.

    :param typedef: to be translated
    :param path: path in the intermediate representation
    :return: type encoder
    """
    # pylint: disable=too-many-return-statements

    if isinstance(typedef, Booldef):
        return 'Json.Encode.bool'
    elif isinstance(typedef, Floatdef):
        return 'Json.Encode.float'
    elif isinstance(typedef, Intdef):
        return 'Json.Encode.int'
    elif isinstance(typedef, Stringdef):
        return 'Json.Encode.string'
    elif isinstance(typedef, Listdef):
        if typedef.items is None:
            raise ValueError("Unexpected None items in typedef {!r}".format(typedef.identifier))

        return 'Json.Encode.list <| List.map ' + _type_encoder(typedef=typedef.items, path=str(path) + '.items')
    elif isinstance(typedef, Dictdef):
        if typedef.values is None:
            raise ValueError("Unexpected None values in typedef {!r}".format(typedef.identifier))

        return 'Json.Encode.Extra.dict identity ' + _type_encoder(typedef=typedef.values, path=str(path) + '.values')
    elif isinstance(typedef, Recorddef):
        if typedef.identifier == '':
            raise NotImplementedError(
                "Translating an anonymous class to an Elm type expression is not supported: {}".format(path))

        return 'encode' + typedef.identifier
    else:
        raise NotImplementedError("Translating the typedef to an encoder is not supported: {!r}: {}".format(
            type(typedef), path))


def _type_decoder(typedef: Typedef, path: Optional[str] = None) -> str:
    """
    Translate the typedef to a type decoder.

    :param typedef: to be translated
    :param path: path in the intermediate representation
    :return: type decoder
    """
    # pylint: disable=too-many-return-statements

    if isinstance(typedef, Booldef):
        return 'Json.Decode.bool'
    elif isinstance(typedef, Floatdef):
        return 'Json.Decode.float'
    elif isinstance(typedef, Intdef):
        return 'Json.Decode.int'
    elif isinstance(typedef, Stringdef):
        return 'Json.Decode.string'
    elif isinstance(typedef, Listdef):
        if typedef.items is None:
            raise ValueError("Unexpected None items in typedef {!r}".format(typedef.identifier))

        return 'Json.Decode.list <| ' + _type_decoder(typedef=typedef.items, path=str(path) + '.items')
    elif isinstance(typedef, Dictdef):
        if typedef.values is None:
            raise ValueError("Unexpected None values in typedef {!r}".format(typedef.identifier))

        return 'Json.Decode.dict <| ' + _type_decoder(typedef=typedef.values, path=str(path) + '.values')
    elif isinstance(typedef, Recorddef):
        if typedef.identifier == '':
            raise NotImplementedError(
                "Translating an anonymous class to an Elm type expression is not supported: {}".format(path))

        return 'decode' + typedef.identifier
    else:
        raise NotImplementedError("Translating the typedef to a decoder is not supported: {!r}: {}".format(
            type(typedef), path))


def elm_package_json() -> MutableMapping[str, Any]:
    """
    Generate the elm-package json file.

    :return: The JSON Elm package for the project as a Dictionary.
    """
    elm_pkg = collections.OrderedDict()  # type: Dict[str, Any]
    elm_pkg['version'] = '1.1.0'
    elm_pkg['summary'] = ''
    elm_pkg['repository'] = 'https://github.com/invalid/repo.git'
    elm_pkg['license'] = ''
    elm_pkg['source-directories'] = ['src']
    elm_pkg['exposed-modules'] = []

    packages = collections.OrderedDict()  # type: Dict[str, str]
    packages['elm-lang/core'] = '2.0.0 <= v <= 2.0.0'
    packages['elm-lang/http'] = '1.0.0 <= v <= 1.0.0'
    packages['elm-community/json-extra'] = '2.7.0 <= v <= 2.7.0'
    packages['NoRedInk/elm-decode-pipeline'] = '3.0.0 <= v <= 3.0.0'

    elm_pkg['dependencies'] = packages
    elm_pkg['elm-version'] = '0.18.0 <= v < 0.19.0'

    return elm_pkg


def write_client_elm(typedefs: MutableMapping[str, Typedef], requests: List[Request], fid: TextIO) -> None:
    """
    Generate the file with the client code.

    :param typedefs: translated type definitions
    :param requests: translated request functions
    :param fid: target
    :return:
    """
    _write_header(fid=fid, typedefs=typedefs, requests=requests)

    if typedefs:
        _write_type_definitions(typedefs=typedefs, fid=fid)

        _write_encoders(typedefs=typedefs, fid=fid)

        _write_decoders(typedefs=typedefs, fid=fid)

    if requests:
        _write_client(requests=requests, fid=fid)

        for request in requests:
            if request.query_parameters:
                _write_query_function(fid=fid)
                break

    _write_footer(fid=fid)


@icontract.require(lambda operation_id: operation_id != '')
def _request_function_name(operation_id: str) -> str:
    """
    Generate the name of the function which will send the request based on the operation ID.

    :param operation_id: ID of the operation from the Swagger spec
    :return: Valid Elm identifier

    >>> _request_function_name('CamelCase')
    'camelCase'

    >>> _request_function_name('snake_case')
    'snakeCase'

    >>> _request_function_name('Snake_case')
    'snakeCase'

    >>> _request_function_name('Dash-Case')
    'dashCase'

    >>> _request_function_name('dash-case')
    'dashCase'

    >>> _request_function_name('_snake_case')
    '_snakeCase'

    >>> _request_function_name('snake_case_')
    'snakeCase_'

    >>> _request_function_name('__')
    '__'

    >>> _request_function_name('test.me')
    'testMe'

    >>> _request_function_name('test.me.some.more')
    'testMeSomeMore'
    """
    identifier = operation_id.replace('.', '_')
    return swagger_to.camel_case(identifier)
