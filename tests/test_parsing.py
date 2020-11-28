#!/usr/bin/env python3
"""Test that parsing does not break on certain edge cases."""
import os
import pathlib
import unittest

import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.swagger

# pylint: disable=missing-docstring
# pylint: disable=protected-access


class TestParsing(unittest.TestCase):
    def test_that_it_does_not_break(self):
        tests_dir = pathlib.Path(os.path.realpath(__file__)).parent

        cases_dir = tests_dir / "cases" / "parsing"

        for case_dir in sorted(cases_dir.iterdir()):
            swagger_path = case_dir / "swagger.yaml"

            _, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)

            expected_errs_pth = case_dir / "errors.txt"
            expected_errs = expected_errs_pth.read_text()

            self.assertEqual(expected_errs, "\n".join(errs),
                             "Mismatch against the expected errors from {}".format(expected_errs_pth))


if __name__ == '__main__':
    unittest.main()
