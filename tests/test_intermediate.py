#!/usr/bin/env python3
"""Test that parsing into intermediate representation does not break on certain edge cases."""

# pylint: disable=missing-docstring
# pylint: disable=protected-access

import collections
import json
import os
import pathlib
import unittest
from typing import Any, MutableMapping

import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.swagger


def jsonize_with_references(what: Any) -> Any:
    """
    Convert a part of the intermediate representation to a JSON-able structure.

    This is almost certainly not the same representation as the original type definition in the Swagger spec.

    The identifiable typedefs (*i.e.*, the typedefs with an identifier) will be jsonized as human-readable string
    references to avoid endless loops through cycles.
    """
    if isinstance(what, (swagger_to.intermediate.JsonSchema, swagger_to.intermediate.Typedef,
                         swagger_to.intermediate.Response, swagger_to.intermediate.Endpoint)):
        if (isinstance(what, swagger_to.intermediate.Typedef) and what.identifier != ''):
            return 'reference to a typedef with identifier {}'.format(what.identifier)

        jsonable = collections.OrderedDict(
            (k, jsonize_with_references(what.__dict__[k])) for k in sorted(what.__dict__.keys()))  # type: Any

        return jsonable

    elif isinstance(
            what,
        (swagger_to.intermediate.Propertydef, swagger_to.intermediate.Parameter, swagger_to.intermediate.Response)):
        jsonable = collections.OrderedDict(
            (k, jsonize_with_references(what.__dict__[k])) for k in sorted(what.__dict__.keys()))

        return jsonable

    elif isinstance(what, collections.OrderedDict):
        jsonable = collections.OrderedDict((k, jsonize_with_references(v)) for k, v in what.items())
        return jsonable

    elif isinstance(what, list):
        jsonable = [jsonize_with_references(v) for v in what]
        return jsonable

    elif isinstance(what, (int, bool, str)):
        return what

    elif what is None:
        return None

    else:
        raise NotImplementedError("Unhandled ``what``: {!r}".format(what))


def jsonize_typedefs(typedefs: MutableMapping[str, swagger_to.intermediate.Typedef]) -> Any:
    """
    Convert the type definitions to a JSON-able structure.

    This is almost certainly not the same representation as the original type definition in the Swagger spec.

    The references to identifiable typedefs (*i.e.*, the typedefs with an identifier) will be jsonized as
    human-readable strings to avoid endless loops through cycles.
    """
    result = collections.OrderedDict()  # type: MutableMapping[str, Any]

    for name, typedef in typedefs.items():
        jsonable = collections.OrderedDict(
            (k, jsonize_with_references(typedef.__dict__[k])) for k in sorted(typedef.__dict__.keys()))  # type: Any

        result[name] = jsonable

    return result


class TestIntermediate(unittest.TestCase):
    def test_that_it_does_not_break(self):
        tests_dir = pathlib.Path(os.path.realpath(__file__)).parent

        cases_dir = tests_dir / "cases" / "intermediate"

        for swagger_path in sorted(cases_dir.glob("**/swagger.yaml")):
            case_dir = swagger_path.parent

            swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
            if errs:
                raise ValueError("Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))

            inter_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
            inter_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=inter_typedefs)

            endpoints = swagger_to.intermediate.to_endpoints(
                swagger=swagger, typedefs=inter_typedefs, params=inter_params)

            inter_typedefs_pth = case_dir / "intermediate_typedefs.json"
            inter_params_pth = case_dir / "intermediate_params.json"
            endpoints_pth = case_dir / "endpoints.json"

            expected_typedefs_as_json_str = json.dumps(jsonize_typedefs(inter_typedefs), indent=2)
            expected_params_as_json_str = json.dumps(jsonize_with_references(inter_params), indent=2)
            expected_endpoints_as_json_str = json.dumps(jsonize_with_references(endpoints), indent=2)

            # Leave this snippet here to facilitate updating the tests in the future
            # inter_typedefs_pth.write_text(expected_typedefs_as_json_str)
            # inter_params_pth.write_text(expected_params_as_json_str)
            # endpoints_pth.write_text(expected_endpoints_as_json_str)

            self.assertEqual(
                inter_typedefs_pth.read_text(), expected_typedefs_as_json_str,
                "Expected content from {} does not match the jsonized typedefs.".format(inter_typedefs_pth))

            self.assertEqual(inter_params_pth.read_text(), expected_params_as_json_str,
                             "Expected content from {} does not match the jsonized params.".format(inter_params_pth))

            self.assertEqual(endpoints_pth.read_text(), expected_endpoints_as_json_str,
                             "Expected content from {} does not match the jsonized endpoints.".format(endpoints_pth))


if __name__ == '__main__':
    unittest.main()
