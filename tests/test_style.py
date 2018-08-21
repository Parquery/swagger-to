#!/usr/bin/env python3
"""
Tests the Swagger style check.
"""
import os
import pathlib
# pylint: disable=missing-docstring
import unittest

import swagger_to.elm_client
import swagger_to.intermediate
import swagger_to.swagger
import swagger_to.style


class TestStyleCheck(unittest.TestCase):
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

        complaints = swagger_to.style.perform(swagger=swagger, typedefs=intermediate_typedefs, endpoints=endpoints)
        cmpl_strings = []
        for cmpl in complaints:
            cmpl_strings.append("{}: {}: \"{}\"".format(cmpl.where, cmpl.message, cmpl.what.replace('\n', ' ')))

        expected = (script_dir / "expected" / "style" / "errors.txt").read_text()
        self.assertEqual(expected, "\n".join(cmpl_strings))

    def test_with_line_numbers(self):
        script_dir = pathlib.Path(os.path.realpath(__file__)).parent
        swagger_path = script_dir / "swagger.yaml"
        swagger_path_rel = "tests/swagger.yaml"

        swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
        if errs:
            raise ValueError("Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))

        intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
        intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

        endpoints = swagger_to.intermediate.to_endpoints(
            swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

        complaints = swagger_to.style.perform(swagger=swagger, typedefs=intermediate_typedefs, endpoints=endpoints)
        complaints.sort(key=lambda complaint: complaint.line)

        cmpl_strings = []
        for cmpl in complaints:
            complaint_str = "{}:{} {} \"{}\"".format(swagger_path_rel, cmpl.line, cmpl.message,
                                                     cmpl.what.replace('\n', ' '))

            cmpl_strings.append(complaint_str)

        expected = (script_dir / "expected" / "style" / "errors_line_numbers.txt").read_text()
        self.assertEqual(expected, "\n".join(cmpl_strings))


class TestDescription(unittest.TestCase):
    def test_that_it_works(self):
        # Good: empty string
        self.assertEqual(swagger_to.style.check_description(""), None)
        # Good: lower case first letter and ends with period
        self.assertEqual(swagger_to.style.check_description("is a well-formatted description."), None)
        # Good: description and paragraph
        self.assertEqual(
            swagger_to.style.check_description("is a well-formatted description.\n\nit really is a "
                                               "well-formatted thing"), None)
        # Good: description and paragraphs
        self.assertEqual(
            swagger_to.style.check_description("is a well-formatted description.\n\nit really is a "
                                               "well-formatted thing\n\nit really is"), None)

        # Bad: everything else
        self.assertNotEqual(swagger_to.style.check_description("isnt a not-so-well-formatted description"), None)
        self.assertNotEqual(swagger_to.style.check_description("Has a not-so-well-formatted description."), None)
        self.assertNotEqual(swagger_to.style.check_description("has a not-so-well-formatted description"), None)
        self.assertNotEqual(swagger_to.style.check_description("123e1dt-so-well-formatted description."), None)
        self.assertNotEqual(swagger_to.style.check_description("    is not-so-well-formatted description."), None)
        self.assertNotEqual(swagger_to.style.check_description("\tis not-so-well-formatted description."), None)
        self.assertNotEqual(swagger_to.style.check_description("\nis not-so-well-formatted description."), None)
        self.assertNotEqual(
            swagger_to.style.check_description("is not-so-well-formatted description.\nnot at all."), None)


if __name__ == '__main__':
    unittest.main()
