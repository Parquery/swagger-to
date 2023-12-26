#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for API."""

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

    if exp == SomeDefinition:
        return some_definition_from_obj(obj, path=path)

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

    if exp == SomeDefinition:
        assert isinstance(obj, SomeDefinition)
        return some_definition_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class SomeDefinition:
    def __init__(
            self,
            some_property: Optional[int] = None) -> None:
        """Initializes with the given values."""
        self.some_property = some_property

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to some_definition_to_jsonable.

        :return: JSON-able representation
        """
        return some_definition_to_jsonable(self)


def new_some_definition() -> SomeDefinition:
    """Generates an instance of SomeDefinition with default values."""
    return SomeDefinition()


def some_definition_from_obj(obj: Any, path: str = "") -> SomeDefinition:
    """
    Generates an instance of SomeDefinition from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of SomeDefinition
    :param path: path to the object used for debugging
    :return: parsed instance of SomeDefinition
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))

    obj_some_property = obj.get('some.property', None)
    if obj_some_property is not None:
        some_property_from_obj = from_obj(
            obj_some_property,
            expected=[int],
            path=path + '.some.property')  # type: Optional[int]
    else:
        some_property_from_obj = None

    return SomeDefinition(
        some_property=some_property_from_obj)


def some_definition_to_jsonable(
        some_definition: SomeDefinition,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of SomeDefinition.

    :param some_definition: instance of SomeDefinition to be JSON-ized
    :param path: path to the some_definition used for debugging
    :return: a JSON-able representation
    """
    res = dict()  # type: Dict[str, Any]

    if some_definition.some_property is not None:
        res['some.property'] = some_definition.some_property

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

    def do_something(
            self,
            some_parameter: 'SomeDefinition',
            another_parameter: Optional[str] = None) -> MutableMapping[str, Any]:
        """
        Send a post request to /do.something.

        :param some_parameter: some test parameter
        :param another_parameter: another test parameter, this time not required and in query

        :return: Success
        """
        url = self.url_prefix + '/do.something'

        params = {}  # type: Dict[str, str]

        if another_parameter is not None:
            params['another.parameter'] = another_parameter

        data = to_jsonable(
            some_parameter,
            expected=[SomeDefinition])


        resp = self.session.request(
            method='post',
            url=url,
            params=params,
            json=data,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.json()


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
