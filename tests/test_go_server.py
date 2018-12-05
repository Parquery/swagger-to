#!/usr/bin/env python3
"""
Tests the Go server code generation.
"""
import os
import pathlib
import subprocess
import tempfile
import unittest

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
        script_dir = pathlib.Path(os.path.realpath(__file__)).parent
        swagger_path = script_dir / "swagger.yaml"

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

        got = swagger_to.go_server.generate_types_go(package=package, typedefs=go_typedefs)
        expected = (script_dir / "expected" / "go" / "types.go").read_text()
        self.assertEqual(expected, got)

        got = swagger_to.go_server.generate_routes_go(package=package, routes=go_routes)
        expected = (script_dir / "expected" / "go" / "routes.go").read_text()
        self.assertEqual(expected, got)

        got = swagger_to.go_server.generate_handler_impl_go(package=package, routes=go_routes)
        expected = (script_dir / "expected" / "go" / "handler_impl.go.sample").read_text()
        self.assertEqual(expected, got)

        got = swagger_to.go_server.generate_handler_go(package=package, routes=go_routes)
        expected = (script_dir / "expected" / "go" / "handler.go").read_text()
        self.assertEqual(expected, got)

        got = swagger_to.go_server.generate_json_schemas_go(package=package, routes=go_routes, typedefs=go_typedefs)
        expected = (script_dir / "expected" / "go" / "jsonschemas.go").read_text()
        self.assertEqual(expected, got)


if __name__ == '__main__':
    unittest.main()
