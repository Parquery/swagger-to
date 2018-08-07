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


class TestElmPackage(unittest.TestCase):
    def test_that_it_works(self):
        script_dir = pathlib.Path(os.path.realpath(__file__)).parent

        buf = io.StringIO()
        buffid = cast(TextIO, buf)
        elm_package_json = swagger_to.elm_client.elm_package_json(query_strings=True)
        json.dump(elm_package_json, fp=buffid, indent=2, sort_keys=False)

        got = buf.getvalue()
        expected = (script_dir / "expected" / "elm" / "elm-package-with-querystring.json").read_text()
        self.assertEqual(expected, got)

        buf = io.StringIO()
        buffid = cast(TextIO, buf)
        elm_package_json = swagger_to.elm_client.elm_package_json(query_strings=False)
        json.dump(elm_package_json, fp=buffid, indent=2, sort_keys=False)

        got = buf.getvalue()
        expected = (script_dir / "expected" / "elm" / "elm-package-without-querystring.json").read_text()
        self.assertEqual(expected, got)


class TestNeedsQueryStrings(unittest.TestCase):
    def test_that_it_works(self):

        mock_query_param = swagger_to.elm_client.Parameter()
        mock_query_param.name = "a mock parameter"

        mock_request = swagger_to.elm_client.Request()
        mock_request.query_parameters = [mock_query_param]

        self.assertEqual(swagger_to.elm_client.needs_query_strings(requests=[mock_request]), True)

        mock_request.path_parameters = mock_request.query_parameters
        mock_request.query_parameters = []

        self.assertEqual(swagger_to.elm_client.needs_query_strings(requests=[mock_request]), False)


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
