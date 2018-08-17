#!/usr/bin/env python3
"""
Tests the Py client code generation.
"""
import io
import os
import pathlib
# pylint: disable=missing-docstring
import unittest
from typing import TextIO, cast

import swagger_to.py_client
import swagger_to.intermediate
import swagger_to.swagger


class TestPyClient(unittest.TestCase):
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

        py_typedefs = swagger_to.py_client.to_typedefs(intermediate_typedefs=intermediate_typedefs)

        if 'RemoteCaller' in py_typedefs:
            raise ValueError("A definition was specified in the swagger with the name 'RemoteCaller', "
                             "but it's reserved for the Python client class.")

        py_requests = swagger_to.py_client.to_requests(endpoints=endpoints, typedefs=py_typedefs)

        buf = io.StringIO()
        buffid = cast(TextIO, buf)
        swagger_to.py_client.write_client_py(
            service_name=swagger.name, typedefs=py_typedefs, requests=py_requests, fid=buffid)

        got = buf.getvalue()

        expected = (script_dir / "expected" / "py" / "client.py").read_text()
        self.assertEqual(expected, got)


if __name__ == '__main__':
    unittest.main()
