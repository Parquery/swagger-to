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

    def test_me(self) -> bytes:
        """
        Is a test endpoint.

        :return: a confirmation
        """
        url = self.url_prefix + '/test-me'

        resp = requests.request(method='get', url=url, auth=self.auth)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content

    def post_test_another_one(
            self,
            id: str) -> bytes:
        """
        Is another test endpoint.

        :param id:

        :return: a confirmation
        """
        url = "".join([
            self.url_prefix,
            '/test-another-one/',
            str(id)])

        resp = requests.request(
            method='post',
            url=url,
            auth=self.auth,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content

    def delete_test_another_one(
            self,
            id: str) -> bytes:
        """
        Is yet another test endpoint.

        :param id:

        :return: a confirmation
        """
        url = "".join([
            self.url_prefix,
            '/test-another-one/',
            str(id)])

        resp = requests.request(
            method='delete',
            url=url,
            auth=self.auth,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
