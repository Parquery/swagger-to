#!/usr/bin/env python3
"""Test the Swagger style check."""
import os
import pathlib
import subprocess
import tempfile
import unittest
from typing import List  # pylint: disable=unused-import

import swagger_to.elm_client
import swagger_to.intermediate
import swagger_to.style
import swagger_to.swagger

# pylint: disable=missing-docstring,protected-access


def meld(expected: str, got: str) -> None:
    """Calls meld to diff the two strings."""
    with tempfile.NamedTemporaryFile() as tmp1, \
            tempfile.NamedTemporaryFile() as tmp2:
        tmp1.file.write(expected.encode())  # type: ignore
        tmp1.file.flush()  # type: ignore

        tmp2.file.write(got.encode())  # type: ignore
        tmp2.file.flush()  # type: ignore

        subprocess.check_call(['meld', tmp1.name, tmp2.name])


class TestStyleCheck(unittest.TestCase):
    def test_that_it_works(self):
        # pylint: disable=too-many-locals
        tests_dir = pathlib.Path(os.path.realpath(__file__)).parent

        cases_dir = tests_dir / "cases" / "style"

        for case_dir in sorted(cases_dir.iterdir()):
            swagger_path = case_dir / "swagger.yaml"

            swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
            if errs:
                raise ValueError("Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))

            intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
            intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

            endpoints = swagger_to.intermediate.to_endpoints(
                swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

            complaints = swagger_to.style.perform(swagger=swagger, typedefs=intermediate_typedefs, endpoints=endpoints)

            # Convert complaints so that they can be easily compared against a golden file
            cmpl_lines = []  # type: List[str]
            for cmpl in complaints:
                cmpl_lines.append("Line {:4d}: {}: {}: {!r}".format(cmpl.line, cmpl.where, cmpl.message,
                                                                    cmpl.what.replace('\n', ' ')))

            cmpl_lines.sort()

            got = "\n".join(cmpl_lines) + '\n'
            expected_pth = case_dir / "errors.txt"
            expected = expected_pth.read_text()
            self.assertEqual(expected, got, "Mismatch from the expected content in {}".format(expected_pth))


class TestDescription(unittest.TestCase):
    def test_that_it_works(self):
        # Good: empty string
        self.assertEqual(swagger_to.style._check_description(description="", starts_with_verb=True), None)
        # Good: lower case first letter and ends with period
        self.assertEqual(
            swagger_to.style._check_description(description="is a well-formatted description.", starts_with_verb=True),
            None)
        # Good: description and paragraph
        self.assertEqual(
            swagger_to.style._check_description(
                description="is a well-formatted description.\n\nit really is a "
                "well-formatted thing",
                starts_with_verb=True), None)
        # Good: description and paragraphs
        self.assertEqual(
            swagger_to.style._check_description(
                description="is a well-formatted description.\n\nit really is a "
                "well-formatted thing\n\nit really is",
                starts_with_verb=True), None)

        # Bad: everything else
        self.assertNotEqual(
            swagger_to.style._check_description(
                description="isnt a not-so-well-formatted description", starts_with_verb=True), None)
        self.assertNotEqual(
            swagger_to.style._check_description(
                description="Has a not-so-well-formatted description.", starts_with_verb=True), None)
        self.assertNotEqual(
            swagger_to.style._check_description(
                description="has a not-so-well-formatted description", starts_with_verb=True), None)
        self.assertNotEqual(
            swagger_to.style._check_description(
                description="123e1dt-so-well-formatted description.", starts_with_verb=True), None)
        self.assertNotEqual(
            swagger_to.style._check_description(
                description="    is not-so-well-formatted description.", starts_with_verb=True), None)
        self.assertNotEqual(
            swagger_to.style._check_description(
                description="\tis not-so-well-formatted description.", starts_with_verb=True), None)
        self.assertNotEqual(
            swagger_to.style._check_description(
                description="\nis not-so-well-formatted description.", starts_with_verb=True), None)
        self.assertNotEqual(
            swagger_to.style._check_description(
                description="is not-so-well-formatted description.\nnot at all.", starts_with_verb=True), None)


if __name__ == '__main__':
    unittest.main()
