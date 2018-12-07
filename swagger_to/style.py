#!/usr/bin/env python3
"""
Generates code for an Elm client.
"""
# pylint: disable=too-many-lines
from typing import MutableSet, MutableMapping, List, Optional

import swagger_to.intermediate
import swagger_to.swagger
import swagger_to


class Complaint:
    """Encapsulates a complaint."""

    def __init__(self, message: str, what: str, where: str, line: int) -> None:
        self.message = message
        self.what = what
        self.where = where
        self.line = line


def check_header(swagger: swagger_to.swagger.Swagger) -> List[Complaint]:
    """
    Checks whether the swagger header conforms to the style guide.

    :param swagger: parsed swagger file
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]

    if swagger.name != swagger_to.snake_case(swagger.name):
        complaints.append(
            Complaint(
                message="Name of the Swagger specification is not snake case (e.g. snake_case)",
                what=swagger.name,
                where="In the Swagger header",
                line=1))

    if not swagger.base_path.startswith("/"):
        complaints.append(
            Complaint(
                message="Swagger base path doesn't start with a slash",
                what=swagger.base_path,
                where="In the Swagger header",
                line=1))

    if swagger.description.capitalize() != swagger.description:
        complaints.append(
            Complaint(
                message="Swagger description should be capitalized",
                what=swagger.description,
                where="In the Swagger header",
                line=1))

    return complaints


def check_casing_typedefs(typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> List[Complaint]:
    """
    Checks whether the typedefs conform to the casing conventions.

    :param typedefs: swagger type definitions
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]

    seen_typedefs = set()  # type: MutableSet
    for _, typedef in enumerate(typedefs.values()):
        complaints.extend(_check_recursively_cases(typedef=typedef, visited=seen_typedefs))

    return complaints


def check_casing_endpoints(endpoints: List[swagger_to.intermediate.Endpoint]) -> List[Complaint]:
    """
    Checks whether the endpoints conform to the casing conventions.

    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]

    for endpoint in endpoints:
        if endpoint.path != swagger_to.snake_case(endpoint.path):
            complaints.append(
                Complaint(
                    message="Path doesn't conform to snake case (e.g. snake_case)",
                    what=endpoint.path,
                    where="In endpoint {}".format(endpoint.operation_id),
                    line=endpoint.line))
        if endpoint.operation_id != swagger_to.snake_case(endpoint.operation_id):
            complaints.append(
                Complaint(
                    message="Endpoint operation ID is not a snake case identifier (e.g. snake_case)",
                    what=endpoint.operation_id,
                    where="In endpoint {}".format(endpoint.operation_id),
                    line=endpoint.line))
        for param in endpoint.parameters:
            if param.name != swagger_to.snake_case(param.name):
                complaints.append(
                    Complaint(
                        message="Parameter has not a snake case identifier (e.g. snake_case)",
                        what=param.name,
                        where="In endpoint {}, parameter {}".format(endpoint.operation_id, param.name),
                        line=param.line))

    return complaints


def check_descriptions_typedefs(typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> List[Complaint]:
    """
    Checks whether the typedefs conform to the description conventions.

    :param typedefs: swagger type definitions
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]

    seen_typedefs = set()  # type: MutableSet
    for _, typedef in enumerate(typedefs.values()):
        complaints.extend(_check_recursively_descriptions(typedef=typedef, visited=seen_typedefs))

    return complaints


