#!/usr/bin/env python3
"""Test the Py client code generation."""
import os
import pathlib
import unittest

import swagger_to.intermediate
import swagger_to.py_client
import swagger_to.swagger

# pylint: disable=missing-docstring
# pylint: disable=protected-access


class TestPyClient(unittest.TestCase):
    def test_that_it_works(self):
        # pylint: disable=too-many-locals
        tests_dir = pathlib.Path(os.path.realpath(__file__)).parent

        cases_dir = tests_dir / "cases" / "py_client"

        for case_dir in sorted(cases_dir.iterdir()):
            swagger_path = case_dir / "swagger.yaml"

            swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
            if errs:
                raise ValueError("Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))

            intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
            intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

            endpoints = swagger_to.intermediate.to_endpoints(
                swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

            py_typedefs = swagger_to.py_client.to_typedefs(intermediate_typedefs=intermediate_typedefs)

            if 'RemoteCaller' in py_typedefs:
                raise ValueError("A definition was specified in the swagger with the name 'RemoteCaller', "
                                 "but it's reserved for the Python client class.")

            py_requests = swagger_to.py_client.to_requests(endpoints=endpoints, typedefs=py_typedefs)

            got = swagger_to.py_client.generate_client_py(
                service_name=swagger.name, typedefs=py_typedefs, requests=py_requests)

            expected = (case_dir / "client.py").read_text()
            self.assertEqual(expected, got)


class TestDocstring(unittest.TestCase):
    def test_single_line(self):
        result = swagger_to.py_client._docstring(text=r'Do something.')
        self.assertEqual('"""Do something."""', result)

    def test_backslash_handled(self):
        result = swagger_to.py_client._docstring(text=r'Do \something.')
        self.assertEqual('r"""Do \\something."""', result)

    def test_triple_quote_handled(self):
        result = swagger_to.py_client._docstring(text='Do """something.')
        self.assertEqual('"""Do \\"\\"\\"something."""', result)

    def test_backslash_and_triple_quote(self):
        result = swagger_to.py_client._docstring(text='Do \\ really """something.')
        self.assertEqual('"""Do \\\\ really \\"\\"\\"something."""', result)

    def test_special_chars(self):
        result = swagger_to.py_client._docstring(text='Do \t really something.')
        self.assertEqual('"""Do \t really something."""', result)

    def test_multiline(self):
        result = swagger_to.py_client._docstring(text='Do\nreally\nsomething.')
        self.assertEqual('"""\nDo\nreally\nsomething.\n"""', result)


if __name__ == '__main__':
    unittest.main()
