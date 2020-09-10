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


def from_obj(obj: Any, expected: List[type], path: str = '') -> Any:
    """
    Checks and converts the given obj along the expected types.

    :param obj: to be converted
    :param expected: list of types representing the (nested) structure
    :param path: to the object used for debugging
    :return: the converted object
    """
    if not expected:
        raise ValueError("`expected` is empty, but at least one type needs to be specified.")

    exp = expected[0]

    if exp == float:
        if isinstance(obj, int):
            return float(obj)

        if isinstance(obj, float):
            return obj

        raise ValueError(
            'Expected object of type int or float at {!r}, but got {}.'.format(path, type(obj)))

    if exp in [bool, int, str, list, dict]:
        if not isinstance(obj, exp):
            raise ValueError(
                'Expected object of type {} at {!r}, but got {}.'.format(exp, path, type(obj)))

    if exp in [bool, int, float, str]:
        return obj

    if exp == list:
        lst = []  # type: List[Any]
        for i, value in enumerate(obj):
            lst.append(
                from_obj(value, expected=expected[1:], path='{}[{}]'.format(path, i)))

        return lst

    if exp == dict:
        adict = dict()  # type: Dict[str, Any]
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError(
                    'Expected a key of type str at path {!r}, got: {}'.format(path, type(key)))

            adict[key] = from_obj(value, expected=expected[1:], path='{}[{!r}]'.format(path, key))

        return adict

    if exp == EmptyObject:
        return empty_object_from_obj(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


def to_jsonable(obj: Any, expected: List[type], path: str = "") -> Any:
    """
    Checks and converts the given object along the expected types to a JSON-able representation.

    :param obj: to be converted
    :param expected: list of types representing the (nested) structure
    :param path: path to the object used for debugging
    :return: JSON-able representation of the object
    """
    if not expected:
        raise ValueError("`expected` is empty, but at least one type needs to be specified.")

    exp = expected[0]
    if not isinstance(obj, exp):
        raise ValueError('Expected object of type {} at path {!r}, but got {}.'.format(
            exp, path, type(obj)))

    # Assert on primitive types to help type-hinting.
    if exp == bool:
        assert isinstance(obj, bool)
        return obj

    if exp == int:
        assert isinstance(obj, int)
        return obj

    if exp == float:
        assert isinstance(obj, float)
        return obj

    if exp == str:
        assert isinstance(obj, str)
        return obj

    if exp == list:
        assert isinstance(obj, list)

        lst = []  # type: List[Any]
        for i, value in enumerate(obj):
            lst.append(
                to_jsonable(value, expected=expected[1:], path='{}[{}]'.format(path, i)))

        return lst

    if exp == dict:
        assert isinstance(obj, dict)

        adict = dict()  # type: Dict[str, Any]
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError(
                    'Expected a key of type str at path {!r}, got: {}'.format(path, type(key)))

            adict[key] = to_jsonable(
                value,
                expected=expected[1:],
                path='{}[{!r}]'.format(path, key))

        return adict

    if exp == EmptyObject:
        assert isinstance(obj, EmptyObject)
        return empty_object_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class EmptyObject:
    """Is an empty object without properties."""

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to empty_object_to_jsonable.

        :return: a JSON-able representation
        """
        return empty_object_to_jsonable(self)


def new_empty_object() -> EmptyObject:
    """Generates an instance of EmptyObject with default values."""
    return EmptyObject()


def empty_object_from_obj(obj: Any, path: str = "") -> EmptyObject:
    """
    Generates an instance of EmptyObject from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of EmptyObject
    :param path: path to the object used for debugging
    :return: parsed instance of EmptyObject
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    return EmptyObject()


def empty_object_to_jsonable(
        empty_object: EmptyObject,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of EmptyObject.

    :param empty_object: instance of EmptyObject to be JSON-ized
    :param path: path to the empty_object used for debugging
    :return: a JSON-able representation
    """
    return dict()


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
            empty_object: Optional[EmptyObject] = None) -> EmptyObject:
        """
        Is a test endpoint.

        :param empty_object:

        :return: an empty object
        """
        url = self.url_prefix + '/products'

        data = None  # type: Optional[Any]
        if empty_object != None:
            data = to_jsonable(
                empty_object,
                expected=[EmptyObject])

        resp = self.session.request(
            method='get',
            url=url,
            json=data,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[EmptyObject])


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
