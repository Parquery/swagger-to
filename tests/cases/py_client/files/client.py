#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for test_server."""

# pylint: skip-file
# pydocstyle: add-ignore=D105,D107,D401

import contextlib
import json
from typing import Any, BinaryIO, Dict, List, MutableMapping, Optional

import requests
import requests.auth


class RemoteCaller:
    """Executes the remote calls to the server."""

    def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth

    def upload(
            self,
            file_nme: str,
            reference_image: BinaryIO) -> bytes:
        """
        Send a put request to /upload.

        :param file_nme: identifies the uploaded file.
        :param reference_image: contains a .tar archive containing the reference image(s) encoded in JPEG.

        :return: states that the session was correctly updated.
        """
        url = self.url_prefix + '/upload'

        data = {}  # type: Dict[str, str]
            
        data['file_nme'] = str(file_nme)

        files = {
            'reference_image': reference_image}

        resp = requests.request(
            method='put',
            url=url,
            data=data,
            files=files,
            auth=self.auth)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content

    def static(
            self,
            path: str) -> bytes:
        """
        Serves a static file that matches the path.

        :param path: is the path to the file relative to the root.

        :return: serves the file content.
        """
        url = "".join([
            self.url_prefix,
            '/',
            str(path)])

        resp = requests.request(
            method='get',
            url=url,
            auth=self.auth)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
