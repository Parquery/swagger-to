#!/usr/bin/env python3
"""Test that parsing into intermediate representation does not break on certain edge cases."""

# pylint: disable=missing-docstring
# pylint: disable=protected-access

import collections
import json
import os
import pathlib
import unittest
from typing import Any

import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.swagger


def jsonize(what: Any) -> Any:
    """
    Convert a part of a type definition to a JSON-able structure.

    This is almost certainly not the same representation as the original type definition in the Swagger spec.
    """
    if isinstance(what, (swagger_to.intermediate.JsonSchema, swagger_to.intermediate.Typedef,
                         swagger_to.intermediate.Response, swagger_to.intermediate.Endpoint)):
        return collections.OrderedDict((k, jsonize(what.__dict__[k])) for k in sorted(what.__dict__.keys()))

    elif isinstance(
            what,
        (swagger_to.intermediate.Propertydef, swagger_to.intermediate.Parameter, swagger_to.intermediate.Response)):
        jsonable = collections.OrderedDict((k, jsonize(what.__dict__[k])) for k in sorted(what.__dict__.keys()))

        # We reference typedefs by identifier to make the output a bit more succinct.
        # In case of properties, this is even mandatory in order to avoid cycles.
        if what.typedef is not None and what.typedef.identifier != '':
            jsonable['typedef'] = 'reference to a typedef with identifier {}'.format(what.typedef.identifier)

        return jsonable

    elif isinstance(what, collections.OrderedDict):
        return collections.OrderedDict((k, jsonize(v)) for k, v in what.items())

    elif isinstance(what, list):
        return [jsonize(v) for v in what]

    elif isinstance(what, (int, bool, str)):
        return what

    elif what is None:
        return None

    else:
        raise NotImplementedError("Unhandled ``what``: {!r}".format(what))


class TestIntermediate(unittest.TestCase):
    def test_that_it_does_not_break(self):
        tests_dir = pathlib.Path(os.path.realpath(__file__)).parent

        cases_dir = tests_dir / "cases" / "intermediate"

        for case_dir in sorted(cases_dir.iterdir()):
            swagger_path = case_dir / "swagger.yaml"

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

            # Leave this snippet here to facilitate updating the tests in the future
            # inter_typedefs_pth.write_text(json.dumps(jsonize(inter_typedefs), indent=2))
            # inter_params_pth.write_text(json.dumps(jsonize(inter_params), indent=2))
            # endpoints_pth.write_text(json.dumps(jsonize(endpoints), indent=2))

            self.assertEqual(
                inter_typedefs_pth.read_text(), json.dumps(jsonize(inter_typedefs), indent=2),
                "Expected content from {} does not match the jsonized typedefs.".format(inter_typedefs_pth))

            self.assertEqual(inter_params_pth.read_text(), json.dumps(jsonize(inter_params), indent=2),
                             "Expected content from {} does not match the jsonized params.".format(inter_params_pth))

            self.assertEqual(endpoints_pth.read_text(), json.dumps(jsonize(endpoints), indent=2),
                             "Expected content from {} does not match the jsonized endpoints.".format(endpoints_pth))


if __name__ == '__main__':
    unittest.main()
