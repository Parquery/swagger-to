#!/usr/bin/env python3
"""
Tests the Elm client code generation.
"""
import io
import os
import pathlib
# pylint: disable=missing-docstring
import unittest
import json
from typing import TextIO, cast

import swagger_to.elm_client
import swagger_to.intermediate
import swagger_to.swagger


class TestElmClient(unittest.TestCase):
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

        elm_typedefs = swagger_to.elm_client.to_typedefs(intermediate_typedefs=intermediate_typedefs)
        elm_requests = swagger_to.elm_client.to_requests(endpoints=endpoints, typedefs=elm_typedefs)

        buf = io.StringIO()
        buffid = cast(TextIO, buf)
        swagger_to.elm_client.write_client_elm(typedefs=elm_typedefs, requests=elm_requests, fid=buffid)

        got = buf.getvalue()

        expected = (script_dir / "expected" / "elm" / "Client.elm").read_text()
        self.assertEqual(expected, got)

    def test_with_no_json(self):
        script_dir = pathlib.Path(os.path.realpath(__file__)).parent
        swagger_path = script_dir / "swagger-no-json.yaml"

        swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
        if errs:
            raise ValueError("Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))

        intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
        intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

        endpoints = swagger_to.intermediate.to_endpoints(
            swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

        elm_typedefs = swagger_to.elm_client.to_typedefs(intermediate_typedefs=intermediate_typedefs)
        elm_requests = swagger_to.elm_client.to_requests(endpoints=endpoints, typedefs=elm_typedefs)

        buf = io.StringIO()
        buffid = cast(TextIO, buf)
        swagger_to.elm_client.write_client_elm(typedefs=elm_typedefs, requests=elm_requests, fid=buffid)

        got = buf.getvalue()
        expected = (script_dir / "expected" / "elm" / "Client-no-json.elm").read_text()
        self.assertEqual(expected, got)


class TestElmPackage(unittest.TestCase):
    def test_that_it_works(self):
        script_dir = pathlib.Path(os.path.realpath(__file__)).parent

        buf = io.StringIO()
        buffid = cast(TextIO, buf)
        elm_package_json = swagger_to.elm_client.elm_package_json()
        json.dump(elm_package_json, fp=buffid, indent=2, sort_keys=False)

        got = buf.getvalue()
        expected = (script_dir / "expected" / "elm" / "elm-package.json").read_text()
        self.assertEqual(expected, got)


class TestEscapeElmString(unittest.TestCase):
    def test_that_it_works(self):
        expected = "some totally normal string"
        self.assertEqual(swagger_to.elm_client.escape_string(r"some totally normal string"), expected)

        expected = 'some totally \\t \\t \\"normal\\" string'
        self.assertEqual(swagger_to.elm_client.escape_string(r'some totally \t \t \"normal\" string'), expected)

        expected = "some totally\\n normal string\\t"
        self.assertEqual(swagger_to.elm_client.escape_string(r"some totally\n normal string\t"), expected)

        expected = "\\nsome\\r\\r totally normal string"
        self.assertEqual(swagger_to.elm_client.escape_string(r"\nsome\r\r totally normal string"), expected)

        expected = "\\\\\\\\\\\\some \\'totally normal\\' string"
        self.assertEqual(swagger_to.elm_client.escape_string(r"\\\\\\some \'totally normal\' string"), expected)


if __name__ == '__main__':
    unittest.main()
