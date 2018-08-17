#!/usr/bin/env python3
"""
Tests the Go server code generation.
"""
import io
import os
import pathlib
# pylint: disable=missing-docstring
import unittest
from typing import TextIO, cast

import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.swagger


class TestGoServer(unittest.TestCase):
    def test_that_it_works(self):
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

        with io.StringIO() as buf:
            buffid = cast(TextIO, buf)
            swagger_to.go_server.write_types_go(package=package, typedefs=go_typedefs, fid=buffid)

            got = buf.getvalue()

            expected = (script_dir / "expected" / "go" / "types.go").read_text()
            self.assertEqual(expected, got)

        with io.StringIO() as buf:
            buffid = cast(TextIO, buf)
            swagger_to.go_server.write_routes_go(package=package, routes=go_routes, fid=buffid)

            got = buf.getvalue()

            expected = (script_dir / "expected" / "go" / "routes.go").read_text()
            self.assertEqual(expected, got)

        with io.StringIO() as buf:
            buffid = cast(TextIO, buf)
            swagger_to.go_server.write_handler_go(package=package, routes=go_routes, fid=buffid)

            got = buf.getvalue()

            expected = (script_dir / "expected" / "go" / "handler.go").read_text()
            self.assertEqual(expected, got)

        with io.StringIO() as buf:
            buffid = cast(TextIO, buf)
            swagger_to.go_server.write_handler_impl_go(package=package, routes=go_routes, fid=buffid)

            got = buf.getvalue()

            expected = (script_dir / "expected" / "go" / "handler_impl.go.sample").read_text()
            self.assertEqual(expected, got)

        with io.StringIO() as buf:
            buffid = cast(TextIO, buf)
            swagger_to.go_server.write_json_schemas_go(package=package, routes=go_routes, typedefs=go_typedefs, fid=buffid)

            got = buf.getvalue()

            expected = (script_dir / "expected" / "go" / "jsonschemas.go").read_text()
            self.assertEqual(expected, got)


if __name__ == '__main__':
    unittest.main()
