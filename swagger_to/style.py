#!/usr/bin/env python3
"""
Generates code for an Elm client.
"""
# pylint: disable=too-many-lines
from typing import MutableSet, MutableMapping, List, Optional

import swagger_to.intermediate
import swagger_to.swagger
import swagger_to


def check_header(swagger: swagger_to.swagger) -> List[str]:
    """
    Checks whether the swagger header conforms to the style guide.

    :param swagger: parsed swagger file
    :return: the list of failed checks
    """
    errs = []  # type: List[str]

    if swagger.name != swagger_to.snake_case(swagger.name):
        errs.append("Name of the Swagger specification is not snake case: {}".format(swagger.name))

    if not swagger.base_path.startswith("/"):
        errs.append("Swagger base path doesn't start with a slash: {}".format(swagger.base_path))

    if swagger.description.capitalize() != swagger.description:
        errs.append("Swagger description should be capitalized: \"{}\"")

    return errs


def check_casing_typedefs(typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> List[str]:
    """
    Checks whether the typedefs conform to the casing conventions.

    :param typedefs: swagger type definitions
    :return: the list of failed checks
    """
    errs = []  # type: List[str]

    seen_typedefs = set()  # type: MutableSet
    for _, typedef in enumerate(typedefs.values()):
        errs.extend(_check_recursively_cases(typedef=typedef, visited=seen_typedefs))

    return errs


def check_casing_endpoints(endpoints: List[swagger_to.intermediate.Endpoint]) -> List[str]:
    """
    Checks whether the endpoints conform to the casing conventions.

    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    errs = []  # type: List[str]

    for endpoint in endpoints:
        if endpoint.path != swagger_to.snake_case(endpoint.path):
            errs.append("Path doesn't conform to snake case: {}".format(endpoint.path))
        if endpoint.operation_id != swagger_to.snake_case(endpoint.operation_id):
            errs.append("Endpoint operation ID is not a snake case identifier: {}".format(endpoint.operation_id))
        for param in endpoint.parameters:
            if param.name != swagger_to.snake_case(param.name):
                errs.append("Parameter has not a snake case identifier: {}".format(param.name))

    return errs


def check_descriptions_typedefs(typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> List[str]:
    """
    Checks whether the typedefs conform to the description conventions.

    :param typedefs: swagger type definitions
    :return: the list of failed checks
    """
    errs = []  # type: List[str]

    seen_typedefs = set()  # type: MutableSet
    for _, typedef in enumerate(typedefs.values()):
        errs.extend(_check_recursively_descriptions(typedef=typedef, visited=seen_typedefs))

    return errs


def check_descriptions_endpoints(endpoints: List[swagger_to.intermediate.Endpoint]) -> List[str]:
    """
    Checks whether the endpoints conform to the description conventions.

    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    errs = []  # type: List[str]

    for endpoint in endpoints:
        if check_description(endpoint.description):
            errs.append("The endpoint description is invalid: {}".format(check_description(endpoint.description)))
        for param in endpoint.parameters:
            if check_description(param.description):
                errs.append("The parameter description is invalid: {}".format(check_description(param.description)))
        for _, resp in enumerate(endpoint.responses.values()):
            if check_description(resp.description):
                errs.append("The response description is invalid: {}".format(check_description(resp.description)))

    return errs


def _check_recursively_cases(typedef: swagger_to.intermediate.Typedef,
                             visited: MutableSet[swagger_to.intermediate.Typedef]) -> List[str]:
    """
    Checks the typedef's adherence to the casing conventions.

    :param typedef: to be translated
    :param visited: already seen typedefs
    :return: the list of failed checks
    """
    errs = []  # type: List[str]
    if typedef in visited:
        return errs

    visited.add(typedef)

    if isinstance(typedef, swagger_to.intermediate.Primitivedef):
        pass

    elif isinstance(typedef, swagger_to.intermediate.Arraydef):
        errs.extend(_check_recursively_cases(typedef=typedef.items, visited=visited))

    elif isinstance(typedef, swagger_to.intermediate.Mapdef):
        errs.extend(_check_recursively_cases(typedef=typedef.values, visited=visited))

    elif isinstance(typedef, swagger_to.intermediate.Objectdef):

        if typedef.identifier != "" and typedef.identifier != swagger_to.capital_camel_case(typedef.identifier):
            errs.append("Not a capital camel case identifier: {}".format(typedef.identifier))

        for prop in typedef.properties.values():
            if prop.name != swagger_to.snake_case(prop.name):
                errs.append("Not a capital camel case identifier: {}".format(prop.name))
            errs.extend(_check_recursively_cases(typedef=prop.typedef, visited=visited))

    return errs


def _check_recursively_descriptions(typedef: swagger_to.intermediate.Typedef,
                                    visited: MutableSet[swagger_to.intermediate.Typedef]) -> List[str]:
    """
    Checks the typedef's adherence to the description conventions.

    :param typedef: to be translated
    :param visited: already seen typedefs
    :return: the list of failed checks
    """
    errs = []  # type: List[str]
    if typedef in visited:
        return errs

    visited.add(typedef)

    if isinstance(typedef, swagger_to.intermediate.Primitivedef):
        pass

    elif isinstance(typedef, swagger_to.intermediate.Arraydef):
        errs.extend(_check_recursively_descriptions(typedef=typedef.items, visited=visited))

    elif isinstance(typedef, swagger_to.intermediate.Mapdef):
        errs.extend(_check_recursively_descriptions(typedef=typedef.values, visited=visited))

    elif isinstance(typedef, swagger_to.intermediate.Objectdef):
        if check_description(typedef.description):
            errs.append("The object description is invalid: {}".format(check_description(typedef.description)))

        for prop in typedef.properties.values():
            if check_description(prop.description):
                errs.append("The property description is invalid: {}".format(check_description(prop.description)))
                errs.extend(_check_recursively_descriptions(typedef=prop.typedef, visited=visited))

    return errs


def check_endpoint_responses(endpoints: List[swagger_to.intermediate.Endpoint]) -> List[str]:
    """
    Checks whether the endpoints conform to the conventions for responses.

    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    errs = []  # type: List[str]

    for endpoint in endpoints:
        if "200" not in endpoint.responses.keys():
            errs.append("Path doesn't include response 200: {}".format(endpoint.path))
        if "default" not in endpoint.responses.keys():
            errs.append("Path doesn't include default response: {}".format(endpoint.path))

    return errs


def check_endpoint_path(endpoints: List[swagger_to.intermediate.Endpoint]) -> List[str]:
    """
    Checks whether the endpoints conform to the conventions for paths.

    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    errs = []  # type: List[str]

    for endpoint in endpoints:
        if not endpoint.path.startswith("/"):
            errs.append("Path doesn't begin with a slash: {}".format(endpoint.path))

    return errs


def check_description(description: str) -> Optional[str]:
    """
    Checks whether a description is well-styled.

    :param description: the description
    :return: the failed check, if any
    """
    # pylint: disable=too-many-return-statements
    if description == "":
        return None

    trimmed = description.replace("|", "")

    if not trimmed[:1].isalpha():
        return "should start with alphanumeric letter: {}".format(description)

    if trimmed[:1].isupper():
        return "should start with lower case letter: {}".format(description)

    words = trimmed.split(' ')

    if not words[0].endswith('s'):
        return "should start with verb in present tense: {}".format(description)

    lines = trimmed.splitlines()

    if not lines[0].endswith('.'):
        return "first line should end with a period: {}".format(description)
    for i, word in enumerate(lines):
        if i == 1 and word != "":
            return "second line should be empty: {}".format(description)
        elif i != 1 and word == "":
            return "no line apart from the second should be empty: {}".format(description)

    if not trimmed.endswith("."):
        return "should end with a period: {}".format(description)

    if trimmed.strip() != trimmed:
        return "should not contain leading or trailing whitespaces: {}".format(description)

    return None


def perform(swagger: swagger_to.swagger.Swagger, typedefs: MutableMapping[str, swagger_to.intermediate.Typedef],
            endpoints: List[swagger_to.intermediate.Endpoint]) -> List[str]:
    """
    Checks whether the typedefs and endpoints conform to the swagger style guide.

    :param swagger: parsed swagger file
    :param typedefs: swagger type definitions
    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    errs = []  # type: List[str]

    errs.extend(check_header(swagger=swagger))

    errs.extend(check_casing_typedefs(typedefs=typedefs))

    errs.extend(check_casing_endpoints(endpoints=endpoints))

    errs.extend(check_descriptions_typedefs(typedefs=typedefs))

    errs.extend(check_descriptions_endpoints(endpoints=endpoints))

    errs.extend(check_endpoint_path(endpoints=endpoints))

    errs.extend(check_endpoint_responses(endpoints=endpoints))

    errs.sort()
    return errs
