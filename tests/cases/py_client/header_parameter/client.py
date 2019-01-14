#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for test."""

# pylint: skip-file
# pydocstyle: add-ignore=D105,D107,D401

import contextlib
from typing import Any, BinaryIO, Dict, List, MutableMapping, Optional

import requests
import requests.auth


class RemoteCaller:
    """Executes the remote calls to the server."""

    def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth

    def test_me(
            self,
            some_parameter: str,
            x_some_custom_parameter: int,
            some_optional: Optional[str] = None) -> bytes:
        """
        Is a test endpoint.

        :param some_parameter:
        :param x_some_custom_parameter:
        :param some_optional:

        :return: a confirmation
        """
        url = self.url_prefix + '/products'

        headers = {
            'Some-parameter': some_parameter,
            'Some-optional': some_optional,
            'X-Some-Custom-Parameter': x_some_custom_parameter}

        resp = requests.request(
            method='get',
            url=url,
            headers=headers,
            auth=self.auth)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
