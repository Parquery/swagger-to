#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for test."""

# pylint: skip-file
# pydocstyle: add-ignore=D105,D107,D401

import contextlib
import json
from typing import Any, BinaryIO, Dict, List, MutableMapping, Optional

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

    if exp == TestObject:
        return test_object_from_obj(obj, path=path)

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

    if exp == TestObject:
        assert isinstance(obj, TestObject)
        return test_object_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class TestObject:
    """Is a test object."""

    def __init__(
            self,
            timestamp: str) -> None:
        """Initializes with the given values."""
        # is a test string property.
        self.timestamp = timestamp

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to test_object_to_jsonable.

        :return: JSON-able representation
        """
        return test_object_to_jsonable(self)


def new_test_object() -> TestObject:
    """Generates an instance of TestObject with default values."""
    return TestObject(
        timestamp='')


def test_object_from_obj(obj: Any, path: str = "") -> TestObject:
    """
    Generates an instance of TestObject from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of TestObject
    :param path: path to the object used for debugging
    :return: parsed instance of TestObject
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))

    timestamp_from_obj = from_obj(
        obj['timestamp'],
        expected=[str],
        path=path + '.timestamp')  # type: str

    return TestObject(
        timestamp=timestamp_from_obj)


def test_object_to_jsonable(
        test_object: TestObject,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of TestObject.

    :param test_object: instance of TestObject to be JSON-ized
    :param path: path to the test_object used for debugging
    :return: a JSON-able representation
    """
    res = dict()  # type: Dict[str, Any]

    res['timestamp'] = test_object.timestamp

    return res


class RemoteCaller:
    """Executes the remote calls to the server."""

    def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth

    def test_me(
            self,
            test_object: Optional[TestObject] = None) -> TestObject:
        """
        Is a test endpoint.

        :param test_object:

        :return: a test object
        """
        url = self.url_prefix + '/products'

        data = to_jsonable(
            test_object,
            expected=[TestObject])

        resp = requests.request(
            method='get',
            url=url,
            json=data,
            auth=self.auth)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[TestObject])


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
