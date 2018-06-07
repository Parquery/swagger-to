#!/usr/bin/env python3
"""
Generates server stubs from Swagger specification in Go.
"""

# pylint: disable=missing-docstring,too-many-instance-attributes,too-many-locals,too-many-ancestors,too-many-branches
# pylint: disable=too-many-statements, too-many-lines

import collections
import io
from typing import MutableMapping, Union, Set, List, TextIO, Optional  # pylint: disable=unused-import

import swagger_to
import swagger_to.intermediate
import swagger_to.swagger


class JsonSchema:
    def __init__(self):
        self.identifier = ''
        self.text = ''

    def text_identifier(self) -> str:
        """
        :return: name of the global variable holding the schema text
        """
        return 'jsonSchema{}Text'.format(swagger_to.capital_camel_case(self.identifier))

    def schema_identifier(self) -> str:
        """
        :return: name of the global variable holding the schema
        """
        return 'jsonSchema{}'.format(swagger_to.capital_camel_case(self.identifier))

    def validate_func_name(self) -> str:
        """
        :return: name of the function that validate the object against the schema.
        """
        return 'ValidateAgainst{}Schema'.format(swagger_to.capital_camel_case(self.identifier))


def to_json_schema(intermediate_schema: swagger_to.intermediate.JsonSchema) -> JsonSchema:
    """
    Converts the intermediate schema to a representation that we can use to easily generate go code.

    :param intermediate_schema: intermediate representation of a JSON schema
    :return: go-suitable representation
    """
    schema = JsonSchema()
    schema.identifier = intermediate_schema.identifier
    schema.text = intermediate_schema.text

    return schema


class Typedef:
    def __init__(self):
        self.identifier = ''
        self.description = ''
        self.json_schema = None  # type: Union[None, JsonSchema]


class Fielddef:
    def __init__(self):
        self.typedef = None  # type: Union[None, Typedef]
        self.description = ''
        self.json_name = ''
        self.name = ''


class Structdef(Typedef):
    def __init__(self):
        super().__init__()

        self.fields = collections.OrderedDict()  # type: MutableMapping[str, Fielddef]
        self.required = []  # type: List[str]


class Arraydef(Typedef):
    def __init__(self):
        super().__init__()

        self.items = None  # type: Union[None, Typedef]


class Mapdef(Typedef):
    def __init__(self):
        super().__init__()

        self.values = None  # type: Union[None, Typedef]


class Pointerdef(Typedef):
    def __init__(self):
        super().__init__()

        self.pointed = None  # type: Union[None, Typedef]


class Primitivedef(Typedef):
    def __init__(self):
        super().__init__()

        self.type = ''


def to_typedef(intermediate_typedef: swagger_to.intermediate.Typedef) -> Typedef:
    typedef = None  # type: Union[None, Typedef]

    if isinstance(intermediate_typedef, swagger_to.intermediate.Primitivedef):
        typedef = Primitivedef()

        if intermediate_typedef.type == 'string':
            if intermediate_typedef.format == 'date-time':
                typedef.type = 'time.Time'
            else:
                typedef.type = 'string'
        elif intermediate_typedef.type == 'number':
            if intermediate_typedef.format == '':
                typedef.type = 'float64'
            elif intermediate_typedef.format == 'float':
                typedef.type = 'float32'
            elif intermediate_typedef.format == 'double':
                typedef.type = 'float64'
            else:
                raise ValueError("Unexpected format {!r} for type {!r}".format(intermediate_typedef.format,
                                                                               intermediate_typedef.type))

        elif intermediate_typedef.type == 'integer':
            if intermediate_typedef.format == '':
                typedef.type = 'int'
            elif intermediate_typedef.format == 'int32':
                typedef.type = 'int32'
            elif intermediate_typedef.format == 'int64':
                typedef.type = 'int64'
            else:
                raise ValueError("Unexpected format {!r} for type {!r}".format(intermediate_typedef.format,
                                                                               intermediate_typedef.type))

        elif intermediate_typedef.type == 'boolean':
            typedef.type = 'bool'

        else:
            raise NotImplementedError(
                "Unhandled translation of a primitive intermediate type to Go with 'type': {!r}".format(
                    intermediate_typedef.type))

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Arraydef):
        if intermediate_typedef.items is None:
            raise ValueError("Unexpected intermediate type definition of an array to have items None: {!r}".format(
                intermediate_typedef.identifier))

        typedef = Arraydef()
        typedef.items = to_typedef(intermediate_typedef=intermediate_typedef.items)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Mapdef):
        typedef = Mapdef()
        typedef.values = to_typedef(intermediate_typedef=intermediate_typedef.values)

    elif isinstance(intermediate_typedef, swagger_to.intermediate.Objectdef):
        typedef = Structdef()

        for propdef in intermediate_typedef.properties.values():
            field = Fielddef()

            field_typedef = to_typedef(intermediate_typedef=propdef.typedef)
            if not propdef.name in intermediate_typedef.required and isinstance(field_typedef, Primitivedef):
                optional_field_typedef = Pointerdef()
                optional_field_typedef.pointed = field_typedef
                field_typedef = optional_field_typedef

            field.typedef = field_typedef
            field.description = propdef.description
            field.json_name = propdef.name
            field.name = swagger_to.capital_camel_case(identifier=propdef.name)

            typedef.fields[field.name] = field

            if propdef.name in intermediate_typedef.required:
                typedef.required.append(field.name)

    else:
        raise NotImplementedError("Unhandled translation of an intermediate type to Go: {!r}".format(
            type(intermediate_typedef)))

    assert typedef is not None

    if intermediate_typedef.identifier != '':
        typedef.identifier = swagger_to.capital_camel_case(identifier=intermediate_typedef.identifier)

    typedef.description = intermediate_typedef.description

    typedef.json_schema = to_json_schema(intermediate_schema=intermediate_typedef.json_schema)

    return typedef


