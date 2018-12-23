#!/usr/bin/env python3
"""Test the Go server code generation."""
import os
import pathlib
import subprocess
import tempfile
import unittest

import collections

import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.swagger

# pylint: disable=missing-docstring
# pylint: disable=protected-access


class TestEscapeStr(unittest.TestCase):
    def test_empty(self):
        self.assertEqual('""', swagger_to.go_server._escaped_str(''))

    def test_that_it_works(self):
        self.assertEqual('"some \\\\ \\" \\a \\f \\t \\n \\r \\v text"',
                         swagger_to.go_server._escaped_str('some \\ " \a \f \t \n \r \v text'))


def meld(expected: str, got: str) -> None:
    """Calls meld to diff the two strings."""
    with tempfile.NamedTemporaryFile() as tmp1, \
            tempfile.NamedTemporaryFile() as tmp2:
        tmp1.file.write(expected.encode())  # type: ignore
        tmp1.file.flush()  # type: ignore

        tmp2.file.write(got.encode())  # type: ignore
        tmp2.file.flush()  # type: ignore

        subprocess.check_call(['meld', tmp1.name, tmp2.name])


class TestGoServer(unittest.TestCase):
    def test_that_it_works(self):
        # pylint: disable=too-many-locals
        tests_dir = pathlib.Path(os.path.realpath(__file__)).parent

        cases_dir = tests_dir / "cases" / "go_server"

        for case_dir in sorted(cases_dir.iterdir()):
            swagger_path = case_dir / "swagger.yaml"

            swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
            if errs:
                raise ValueError("Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))

            intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
            intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

            endpoints = swagger_to.intermediate.to_endpoints(
                swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

            go_typedefs = swagger_to.go_server.to_typedefs(intermediate_typedefs=intermediate_typedefs)
            go_routes = swagger_to.go_server.to_routes(endpoints=endpoints, typedefs=go_typedefs)

            package = swagger.name

            got = collections.OrderedDict([("types.go",
                                            swagger_to.go_server.generate_types_go(
                                                package=package,
                                                typedefs=go_typedefs)), ("routes.go",
                                                                         swagger_to.go_server.generate_routes_go(
                                                                             package=package, routes=go_routes)),
                                           ("handler_impl.go.sample",
                                            swagger_to.go_server.generate_handler_impl_go(
                                                package=package,
                                                routes=go_routes)), ("handler.go",
                                                                     swagger_to.go_server.generate_handler_go(
                                                                         package=package, routes=go_routes)),
                                           ("jsonschemas.go",
                                            swagger_to.go_server.generate_json_schemas_go(
                                                package=package, routes=go_routes, typedefs=go_typedefs))])

            for filename, text in got.items():
                expected_pth = case_dir / filename

                expected = expected_pth.read_text()
                self.assertEqual(expected, text,
                                 "A mismatch between the generated file and the expected file: {}".format(expected_pth))


if __name__ == '__main__':
    unittest.main()