def check_descriptions_endpoints(endpoints: List[swagger_to.intermediate.Endpoint]) -> List[Complaint]:
    """
    Checks whether the endpoints conform to the description conventions.

    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]

    for endpoint in endpoints:
        if check_description(endpoint.description):
            complaints.append(
                Complaint(
                    message=check_description(endpoint.description),
                    what=endpoint.description,
                    where="In endpoint {}".format(endpoint.operation_id),
                    line=endpoint.line))
        for param in endpoint.parameters:
            if check_description(param.description):
                complaints.append(
                    Complaint(
                        message=check_description(param.description),
                        what=param.description,
                        where="In endpoint {}, parameter {}".format(endpoint.operation_id, param.name),
                        line=param.line))
        for _, resp in enumerate(endpoint.responses.values()):
            if check_description(resp.description):
                complaints.append(
                    Complaint(
                        message=check_description(resp.description),
                        what=resp.description,
                        where="In endpoint {}, response {}".format(endpoint.operation_id, resp.code),
                        line=resp.line))

    return complaints


def _check_recursively_cases(typedef: swagger_to.intermediate.Typedef,
                             visited: MutableSet[swagger_to.intermediate.Typedef]) -> List[Complaint]:
    """
    Checks the typedef's adherence to the casing conventions.

    :param typedef: to be translated
    :param visited: already seen typedefs
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]
    if typedef in visited:
        return complaints

    visited.add(typedef)

    if isinstance(typedef, swagger_to.intermediate.Primitivedef):
        pass

    elif isinstance(typedef, swagger_to.intermediate.Arraydef):
        if typedef.identifier != "" and typedef.identifier != swagger_to.capital_camel_case(typedef.identifier):
            complaints.append(
                Complaint(
                    message="Not a capital camel case identifier (e.g. CamelCase)",
                    what=typedef.identifier,
                    where="In array {}".format(typedef.identifier),
                    line=typedef.line))
        complaints.extend(_check_recursively_cases(typedef=typedef.items, visited=visited))

    elif isinstance(typedef, swagger_to.intermediate.Mapdef):
        if typedef.identifier != "" and typedef.identifier != swagger_to.capital_camel_case(typedef.identifier):
            complaints.append(
                Complaint(
                    message="Not a capital camel case identifier (e.g. CamelCase)",
                    what=typedef.identifier,
                    where="In map {}".format(typedef.identifier),
                    line=typedef.line))
        complaints.extend(_check_recursively_cases(typedef=typedef.values, visited=visited))

    elif isinstance(typedef, swagger_to.intermediate.Objectdef):

        if typedef.identifier != "" and typedef.identifier != swagger_to.capital_camel_case(typedef.identifier):
            complaints.append(
                Complaint(
                    message="Not a capital camel case identifier (e.g. CamelCase)",
                    what=typedef.identifier,
                    where="In object {}".format(typedef.identifier),
                    line=typedef.line))

        for prop in typedef.properties.values():
            if prop.name != swagger_to.snake_case(prop.name):
                complaints.append(
                    Complaint(
                        message="Not a snake case identifier (e.g. snake_case)",
                        what=prop.name,
                        where="In object {}, property {}".format(typedef.identifier, prop.name),
                        line=typedef.line))
            complaints.extend(_check_recursively_cases(typedef=prop.typedef, visited=visited))

    return complaints


def _check_recursively_descriptions(typedef: swagger_to.intermediate.Typedef,
                                    visited: MutableSet[swagger_to.intermediate.Typedef]) -> List[Complaint]:
    """
    Checks the typedef's adherence to the description conventions.

    :param typedef: to be translated
    :param visited: already seen typedefs
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]
    if typedef in visited:
        return complaints

    visited.add(typedef)

    if isinstance(typedef, swagger_to.intermediate.Primitivedef):
        pass

    elif isinstance(typedef, swagger_to.intermediate.Arraydef):
        if check_description(typedef.description):
            complaints.append(
                Complaint(
                    message=check_description(typedef.description),
                    what=typedef.description,
                    where="In array {}".format(typedef.identifier),
                    line=typedef.line))
        complaints.extend(_check_recursively_descriptions(typedef=typedef.items, visited=visited))

    elif isinstance(typedef, swagger_to.intermediate.Mapdef):
        if check_description(typedef.description):
            complaints.append(
                Complaint(
                    what=typedef.description,
                    message=check_description(typedef.description),
                    where="In map {}".format(typedef.identifier),
                    line=typedef.line))
        complaints.extend(_check_recursively_descriptions(typedef=typedef.values, visited=visited))

    elif isinstance(typedef, swagger_to.intermediate.Objectdef):
        if check_description(typedef.description):
            complaints.append(
                Complaint(
                    what=typedef.description,
                    message=check_description(typedef.description),
                    where="In object {}".format(typedef.identifier),
                    line=typedef.line))

        for prop in typedef.properties.values():
            if check_description(prop.description):
                complaints.append(
                    Complaint(
                        what=prop.description,
                        message=check_description(prop.description),
                        where="In object {}, property {}".format(typedef.identifier, prop.name),
                        line=typedef.line))
                complaints.extend(_check_recursively_descriptions(typedef=prop.typedef, visited=visited))

    return complaints


def check_endpoint_responses(endpoints: List[swagger_to.intermediate.Endpoint]) -> List[Complaint]:
    """
    Checks whether the endpoints conform to the conventions for responses.

    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]

    for endpoint in endpoints:
        if "200" not in endpoint.responses.keys():
            complaints.append(
                Complaint(
                    message="Path doesn't include response 200",
                    what=endpoint.path,
                    where="In endpoint {}".format(endpoint.operation_id),
                    line=endpoint.line))
        if "default" not in endpoint.responses.keys():
            complaints.append(
                Complaint(
                    message="Path doesn't include default response",
                    what=endpoint.path,
                    where="In endpoint {}".format(endpoint.operation_id),
                    line=endpoint.line))

    return complaints