def to_typedefs(
        intermediate_typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> MutableMapping[str, Typedef]:
    typedefs = collections.OrderedDict()  # type: MutableMapping[str, Typedef]

    for intermediate_typedef in intermediate_typedefs.values():
        assert intermediate_typedef is not None

        typedef = to_typedef(intermediate_typedef=intermediate_typedef)
        typedefs[typedef.identifier] = typedef

    return typedefs


def anonymous_or_get_typedef(intermediate_typedef: swagger_to.intermediate.Typedef,
                             typedefs: MutableMapping[str, Typedef]) -> Typedef:
    if intermediate_typedef.identifier != '':
        identifier = swagger_to.capital_camel_case(identifier=intermediate_typedef.identifier)

        if not identifier in typedefs:
            raise ValueError("Undefined Go type for intermediate typedef {!r}: {!r}".format(
                intermediate_typedef.identifier, identifier))

        return typedefs[identifier]

    return to_typedef(intermediate_typedef=intermediate_typedef)


def walk(typedef: Typedef, parent: Optional[Typedef]):
    yield parent, typedef

    if isinstance(typedef, Primitivedef):
        pass

    elif isinstance(typedef, Pointerdef):
        yield from walk(typedef=typedef.pointed, parent=typedef)

    elif isinstance(typedef, Arraydef):
        yield from walk(typedef=typedef.items, parent=typedef)

    elif isinstance(typedef, Mapdef):
        yield from walk(typedef=typedef.values, parent=typedef)

    elif isinstance(typedef, Structdef):
        for fielddef in typedef.fields.values():
            yield from walk(typedef=fielddef.typedef, parent=typedef)

    else:
        raise NotImplementedError("walk for Go type definition of type: {}".format(type(typedef)))


INDENT = '\t'


def write_description(description: str, fid: TextIO, indention: str) -> None:
    lines = description.strip().splitlines()
    for i, line in enumerate(lines):
        rstripped = line.rstrip()
        if len(rstripped) > 0:
            fid.write(indention + '// {}'.format(rstripped))
        else:
            fid.write(indention + '//')

        if i < len(lines) - 1:
            fid.write('\n')


def write_type_code_or_identifier(typedef: Typedef, fid: TextIO, indention: str) -> None:
    if typedef.identifier != '':
        fid.write(typedef.identifier)

    else:
        write_type_code(typedef=typedef, fid=fid, indention=indention)


def write_type_code(typedef: Typedef, fid: TextIO, indention: str) -> None:
    if isinstance(typedef, Primitivedef):
        fid.write(typedef.type)

    elif isinstance(typedef, Pointerdef):
        fid.write('*')
        write_type_code_or_identifier(typedef=typedef.pointed, fid=fid, indention=indention)

    elif isinstance(typedef, Arraydef):
        fid.write('[]')
        write_type_code_or_identifier(typedef=typedef.items, fid=fid, indention=indention)

    elif isinstance(typedef, Mapdef):
        fid.write('map[string]')
        write_type_code_or_identifier(typedef=typedef.values, fid=fid, indention=indention)

    elif isinstance(typedef, Structdef):
        fid.write('struct {\n')

        has_description = False
        for fielddef in typedef.fields.values():
            if fielddef.description != '':
                has_description = True

        for i, fielddef in enumerate(typedef.fields.values()):
            if fielddef.description != '':
                write_description(description=fielddef.description, fid=fid, indention=indention + INDENT)
                if fielddef.description != '':
                    fid.write('\n')

            fid.write(indention + INDENT)
            fid.write(fielddef.name + " ")
            write_type_code_or_identifier(typedef=fielddef.typedef, fid=fid, indention=indention + INDENT)
            fid.write(" ")

            if fielddef.name in typedef.required:
                fid.write('`json:"{}"`'.format(fielddef.json_name))
            else:
                fid.write('`json:"{},omitempty"`'.format(fielddef.json_name))

            if i < len(typedef.fields) - 1:
                fid.write("\n")

                # if at least one field has a description, add a new line for easier reading
                if has_description:
                    fid.write('\n')

        fid.write('}')

    else:
        raise NotImplementedError("No Go type writing defined for typedef of type: {!r}".format(type(typedef)))


def write_type_definition(typedef: Typedef, fid: io.StringIO) -> None:
    fid.write("type {} ".format(typedef.identifier))


def write_imports(import_set: Set[str], fid: TextIO) -> None:
    import_lst = sorted(list(import_set))

    if len(import_lst) == 1:
        fid.write('import "{}"'.format(import_lst[0]))
    elif len(import_lst) > 1:
        fid.write("import (\n")
        for import_stmt in import_lst:
            fid.write(INDENT + '"{}"\n'.format(import_stmt))
        fid.write(")")


def write_types_go(package: str, typedefs: MutableMapping[str, Typedef], fid: TextIO) -> None:
    """
    Generates a file which defines all the involved types.

    :param package: name of the package
    :param typedefs: type definitions
    :param fid: where output is written to
    :return:
    """
    fid.write("package {}\n\n".format(package))

    fid.write("// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n\n")

    # imports
    import_set = set()  # type: Set[str]
    for typedef in typedefs.values():
        for _, another_typedef in walk(typedef=typedef, parent=None):
            if isinstance(another_typedef, Primitivedef):
                if another_typedef.type == 'time.Time':
                    import_set.add('time')

    write_imports(import_set=import_set, fid=fid)
    if len(import_set) > 0:
        fid.write('\n\n')

    # type definitions
    for i, typedef in enumerate(typedefs.values()):
        if typedef.description != '':
            write_description(description=typedef.identifier + ' ' + typedef.description, fid=fid, indention='')
            fid.write('\n')

        fid.write("type {} ".format(typedef.identifier))
        write_type_code(typedef=typedef, fid=fid, indention='')
        fid.write("\n")

        if i < len(typedefs) - 1:
            fid.write('\n')


class Argument:
    def __init__(self):
        self.typedef = None  # type: Union[None, Typedef]
        self.identifier = ''
        self.in_what = ''
        self.parameter_name = ''
        self.required = False
        self.parsing_identifier = ''
        self.json_schema = None  # type: Optional[JsonSchema]


class Handler:
    def __init__(self):
        self.identifier = ''
        self.arguments = []  # type: List[Argument]
        self.description = ''


class Wrapper:
    def __init__(self):
        self.identifier = ''
        self.description = ''
        self.handler = None  # type: Union[None, Handler]

        self.query_arguments = []  # type: List[Argument]
        self.path_arguments = []  # type: List[Argument]
        self.body_argument = None  # type: Union[None, Argument]


class Route:
    def __init__(self):
        self.description = ''
        self.path = ''
        self.method = ''
        self.wrapper = Wrapper()
        self.handler = Handler()


def endpoint_to_route_path(endpoint: swagger_to.intermediate.Endpoint) -> str:
    """
    Converts an endpoint path to Gorrila Mux route path.

    :param endpoint: whose path we need to convert
    :return: Gorrila Mux route path
    """
    token_pth = swagger_to.tokenize_path(path=endpoint.path)

    tkns = token_pth.tokens[:]

    for param in endpoint.parameters:
        if param.in_what != 'path':
            continue

        if param.name not in token_pth.parameter_to_token_indices:
            continue

        if not isinstance(param.typedef, swagger_to.intermediate.Primitivedef):
            raise ValueError("Expected path parameter {!r} in the path {!r} to be primitive, but got: {!r}".format(
                param.name, endpoint.path, type(param.typedef)))

        assert isinstance(param.typedef, swagger_to.intermediate.Primitivedef)
        if param.typedef.pattern != '':
            param_in_route = '{' + param.name + ":" + param.typedef.pattern + "}"
        else:
            param_in_route = '{' + param.name + '}'

        for i in token_pth.parameter_to_token_indices[param.name]:
            tkns[i] = param_in_route

    return "".join(tkns)


def to_route(endpoint: swagger_to.intermediate.Endpoint, typedefs: MutableMapping[str, Typedef]) -> Route:
    route = Route()
    route.method = endpoint.method.lower()
    route.path = endpoint_to_route_path(endpoint=endpoint)
    route.description = endpoint.description

    # parameters to arguments
    for param in endpoint.parameters:
        if param.in_what == 'formData':
            # no code is generated for the parameters in the form data since there are so many edge cases
            # which we possibly can't cover.
            continue
        elif param.in_what in ['query', 'body', 'path']:
            pass
        else:
            raise NotImplementedError(
                "Handling of parameters in {} is not implemented yet: end point {} {}, parameter {}.".format(
                    param.in_what, endpoint.path, endpoint.method, param.name))

        argument = Argument()
        argument.typedef = anonymous_or_get_typedef(intermediate_typedef=param.typedef, typedefs=typedefs)
        argument.required = param.required

        if not param.required and isinstance(argument.typedef, Primitivedef):
            pointer_typedef = Pointerdef()
            pointer_typedef.identifier = argument.typedef.identifier
            pointer_typedef.description = argument.typedef.description
            pointer_typedef.pointed = argument.typedef

            argument.typedef = pointer_typedef

        argument.parameter_name = param.name
        argument.parsing_identifier = swagger_to.camel_case(identifier='a_' + param.name)
        argument.identifier = swagger_to.camel_case(identifier=param.name)
        argument.in_what = param.in_what

        if param.json_schema is not None:
            argument.json_schema = to_json_schema(intermediate_schema=param.json_schema)

        if argument.in_what == 'query':
            route.wrapper.query_arguments.append(argument)

        elif argument.in_what == 'body':
            route.wrapper.body_argument = argument

        elif argument.in_what == 'path':
            route.wrapper.path_arguments.append(argument)

        else:
            raise AssertionError("Unexpected argument given in: {}".format(argument.in_what))

        route.handler.arguments.append(argument)

    route.wrapper.identifier = swagger_to.capital_camel_case(identifier='wrap_' + endpoint.operation_id)
    route.wrapper.description = '{} wraps the path `{}` with the method "{}"'.format(
        route.wrapper.identifier, route.path, route.method)
    if len(route.description) > 0:
        route.wrapper.description += '\n\nPath description:\n' + route.description

    route.wrapper.handler = route.handler
    route.handler.identifier = swagger_to.capital_camel_case(identifier=endpoint.operation_id)
    route.handler.description = '{} handles the path `{}` with the method "{}".'.format(
        route.handler.identifier, route.path, route.method)
    if len(route.description) > 0:
        route.handler.description += '\n\nPath description:\n' + route.description

    return route


def to_routes(endpoints: List[swagger_to.intermediate.Endpoint], typedefs: MutableMapping[str, Typedef]) -> List[Route]:
    routes = []  # type: List[Route]
    for endpoint in endpoints:
        routes.append(to_route(endpoint=endpoint, typedefs=typedefs))

    return routes


def write_argument_from_string(argument: Argument, string_identifier: str, indention: str, fid: TextIO) -> None:
    tajp = ''
    target_identifier = ''

    if isinstance(argument.typedef, Primitivedef):
        target_identifier = argument.parsing_identifier
        tajp = argument.typedef.type

    elif isinstance(argument.typedef, Pointerdef):
        target_identifier = argument.parsing_identifier

        if isinstance(argument.typedef.pointed, Primitivedef):
            tajp = argument.typedef.pointed.type
    else:
        raise NotImplementedError("Parsing argument from string {!r} of type: {!r}".format(
            string_identifier, type(argument)))

    if tajp == 'string':
        if isinstance(argument.typedef, Pointerdef):
            fid.write(indention + 'val := {}\n'.format(string_identifier))
            fid.write(indention + '{} = &val'.format(target_identifier))
        else:
            fid.write(indention + '{} = {}'.format(target_identifier, string_identifier))

    elif tajp == 'int':
        fid.write(indention + "{\n")
        fid.write(indention + INDENT + 'parsed, err := strconv.ParseInt({}, 10, 64)\n'.format(string_identifier))
        fid.write(indention + INDENT + "if err != nil {\n")
        fid.write(indention + INDENT * 2 + 'http.Error(w, "Parameter \'{}\': "+err.Error(), http.StatusBadRequest)\n'.
                  format(argument.parameter_name))
        fid.write(indention + INDENT * 2 + 'return\n')
        fid.write(indention + INDENT + "}\n")

        fid.write(indention + INDENT + 'converted := int(parsed)\n')

        if isinstance(argument.typedef, Pointerdef):
            fid.write(indention + INDENT + '{} = &converted\n'.format(target_identifier))
        else:
            fid.write(indention + INDENT + '{} = converted\n'.format(target_identifier))

        fid.write(indention + "}")

    elif tajp == 'int64':
        fid.write(indention + "{\n")
        fid.write(indention + INDENT + 'parsed, err := strconv.ParseInt({}, 10, 64)\n'.format(string_identifier))

        fid.write(indention + INDENT + "if err != nil {\n")
        fid.write(indention + INDENT * 2 + 'http.Error(w, "Parameter \'{}\': "+err.Error(), http.StatusBadRequest)\n'.
                  format(argument.parameter_name))
        fid.write(indention + INDENT * 2 + 'return\n')
        fid.write(indention + INDENT + "}\n")

        fid.write(indention + INDENT + 'converted := int64(parsed)\n')

        if isinstance(argument.typedef, Pointerdef):
            fid.write(indention + INDENT + '{} = &converted\n'.format(target_identifier))
        else:
            fid.write(indention + INDENT + '{} = converted\n'.format(target_identifier))

        fid.write(indention + "}")

    elif tajp == 'int32':
        fid.write(indention + "{\n")
        fid.write(indention + INDENT + 'parsed, err := strconv.ParseInt({}, 10, 32)\n'.format(string_identifier))

        fid.write(indention + INDENT + "if err != nil {\n")
        fid.write(indention + INDENT * 2 + 'http.Error(w, "Parameter \'{}\': "+err.Error(), http.StatusBadRequest)\n'.
                  format(argument.parameter_name))
        fid.write(indention + INDENT * 2 + 'return\n')
        fid.write(indention + INDENT + "}\n")

        fid.write(indention + INDENT + 'converted := int32(parsed)\n')

        if isinstance(argument.typedef, Pointerdef):
            fid.write(indention + INDENT + '{} = &converted\n'.format(target_identifier))
        else:
            fid.write(indention + INDENT + '{} = converted\n'.format(target_identifier))

        fid.write(indention + "}")

    elif tajp == 'float32':
        fid.write(indention + "{\n")
        fid.write(indention + INDENT + 'parsed, err := strconv.ParseFloat({}, 32)\n'.format(string_identifier))

        fid.write(indention + INDENT + "if err != nil {\n")
        fid.write(indention + INDENT * 2 + 'http.Error(w, "Parameter \'{}\': "+err.Error(), http.StatusBadRequest)\n'.
                  format(argument.parameter_name))
        fid.write(indention + INDENT * 2 + 'return\n')
        fid.write(indention + INDENT + "}\n")

        fid.write(indention + INDENT + 'converted := float32(parsed)\n')

        if isinstance(argument.typedef, Pointerdef):
            fid.write(indention + INDENT + '{} = &converted\n'.format(target_identifier))
        else:
            fid.write(indention + INDENT + '{} = converted\n'.format(target_identifier))

        fid.write(indention + "}")

    elif tajp == 'float64':
        fid.write(indention + "{\n")
        fid.write(indention + INDENT + 'parsed, err = strconv.ParseFloat({}, 64)\n'.format(string_identifier))

        fid.write(indention + INDENT + "if err != nil {\n")
        fid.write(indention + INDENT * 2 + 'http.Error(w, "Parameter \'{}\': "+err.Error(), http.StatusBadRequest)\n'.
                  format(argument.parameter_name))
        fid.write(indention + INDENT * 2 + 'return\n')
        fid.write(indention + INDENT + "}\n")

        fid.write(indention + INDENT + 'converted := float64(parsed)\n')

        if isinstance(argument.typedef, Pointerdef):
            fid.write(indention + INDENT + '{} = &converted\n'.format(target_identifier))
        else:
            fid.write(indention + INDENT + '{} = converted\n'.format(target_identifier))

        fid.write(indention + "}")

    else:
        raise NotImplementedError("Parsing argument from string {!r} of Go type: {!r}".format(string_identifier, tajp))


def write_parse_argument_from_body(argument: Argument, indention: str, fid: TextIO) -> None:
    fid.write(indention + "{\n")

    fid.write(indention + INDENT + "var err error\n")
    fid.write(indention + INDENT + "r.Body = http.MaxBytesReader(w, r.Body, 1024*1024)\n")
    fid.write(indention + INDENT + 'body, err := ioutil.ReadAll(r.Body)\n')
    fid.write(indention + INDENT + 'if err != nil {\n')
    fid.write(indention + 2 * INDENT + 'http.Error(w, "Body unreadable: "+err.Error(), http.StatusBadRequest)\n')
    fid.write(indention + 2 * INDENT + 'return\n')
    fid.write(indention + INDENT + '}\n\n')

    fid.write(indention + INDENT + "err = {}(body)\n".format(argument.json_schema.validate_func_name()))
    fid.write(indention + INDENT + 'if err != nil {\n')
    fid.write(indention + 2 * INDENT + 'http.Error(w, "Failed to validate against schema: "+err.Error(),\n')
    fid.write(indention + 2 * INDENT + '           http.StatusBadRequest)\n')
    fid.write(indention + 2 * INDENT + 'return\n')
    fid.write(indention + INDENT + '}\n\n')

    fid.write(indention + INDENT + "err = json.Unmarshal(body, &{})\n".format(argument.parsing_identifier))
    fid.write(indention + INDENT + 'if err != nil {\n')
    fid.write(indention + 2 * INDENT + 'http.Error(w, "Error JSON-decoding body parameter \'{}\': "+err.Error(),\n'.
              format(argument.parameter_name))
    fid.write(indention + 3 * INDENT + 'http.StatusBadRequest)\n')
    fid.write(indention + 2 * INDENT + 'return\n')
    fid.write(indention + INDENT + '}\n')

    fid.write(indention + '}')


def write_routes_go(package: str, routes: List[Route], fid: TextIO) -> None:
    """
    Generates the file which defines the router and the routes.

    :param package: name of the package
    :param routes: routes that the router will handle.
    :param fid: where the output is written to
    :return:
    """
    fid.write("package {}\n\n".format(package))
    fid.write("// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n\n")

    # imports
    import_set = {"github.com/gorilla/mux", "net/http"}

    for route in routes:
        for argument in route.handler.arguments:
            if argument.in_what == 'body':
                import_set.add('io/ioutil')
                import_set.add('encoding/json')

            if argument.in_what == 'query':
                tajp = ''
                if isinstance(argument.typedef, Primitivedef):
                    tajp = argument.typedef.type
                elif isinstance(argument.typedef, Pointerdef):
                    if isinstance(argument.typedef.pointed, Primitivedef):
                        tajp = argument.typedef.pointed.type

                if tajp in ['int', 'int32', 'int64', 'float32', 'float64']:
                    import_set.add('strconv')

    write_imports(import_set=import_set, fid=fid)
    if len(import_set) > 0:
        fid.write('\n\n')

    # default router
    fid.write("// SetupRouter sets up a router. If you don't use any middleware, you are good to go.\n"
              "// Otherwise, you need to maually re-implement this function with your middlewares.\n"
              "func SetupRouter(h Handler) *mux.Router {\n")

    fid.write(INDENT + "r := mux.NewRouter()\n")

    for i, route in enumerate(routes):
        if i > 0:
            fid.write('\n\n')

        fid.write(INDENT + "r.HandleFunc(`{}`,\n".format(route.path))
        fid.write(INDENT * 2 + "func(w http.ResponseWriter, r *http.Request) {\n")
        fid.write(INDENT * 3 + "{}(h, w, r)\n".format(route.wrapper.identifier))
        fid.write(INDENT * 2 + '}}).Methods("{}")'.format(route.method))

    if len(routes) > 0:
        fid.write('\n')
    fid.write(INDENT + 'return r\n')

    fid.write("}\n")

    if len(routes) > 0:
        fid.write("\n")

    # wrappers
    for route_i, route in enumerate(routes):
        if route_i > 0:
            fid.write('\n')

        wrapper = route.wrapper
        if len(wrapper.description):
            write_description(description=wrapper.description, fid=fid, indention='')
            fid.write('\n')

        fid.write('func {}(h Handler, w http.ResponseWriter, r *http.Request) {{\n'.format(wrapper.identifier))

        # intermidiate variables
        for argument in route.handler.arguments:
            fid.write(INDENT + 'var {} '.format(argument.parsing_identifier))
            write_type_code_or_identifier(typedef=argument.typedef, fid=fid, indention=INDENT)
            fid.write('\n')

        # query arguments
        if len(route.wrapper.query_arguments) > 0:
            fid.write('\n')
            fid.write(INDENT + "q := r.URL.Query()\n\n")

        for i, argument in enumerate(route.wrapper.query_arguments):
            if i > 0:
                fid.write("\n")

            if argument.required:
                fid.write(INDENT + 'if _, ok := q["{}"]; !ok {{\n'.format(argument.parameter_name))
                fid.write(INDENT * 2 + 'http.Error(w, "Parameter \'{}\' expected in query", http.StatusBadRequest)\n'.
                          format(argument.parameter_name))
                fid.write(INDENT * 2 + 'return\n')
                fid.write(INDENT + "}\n")
                write_argument_from_string(
                    argument=argument,
                    string_identifier='q.Get("{}")'.format(argument.parameter_name),
                    indention=INDENT,
                    fid=fid)
                fid.write('\n')
            else:
                fid.write(INDENT + 'if _, ok := q["{}"]; ok {{\n'.format(argument.parameter_name))
                write_argument_from_string(
                    argument=argument,
                    string_identifier='q.Get("{}")'.format(argument.parameter_name),
                    indention=INDENT * 2,
                    fid=fid)
                fid.write('\n')
                fid.write(INDENT + '}\n')

        # path arguments
        if len(route.wrapper.path_arguments) > 0:
            fid.write("\n")
            fid.write(INDENT + "vars := mux.Vars(r)\n")

        for i, argument in enumerate(route.wrapper.path_arguments):
            if i > 0:
                fid.write("\n")

            fid.write("\n")
            if argument.required:
                fid.write(INDENT + 'if _, ok := vars["{}"]; !ok {{\n'.format(argument.parameter_name))
                fid.write(INDENT * 2 + 'http.Error(w, "Parameter \'{}\' expected in path", http.StatusBadRequest)\n'.
                          format(argument.parameter_name))
                fid.write(INDENT * 2 + 'return\n')
                fid.write(INDENT + "}\n")
                write_argument_from_string(
                    argument=argument,
                    string_identifier='vars["{}"]'.format(argument.parameter_name),
                    indention=INDENT,
                    fid=fid)
                fid.write('\n')
            else:
                fid.write(INDENT + 'if value, ok := vars["{}"]; ok {{\n'.format(argument.parameter_name))
                write_argument_from_string(argument=argument, string_identifier='value', indention=INDENT * 2, fid=fid)
                fid.write('\n}\n')

        # body argument
        if route.wrapper.body_argument is not None:
            if len(route.wrapper.path_arguments) > 0 or len(route.wrapper.query_arguments) > 0:
                fid.write('\n')

            if route.wrapper.body_argument.required:
                fid.write(INDENT + 'if r.Body == nil {\n')
                fid.write(INDENT * 2 + (
                    'http.Error(w, "Parameter \'{}\' expected in body, '
                    'but got no body", http.StatusBadRequest)\n').format(route.wrapper.body_argument.parameter_name))

                fid.write(INDENT * 2 + 'return\n')
                fid.write(INDENT + '}\n')

                write_parse_argument_from_body(argument=route.wrapper.body_argument, indention=INDENT, fid=fid)
                fid.write('\n')
            else:
                fid.write(INDENT + 'if r.Body != nil {\n')
                write_parse_argument_from_body(argument=route.wrapper.body_argument, indention=2 * INDENT, fid=fid)
                fid.write('\n')
                fid.write(INDENT + '}\n')

        # call handler
        if len(route.wrapper.query_arguments) > 0 or \
                len(route.wrapper.path_arguments) > 0 or route.wrapper.body_argument is not None:
            fid.write("\n")
        prefix = INDENT + 'h.{}('.format(route.handler.identifier)
        fid.write(prefix)

        fid.write('w,\n')
        fid.write(2 * INDENT + 'r')

        for argument in route.handler.arguments:
            fid.write(",\n")
            fid.write(2 * INDENT + argument.parsing_identifier)
        fid.write(")")

        fid.write('\n}\n')

    fid.write("\n// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n")


def write_handler_impl_go(package: str, routes: List[Route], fid: TextIO) -> None:
    """
    Generates the file which implements the handler interface with empty methods.

    :param package: name of the package
    :param routes: that a handler will handle
    :param fid: where the output is written to
    :return:
    """
    fid.write("package {}\n\n".format(package))

    fid.write('import (\n')
    fid.write(INDENT + '"net/http"\n')
    fid.write(INDENT + '"log"\n')
    fid.write(')\n\n')

    # yapf: disable
    fid.write('// HandlerImpl implements the Handler.\n')
    fid.write('type HandlerImpl struct {\n' +
              INDENT + 'LogErr *log.Logger\n' +
              INDENT + 'LogOut *log.Logger}')
    # yapf: enable

    if routes:
        fid.write('\n\n')

    for i, route in enumerate(routes):
        if i > 0:
            fid.write('\n\n')

        fid.write('// {0} implements Handler.{0}.\n'.format(route.handler.identifier))
        fid.write("func (h *HandlerImpl) {}(".format(route.handler.identifier))
        fid.write('w http.ResponseWriter,\n')
        fid.write(INDENT + 'r *http.Request')

        for argument in route.handler.arguments:
            fid.write(",\n")
            fid.write(INDENT)

            fid.write(argument.identifier + ' ')
            write_type_code_or_identifier(typedef=argument.typedef, fid=fid, indention='')

        fid.write(") {\n")
        fid.write(INDENT + 'http.Error(w, "Not implemented: {}", http.StatusInternalServerError)\n'.format(
            route.handler.identifier))
        fid.write(INDENT + 'h.LogErr.Printf("Not implemented: {}")\n'.format(route.handler.identifier))
        fid.write("}")

    fid.write('\n')


def write_handler_go(package: str, routes: List[Route], fid: TextIO) -> None:
    """
    Generates the file which defines the handler interface.

    :param package: name of the package
    :param routes: that a handler will handle
    :param fid: where the output is written to
    :return:
    """
    fid.write("package {}\n\n".format(package))

    fid.write("// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n\n")

    fid.write('import "net/http"\n\n')

    fid.write('// Handler defines an interface to handling the routes.\n')
    fid.write('type Handler interface {\n')

    for i, route in enumerate(routes):
        if i > 0:
            fid.write('\n')

        if len(route.handler.description) > 0:
            write_description(description=route.handler.description, fid=fid, indention=INDENT)
            fid.write('\n')

        fid.write(INDENT + "{}(".format(route.handler.identifier))
        fid.write('w http.ResponseWriter,\n')
        fid.write(2 * INDENT + 'r *http.Request')

        for argument in route.handler.arguments:
            fid.write(",\n")
            fid.write(2 * INDENT)

            fid.write(argument.identifier + ' ')
            write_type_code_or_identifier(typedef=argument.typedef, fid=fid, indention='')

        fid.write(")\n")

    fid.write('}\n')

    fid.write("\n// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n")


def write_json_schemas_go(package: str, routes: List[Route], typedefs: MutableMapping[str, Typedef],
                          fid: TextIO) -> None:
    """
    Represents the definitions as json schemas and hard-codes them as strings in Go.

    It is assumed that the Swagger definitions already represent a subset of JSON Schema.
    This is theoretically not the case (some formats are swagger-only), but in most cases
    the literal translation should work.

    :param package: package name
    :param routes: needed to generate the parameter schemas if they are not already defined in the definitions
    :param typedefs: type definitions to generate the schemas for
    :param fid: where output is written to
    """
    fid.write("package {}\n\n".format(package))

    fid.write("// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n\n")

    schemas = collections.OrderedDict()  # type: MutableMapping[str, JsonSchema]

    for route in routes:
        if route.wrapper.body_argument is not None:
            if not route.wrapper.body_argument.json_schema.identifier in schemas:
                schemas[route.wrapper.body_argument.json_schema.identifier] = route.wrapper.body_argument.json_schema

    for typedef_id, typedef in typedefs.items():
        if typedef.json_schema is None:
            raise AssertionError("Missing JSON schema for typedef: {!r}".format(typedef_id))

        # Assume the typedef identifiers are unique accross routes and typedefs.
        if typedef.json_schema.identifier not in schemas:
            schemas[typedef.json_schema.identifier] = typedef.json_schema

    if len(schemas) == 0:
        return

    fid.write('import (\n')
    fid.write(INDENT + '"errors"\n')
    fid.write(INDENT + '"fmt"\n')
    fid.write(INDENT + '"github.com/xeipuuv/gojsonschema"\n')
    fid.write(")\n\n")

    fid.write("func mustNewJSONSchema(text string, name string) *gojsonschema.Schema {\n")
    fid.write(INDENT + "loader := gojsonschema.NewStringLoader(text)\n")
    fid.write(INDENT + "schema, err := gojsonschema.NewSchema(loader)\n")
    fid.write(INDENT + "if err != nil {\n")
    fid.write(INDENT * 2 + 'panic(fmt.Sprintf("failed to load JSON Schema %#v: %s", text, err.Error()))\n')
    fid.write(INDENT + "}\n")
    fid.write(INDENT + "return schema\n")
    fid.write("}\n\n")

    for i, schema in enumerate(schemas.values()):
        if i > 0:
            fid.write('\n\n')

        fid.write('var {} = `{}`'.format(schema.text_identifier(), schema.text.replace(r'`', '` + "`" + `')))

    fid.write('\n\n')

    for schema in schemas.values():
        fid.write('var {} = mustNewJSONSchema({}, "{}")\n'.format(schema.schema_identifier(), schema.text_identifier(),
                                                                  schema.identifier))

    fid.write('\n')

    for i, schema in enumerate(schemas.values()):
        if i > 0:
            fid.write('\n\n')

        fid.write("// {} validates a message coming from the client against {} schema.\n".format(
            schema.validate_func_name(), schema.identifier))

        fid.write("func {}(bb []byte) error {{\n".format(schema.validate_func_name()))
        fid.write(INDENT + "loader := gojsonschema.NewStringLoader(string(bb))\n")
        fid.write(INDENT + "result, err := {}.Validate(loader)\n".format(schema.schema_identifier()))
        fid.write(INDENT + "if err != nil {\n")
        fid.write(2 * INDENT + "return err\n")
        fid.write(INDENT + "}\n\n")
        fid.write(INDENT + "if result.Valid() {\n")
        fid.write(2 * INDENT + "return nil\n")
        fid.write(INDENT + "}\n\n")

        fid.write(INDENT + 'msg := ""\n')
        fid.write(INDENT + 'for i, valErr := range result.Errors() {\n')
        fid.write(2 * INDENT + 'if i > 0 {\n')
        fid.write(3 * INDENT + 'msg += ", "\n')
        fid.write(2 * INDENT + '}\n')
        fid.write(2 * INDENT + 'msg += valErr.String()\n')
        fid.write(INDENT + '}\n')
        fid.write(INDENT + "return errors.New(msg)\n")
        fid.write("}")

    fid.write("\n\n// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!\n")
