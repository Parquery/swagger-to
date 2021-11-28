#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for test_server."""

# pylint: skip-file
# pydocstyle: add-ignore=D105,D107,D401

import contextlib
import json
from typing import Any, BinaryIO, Dict, List, MutableMapping, Optional, cast

import requests
import requests.auth

from http.client import HTTPResponse

import urllib3


class _WrappedResponse(urllib3.HTTPResponse):
    """
    Wrap `requests.Response` so that it fits the `BinaryIO` interface.

    If we directly used `requests.Response`, the user would need to use `requests.Response.raw`,
    but explicitly close `requests.Response`.
    This is confusing and error-prone, so we wrap it all together into a `BinaryIO` interface.

    Additionally, `requests` have no official type annotation making it hard
    for client code to be statically type-checked.
    """

    # noinspection PyMissingConstructor
    def __init__(self, response: requests.Response):
        self._response = response

    def __getattr__(self, item):
        return getattr(self._response.raw, item)

    def close(self):
        self._response.close()


def _wrap_response(resp: requests.Response) -> HTTPResponse:
    """
    Wrap HTTPResponse object.
    """

    # urllib3.HTTPResponse has compatible interface of standard http lib.
    # (see docs for urllib3.HTTPResponse)
    return cast(HTTPResponse, _WrappedResponse(resp))


class RemoteCaller:
    """Executes the remote calls to the server."""

    def __init__(
        self,
        url_prefix: str,
        auth: Optional[requests.auth.AuthBase] = None,
        session: Optional[requests.Session] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth
        self.session = session

        if not self.session:
            self.session = requests.Session()
            self.session.auth = self.auth

    def open_file(
            self,
            path: str) -> BinaryIO:
        """
        Serves a static file that matches the path.

        :param path: is the path to the file relative to the root.

        :return: serves the file content.
        """
        url = "".join([
            self.url_prefix,
            '/',
            str(path)])

        resp = self.session.request(
            method='get',
            url=url,
            stream=True,
        )

        resp.raise_for_status()
        return _wrap_response(resp)


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
