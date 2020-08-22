import contextlib
import unittest
from urllib.parse import urljoin

import requests_mock

from .client import RemoteCaller

url_prefix = "http://localhost"


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = RemoteCaller(url_prefix)

    def test_open_file(self):
        file_name = "target"

        content = b"""{"json_bytes": "value"}"""

        with requests_mock.Mocker() as m:
            # setup mock response
            m.get(urljoin(url_prefix, file_name), content=content)

            res = self.client.open_file(file_name)

            self.assertFalse(res.closed)

            with contextlib.closing(res):
                loaded = res.read()
                self.assertEqual(content, loaded)

            self.assertTrue(res.closed)


if __name__ == '__main__':
    unittest.main()
