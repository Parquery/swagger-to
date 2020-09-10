#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for test."""

# pylint: skip-file
# pydocstyle: add-ignore=D105,D107,D401

import contextlib
import json
from typing import Any, BinaryIO, Dict, List, MutableMapping, Optional, cast

import requests
import requests.auth


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

    def test_me(
            self,
            some_parameter: str,
            some_optional: Optional[str] = None,
            same_named: Optional[str] = None) -> bytes:
        """
        Is a test endpoint.

        :param some_parameter:
        :param some_optional:
        :param same_named:

        :return: a confirmation
        """
        url = self.url_prefix + '/products'

        headers = {}  # type: Dict[str, str]

        headers['Some-parameter'] = some_parameter

        if some_optional is not None:
            headers['Some-optional'] = some_optional

        if same_named is not None:
            headers['same_named'] = same_named

        resp = self.session.request(
            method='get',
            url=url,
            headers=headers,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
