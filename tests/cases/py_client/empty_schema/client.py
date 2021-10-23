#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for product."""

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

    if exp == EmptyParameter:
        return empty_parameter_from_obj(obj, path=path)

    if exp == WithEmptyProperties:
        return with_empty_properties_from_obj(obj, path=path)

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

    if exp == EmptyParameter:
        assert isinstance(obj, EmptyParameter)
        return empty_parameter_to_jsonable(obj, path=path)

    if exp == WithEmptyProperties:
        assert isinstance(obj, WithEmptyProperties)
        return with_empty_properties_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class EmptyParameter:
    """Defines an empty parameter."""

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to empty_parameter_to_jsonable.

        :return: a JSON-able representation
        """
        return empty_parameter_to_jsonable(self)


def new_empty_parameter() -> EmptyParameter:
    """Generates an instance of EmptyParameter with default values."""
    return EmptyParameter()


def empty_parameter_from_obj(obj: Any, path: str = "") -> EmptyParameter:
    """
    Generates an instance of EmptyParameter from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of EmptyParameter
    :param path: path to the object used for debugging
    :return: parsed instance of EmptyParameter
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    return EmptyParameter()


def empty_parameter_to_jsonable(
        empty_parameter: EmptyParameter,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of EmptyParameter.

    :param empty_parameter: instance of EmptyParameter to be JSON-ized
    :param path: path to the empty_parameter used for debugging
    :return: a JSON-able representation
    """
    return dict()


class WithEmptyProperties:
    """Is a product detail."""

    def __init__(
            self,
            required_empty_property: Any,
            optional_empty_property: Optional[Any] = None) -> None:
        """Initializes with the given values."""
        self.required_empty_property = required_empty_property

        self.optional_empty_property = optional_empty_property

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to with_empty_properties_to_jsonable.

        :return: JSON-able representation
        """
        return with_empty_properties_to_jsonable(self)


def new_with_empty_properties() -> WithEmptyProperties:
    """Generates an instance of WithEmptyProperties with default values."""
    return WithEmptyProperties(
        required_empty_property=None)


def with_empty_properties_from_obj(obj: Any, path: str = "") -> WithEmptyProperties:
    """
    Generates an instance of WithEmptyProperties from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of WithEmptyProperties
    :param path: path to the object used for debugging
    :return: parsed instance of WithEmptyProperties
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))

    required_empty_property_from_obj = obj['required_empty_property']

    optional_empty_property_from_obj = obj.get('optional_empty_property', None)

    return WithEmptyProperties(
        required_empty_property=required_empty_property_from_obj,
        optional_empty_property=optional_empty_property_from_obj)


def with_empty_properties_to_jsonable(
        with_empty_properties: WithEmptyProperties,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of WithEmptyProperties.

    :param with_empty_properties: instance of WithEmptyProperties to be JSON-ized
    :param path: path to the with_empty_properties used for debugging
    :return: a JSON-able representation
    """
    res = dict()  # type: Dict[str, Any]

    res['required_empty_property'] = with_empty_properties.required_empty_property

    if with_empty_properties.optional_empty_property is not None:
        res['optional_empty_property'] = with_empty_properties.optional_empty_property

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

    def test_endpoint(
            self,
            required_empty_parameter: 'EmptyParameter') -> 'WithEmptyProperties':
        """
        Test empty schema

        :param required_empty_parameter:

        :return: a product object
        """
        url = self.url_prefix + '/test_endpoint'

        data = to_jsonable(
            required_empty_parameter,
            expected=[EmptyParameter])


        resp = self.session.request(
            method='get',
            url=url,
            json=data,
        )

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[WithEmptyProperties])


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
