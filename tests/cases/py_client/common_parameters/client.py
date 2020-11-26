#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for foo."""

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

    def get_foo(
            self,
            foo_id: str) -> bytes:
        """
        Send a get request to /api/v1/foo/{foo_id}.

        :param foo_id: The foo id

        :return: Success
        """
        url = "".join([
            self.url_prefix,
            '/api/v1/foo/',
            str(foo_id)])

        resp = self.session.request(
            method='get',
            url=url,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
