#!/usr/bin/env python3

# pylint: disable=missing-docstring
import unittest

import swagger_to
import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.swagger


class TestSwaggerToGo(unittest.TestCase):
    def test_camel_case_split(self):
        table = [('CvSizeInt', ['Cv', 'Size', 'Int']), ('SomeURLs', ['Some', 'URLs'])]

        for an_input, expected in table:
            got = swagger_to.camel_case_split(identifier=an_input)
            self.assertListEqual(expected, got)

    def test_capial_camel_case(self):
        table = [
            ('CvSizeInt', 'CvSizeInt'),
            ('some_urls', 'SomeURLs'),
            ('someURLs', 'SomeURLs'),
            ('some_ids', 'SomeIDs'),
            ('someIDs', 'SomeIDs'),
        ]

        for an_input, expected in table:
            got = swagger_to.capital_camel_case(identifier=an_input)
            self.assertEqual(expected, got)

    def test_camel_case(self):
        table = [
            ('CvSizeInt', 'cvSizeInt'),
            ('URLsToFind', 'urlsToFind'),
            ('IDsToFind', 'idsToFind'),
            ('some_ids', 'someIDs'),
            ('someIDs', 'someIDs'),
        ]

        for an_input, expected in table:
            got = swagger_to.camel_case(identifier=an_input)
            self.assertEqual(expected, got)

    def test_snake_case(self):
        table = [
            ('CvSizeInt', 'cv_size_int'),
            ('URLsToFind', 'urls_to_find'),
            ('IDsToFind', 'ids_to_find'),
            ('some_ids', 'some_ids'),
            ('someIDs', 'some_ids'),
        ]

        for an_input, expected in table:
            got = swagger_to.snake_case(identifier=an_input)
            self.assertEqual(expected, got)

    def test_path_tokenization(self):
        pth = "/{hello}/from-me/hello/{hello}/{wicked / one}/some more?q=1#a{unclosed&}"

        token_pth = swagger_to.tokenize_path(path=pth)

        self.assertEqual("".join(token_pth.tokens), pth)
        self.assertListEqual(token_pth.parameter_to_token_indices["hello"], [1, 3])


if __name__ == '__main__':
    unittest.main()
