#!/usr/bin/env python3
"""
Generates code for an Elm client.
"""
from typing import Optional, MutableMapping, List, TextIO
import collections

import swagger_to.intermediate
import swagger_to

INDENT = ' ' * 4


class Typedef:
    """
    Represents an Elm type.
    """

    def __init__(self) -> None:
        self.description = ''
        self.identifier = ''

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.identifier)


class Booldef(Typedef):
    """
    Represents Elm booleans.
    """
    pass


class Intdef(Typedef):
    """
    Represents Elm Ints.
    """
    pass


class BigIntdef(Typedef):
    """
    Represents Elm BigInts.
    """
    pass


class Floatdef(Typedef):
    """
    Represents Elm floating-point numbers.
    """
    pass


class Stringdef(Typedef):
    """
    Represents Elm strings.
    """
    pass


class Listdef(Typedef):
    """
    Represents Elm lists.
    """

    def __init__(self) -> None:
        self.items = None  # type: Optional[Typedef]
        super().__init__()


class Dictdef(Typedef):
    """
    Represents Elm dicts.
    """

    def __init__(self) -> None:
        self.values = None  # type: Optional[Typedef]
        super().__init__()


class Property:
    """
    Represents an Elm record property.
    """

    def __init__(self) -> None:
        self.name = ''
        self.description = ''
        self.typedef = None  # type: Optional[Typedef]
        self.required = False

    def __str__(self) -> str:
        return '{}: {}'.format(self.name, self.typedef)


class Recorddef(Typedef):
    """
    Represents Elm records.
    """

    def __init__(self) -> None:
        self.properties = collections.OrderedDict()  # type: MutableMapping[str, Property]
        super().__init__()


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
    Translates the intermediate typedef to an Elm typedef.

    :param intermediate_typedef: to be translated
    :return:
    """
    typedef = None  # type: Optional[Typedef]

    if isinstance(intermediate_typedef, swagger_to.intermediate.Primitivedef):
        if intermediate_typedef.type == 'boolean':
            typedef = Booldef()
        elif intermediate_typedef.type == "integer":
            if intermediate_typedef.format == "" or intermediate_typedef.format == "int32":
                typedef = Intdef()
            elif intermediate_typedef.format == "int64":
                typedef = BigIntdef()
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
        typedef.items = to_typedef(intermediate_typedef=intermediate_typedef.items)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Dictdef()
        typedef.values = to_typedef(intermediate_typedef=intermediate_typedef.values)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Recorddef()

        for intermediate_prop in intermediate_typedef.properties.values():
            prop = Property()
            prop.description = intermediate_prop.description
            prop.name = intermediate_prop.name
            prop.typedef = to_typedef(intermediate_typedef=intermediate_prop.typedef)
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
    Translates the intermediate typedefs to Elm typedefs.

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

    Otherwise, it is translated on the spot to the corresponding Elm type.

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
    Translates an intermediate parameter to an Elm parameter.

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
    Translates an intermediate response to an Elm response.

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
        raise ValueError("Can not translate an end point to Elm client "
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
            raise NotImplementedError("Unsupported parameter 'in' to Elm translation: {}".format(
                intermediate_param.in_what))

        req.parameters.append(param)

    # parameters are sorted so that first come the required ones; Elm requires the optional ones to come
    # at the end.
    req.parameters.sort(key=lambda param: not param.required)

    for code, intermediate_resp in endpoint.responses.items():
        req.responses[code] = to_response(intermediate_response=intermediate_resp, typedefs=typedefs)

    return req


def to_requests(endpoints: List[swagger_to.intermediate.Endpoint],
                typedefs: MutableMapping[str, Typedef]) -> List[Request]:
    """
    Translates the endpoints to Elm request functions.

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

def write_client_elm(typedefs: MutableMapping[str, Typedef], requests: List[Request], fid: TextIO)->None:
    """
    Generates the file with the client code.

    :param typedefs: translated type definitions
    :param requests: translated request functions
    :param fid: target
    :return:
    """
    # TODO: implement
    raise NotImplementedError("To be implemented")