def check_endpoint_path(endpoints: List[swagger_to.intermediate.Endpoint]) -> List[Complaint]:
    """
    Checks whether the endpoints conform to the conventions for paths.

    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]

    for endpoint in endpoints:
        if not endpoint.path.startswith("/"):
            complaints.append(
                Complaint(
                    message="Path doesn't begin with a slash",
                    what=endpoint.path,
                    where="In endpoint {}".format(endpoint.operation_id),
                    line=endpoint.line))

    return complaints


def check_description(description: str) -> Optional[str]:
    """
    Checks whether a description is well-styled.
    :param description: the description
    :return: the failed check, if any
    """
    # pylint: disable=too-many-return-statements, too-many-branches
    if description == "":
        return None

    without_pipe = description.replace("|", "")

    if not without_pipe[:1].isalpha():
        return "description should start with alphanumeric character"

    if without_pipe[:1].isupper():
        return "description should start with lower case character"

    words = without_pipe.split(' ')

    if not words[0].endswith('s'):
        return "description should start with verb in present tense (stem + \"-s\")"

    lines = without_pipe.splitlines()

    if not lines[0].endswith('.'):
        return "description's first line should end with a period"

    one_empty_line = False
    for i, line in enumerate(lines):
        if line.strip() != line:
            return "no line in the description should contain leading or trailing white space"

        if i == 1 and line.strip() != "":
            return "description's second line should be empty"

        if line == "":
            if one_empty_line:
                return "description should not contain two empty lines"
            else:
                one_empty_line = True
        else:
            one_empty_line = False

    if without_pipe.strip() != without_pipe:
        return "description should not contain leading or trailing whitespaces"

    return None


def perform(swagger: swagger_to.swagger.Swagger, typedefs: MutableMapping[str, swagger_to.intermediate.Typedef],
            endpoints: List[swagger_to.intermediate.Endpoint]) -> List[Complaint]:
    """
    Checks whether the typedefs and endpoints conform to the swagger style guide.

    :param swagger: parsed swagger file
    :param typedefs: swagger type definitions
    :param endpoints: swagger endpoint definitions
    :return: the list of failed checks
    """
    complaints = []  # type: List[Complaint]

    complaints.extend(check_header(swagger=swagger))

    complaints.extend(check_casing_typedefs(typedefs=typedefs))

    complaints.extend(check_casing_endpoints(endpoints=endpoints))

    complaints.extend(check_descriptions_typedefs(typedefs=typedefs))

    complaints.extend(check_descriptions_endpoints(endpoints=endpoints))

    complaints.extend(check_endpoint_path(endpoints=endpoints))

    complaints.extend(check_endpoint_responses(endpoints=endpoints))

    complaints.sort(key=lambda complaint: complaint.where)
    return complaints
