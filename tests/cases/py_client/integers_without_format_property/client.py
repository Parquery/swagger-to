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

    if exp == MyType:
        return my_type_from_obj(obj, path=path)

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

    if exp == MyType:
        assert isinstance(obj, MyType)
        return my_type_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class MyType:
    def __init__(
            self,
            prop: Optional[int] = None) -> None:
        """Initializes with the given values."""
        self.prop = prop

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to my_type_to_jsonable.

        :return: JSON-able representation
        """
        return my_type_to_jsonable(self)


def new_my_type() -> MyType:
    """Generates an instance of MyType with default values."""
    return MyType()


def my_type_from_obj(obj: Any, path: str = "") -> MyType:
    """
    Generates an instance of MyType from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of MyType
    :param path: path to the object used for debugging
    :return: parsed instance of MyType
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))

    obj_prop = obj.get('prop', None)
    if obj_prop is not None:
        prop_from_obj = from_obj(
            obj_prop,
            expected=[int],
            path=path + '.prop')  # type: Optional[int]
    else:
        prop_from_obj = None

    return MyType(
        prop=prop_from_obj)


def my_type_to_jsonable(
        my_type: MyType,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of MyType.

    :param my_type: instance of MyType to be JSON-ized
    :param path: path to the my_type used for debugging
    :return: a JSON-able representation
    """
    res = dict()  # type: Dict[str, Any]

    if my_type.prop is not None:
        res['prop'] = my_type.prop

    return res


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

    def get_foo(self) -> bytes:
        """
        Send a get request to /.

        :return: Success
        """
        url = self.url_prefix + '/'

        resp = self.session.request(method='get', url=url)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
