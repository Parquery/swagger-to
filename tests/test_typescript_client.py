#!/usr/bin/env python3
"""
Tests the Typescript client code generation.
"""
import io
import os
import pathlib
# pylint: disable=missing-docstring
import unittest
from typing import TextIO, cast

import swagger_to.ts_angular5_client
import swagger_to.intermediate
import swagger_to.swagger


class TestTypescriptClient(unittest.TestCase):
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

        ts_typedefs = swagger_to.ts_angular5_client.to_typedefs(intermediate_typedefs=intermediate_typedefs)
        ts_requests = swagger_to.ts_angular5_client.to_requests(endpoints=endpoints, typedefs=ts_typedefs)

        buf = io.StringIO()
        buffid = cast(TextIO, buf)
        swagger_to.ts_angular5_client.write_client_ts(typedefs=ts_typedefs, requests=ts_requests, fid=buffid)

        got = buf.getvalue()

        expected = (script_dir / "expected" / "typescript" / "client.ts").read_text()
        self.assertEqual(expected, got)


if __name__ == '__main__':
    unittest.main()
