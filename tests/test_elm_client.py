#!/usr/bin/env python3
"""Test the Elm client code generation."""
import io
import json
import os
import pathlib
import unittest
from typing import TextIO, cast

import swagger_to.elm_client
import swagger_to.intermediate
import swagger_to.swagger

# pylint: disable=missing-docstring,protected-access


class TestElmClient(unittest.TestCase):
    def __init__(self, methodName: str = 'runTest') -> None:
        self.maxDiff = None  # pylint: disable=invalid-name
        super().__init__(methodName=methodName)

    def test_that_it_works(self):
        # pylint: disable=too-many-locals
        tests_dir = pathlib.Path(os.path.realpath(__file__)).parent

        cases_dir = tests_dir / "cases" / "elm_client"

        for case_dir in sorted(cases_dir.iterdir()):
            swagger_path = case_dir / "swagger.yaml"

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
            expected = (case_dir / "Client.elm").read_text()
            self.assertEqual(expected, got)

            # Check elm-package.json
            buf = io.StringIO()
            buffid = cast(TextIO, buf)
            elm_package_json = swagger_to.elm_client.elm_package_json()
            json.dump(elm_package_json, fp=buffid, indent=2, sort_keys=False)

            got = buf.getvalue()
            expected = (case_dir / "elm-package.json").read_text()
            self.assertEqual(expected, got)


class TestEscapeElmString(unittest.TestCase):
    def test_that_it_works(self):
        expected = "some totally normal string"
        self.assertEqual(swagger_to.elm_client._escape_string(r"some totally normal string"), expected)

        expected = 'some totally \\t \\t \\"normal\\" string'
        self.assertEqual(swagger_to.elm_client._escape_string(r'some totally \t \t \"normal\" string'), expected)

        expected = "some totally\\n normal string\\t"
        self.assertEqual(swagger_to.elm_client._escape_string(r"some totally\n normal string\t"), expected)

        expected = "\\nsome\\r\\r totally normal string"
        self.assertEqual(swagger_to.elm_client._escape_string(r"\nsome\r\r totally normal string"), expected)

        expected = "\\\\\\\\\\\\some \\'totally normal\\' string"
        self.assertEqual(swagger_to.elm_client._escape_string(r"\\\\\\some \'totally normal\' string"), expected)


if __name__ == '__main__':
    unittest.main()
