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

    if exp == AnyTypeValuesContainerInProperty:
        return any_type_values_container_in_property_from_obj(obj, path=path)

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

    if exp == AnyTypeValuesContainerInProperty:
        assert isinstance(obj, AnyTypeValuesContainerInProperty)
        return any_type_values_container_in_property_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class AnyTypeValuesContainerInProperty:
    def __init__(
            self,
            array: List[Any],
            mapping: Dict[str, Any]) -> None:
        """Initializes with the given values."""
        self.array = array

        self.mapping = mapping

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to any_type_values_container_in_property_to_jsonable.

        :return: JSON-able representation
        """
        return any_type_values_container_in_property_to_jsonable(self)


def new_any_type_values_container_in_property() -> AnyTypeValuesContainerInProperty:
    """Generates an instance of AnyTypeValuesContainerInProperty with default values."""
    return AnyTypeValuesContainerInProperty(
        array=[],
        mapping=dict())


def any_type_values_container_in_property_from_obj(obj: Any, path: str = "") -> AnyTypeValuesContainerInProperty:
    """
    Generates an instance of AnyTypeValuesContainerInProperty from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of AnyTypeValuesContainerInProperty
    :param path: path to the object used for debugging
    :return: parsed instance of AnyTypeValuesContainerInProperty
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))

    array_from_obj = from_obj(
        obj['array'],
        expected=[list, Any],
        path=path + '.array')  # type: List[Any]

    mapping_from_obj = from_obj(
        obj['mapping'],
        expected=[dict, Any],
        path=path + '.mapping')  # type: Dict[str, Any]

    return AnyTypeValuesContainerInProperty(
        array=array_from_obj,
        mapping=mapping_from_obj)


def any_type_values_container_in_property_to_jsonable(
        any_type_values_container_in_property: AnyTypeValuesContainerInProperty,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of AnyTypeValuesContainerInProperty.

    :param any_type_values_container_in_property: instance of AnyTypeValuesContainerInProperty to be JSON-ized
    :param path: path to the any_type_values_container_in_property used for debugging
    :return: a JSON-able representation
    """
    res = dict()  # type: Dict[str, Any]

    res['array'] = to_jsonable(
        any_type_values_container_in_property.array,
        expected=[list, Any],
        path='{}.array'.format(path))

    res['mapping'] = to_jsonable(
        any_type_values_container_in_property.mapping,
        expected=[dict, Any],
        path='{}.mapping'.format(path))

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

    def get_foo(
            self,
            body: List[Any]) -> List[Any]:
        """
        Send a post request to /foo.

        :param body:

        :return: response
        """
        url = self.url_prefix + '/foo'

        data = to_jsonable(
            body,
            expected=[list, Any])


        resp = self.session.request(
            method='post',
            url=url,
            json=data,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[list, Any])

    def get_bar(
            self,
            body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a post request to /bar.

        :param body:

        :return: response
        """
        url = self.url_prefix + '/bar'

        data = to_jsonable(
            body,
            expected=[dict, Any])


        resp = self.session.request(
            method='post',
            url=url,
            json=data,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[dict, Any])

    def get_baz(
            self,
            body: AnyTypeValuesContainerInProperty) -> AnyTypeValuesContainerInProperty:
        """
        Send a post request to /baz.

        :param body:

        :return: response
        """
        url = self.url_prefix + '/baz'

        data = to_jsonable(
            body,
            expected=[AnyTypeValuesContainerInProperty])


        resp = self.session.request(
            method='post',
            url=url,
            json=data,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[AnyTypeValuesContainerInProperty])

    def get_qux(
            self,
            body: Any) -> Any:
        """
        Send a post request to /qux.

        :param body:

        :return: response
        """
        url = self.url_prefix + '/qux'

        data = to_jsonable(
            body,
            expected=[Any])


        resp = self.session.request(
            method='post',
            url=url,
            json=data,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[Any])


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
