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

    def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth

    def test_me(
            self,
            query_some_parameter: str,
            path_some_parameter: str) -> bytes:
        """
        Is a test endpoint.

        :param query_some_parameter:
        :param path_some_parameter:

        :return: a confirmation
        """
        url = "".join([
            self.url_prefix,
            '/products/',
            str(path_some_parameter)])

        params = {}  # type: Dict[str, str]

        params['some_parameter'] = query_some_parameter

        resp = requests.request(
            method='get',
            url=url,
            params=params,
            auth=self.auth,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
