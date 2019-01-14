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

    if exp == Profile:
        return profile_from_obj(obj, path=path)

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

    if exp == Profile:
        assert isinstance(obj, Profile)
        return profile_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class Profile:
    def __init__(
            self,
            last_name: str,
            first_name: Optional[str] = None) -> None:
        """Initializes with the given values."""
        # Last name of the user.
        self.last_name = last_name

        # First name of the user.
        self.first_name = first_name

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to profile_to_jsonable.

        :return: JSON-able representation
        """
        return profile_to_jsonable(self)


def new_profile() -> Profile:
    """Generates an instance of Profile with default values."""
    return Profile(
        last_name='')


def profile_from_obj(obj: Any, path: str = "") -> Profile:
    """
    Generates an instance of Profile from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of Profile
    :param path: path to the object used for debugging
    :return: parsed instance of Profile
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))

    last_name_from_obj = from_obj(
        obj['last_name'],
        expected=[str],
        path=path + '.last_name')  # type: str

    if 'first_name' in obj:
        first_name_from_obj = from_obj(
            obj['first_name'],
            expected=[str],
            path=path + '.first_name')  # type: Optional[str]
    else:
        first_name_from_obj = None

    return Profile(
        last_name=last_name_from_obj,
        first_name=first_name_from_obj)


def profile_to_jsonable(
        profile: Profile,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of Profile.

    :param profile: instance of Profile to be JSON-ized
    :param path: path to the profile used for debugging
    :return: a JSON-able representation
    """
    res = dict()  # type: Dict[str, Any]

    res['last_name'] = profile.last_name

    if profile.first_name is not None:
        res['first_name'] = profile.first_name

    return res


class RemoteCaller:
    """Executes the remote calls to the server."""

    def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth

    def test_me(
            self,
            some_str_parameter: str,
            some_complex_parameter: Optional[Profile] = None,
            some_int_parameter: Optional[int] = None) -> bytes:
        """
        Is a test endpoint.

        :param some_str_parameter:
        :param some_complex_parameter:
        :param some_int_parameter:

        :return: a confirmation
        """
        url = self.url_prefix + '/products'

        data = {}  # type: Dict[str, str]

        if some_complex_parameter is not None:
            data['some_complex_parameter'] = json.dumps(
                to_jsonable(
                    some_complex_parameter,
                    expected=[Profile]))

        data['some_str_parameter'] = str(some_str_parameter)

        if some_int_parameter is not None:
            data['some_int_parameter'] = str(some_int_parameter)

        resp = requests.request(
            method='get',
            url=url,
            data=data,
            auth=self.auth)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
