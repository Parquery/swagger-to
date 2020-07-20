#!/usr/bin/env python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for product."""

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

    if exp == ProductSummary:
        return product_summary_from_obj(obj, path=path)

    if exp == ProductDetail:
        return product_detail_from_obj(obj, path=path)

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

    if exp == ProductSummary:
        assert isinstance(obj, ProductSummary)
        return product_summary_to_jsonable(obj, path=path)

    if exp == ProductDetail:
        assert isinstance(obj, ProductDetail)
        return product_detail_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class ProductSummary:
    """Is a product summary object."""

    def __init__(
            self,
            product_id: str,
            metadata: Optional[Any] = None,
            capacity: Optional[int] = None) -> None:
        """Initializes with the given values."""
        # is a test string property.
        self.product_id = product_id

        self.metadata = metadata

        self.capacity = capacity

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to product_summary_to_jsonable.

        :return: JSON-able representation
        """
        return product_summary_to_jsonable(self)


def new_product_summary() -> ProductSummary:
    """Generates an instance of ProductSummary with default values."""
    return ProductSummary(
        product_id='')


def product_summary_from_obj(obj: Any, path: str = "") -> ProductSummary:
    """
    Generates an instance of ProductSummary from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of ProductSummary
    :param path: path to the object used for debugging
    :return: parsed instance of ProductSummary
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))

    product_id_from_obj = from_obj(
        obj['product_id'],
        expected=[str],
        path=path + '.product_id')  # type: str

    if 'metadata' in obj:
        metadata_from_obj = obj['metadata']
    else:
        metadata_from_obj = None

    if 'capacity' in obj:
        capacity_from_obj = from_obj(
            obj['capacity'],
            expected=[int],
            path=path + '.capacity')  # type: Optional[int]
    else:
        capacity_from_obj = None

    return ProductSummary(
        product_id=product_id_from_obj,
        metadata=metadata_from_obj,
        capacity=capacity_from_obj)


def product_summary_to_jsonable(
        product_summary: ProductSummary,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of ProductSummary.

    :param product_summary: instance of ProductSummary to be JSON-ized
    :param path: path to the product_summary used for debugging
    :return: a JSON-able representation
    """
    res = dict()  # type: Dict[str, Any]

    res['product_id'] = product_summary.product_id

    if product_summary.metadata is not None:
        res['metadata'] = product_summary.metadata

    if product_summary.capacity is not None:
        res['capacity'] = product_summary.capacity

    return res


class ProductDetail:
    """Is a product detail"""

    def __init__(
            self,
            product_id: str,
            metadata: Any,
            data: Any,
            capacity: Optional[int] = None) -> None:
        """Initializes with the given values."""
        # is a test string property.
        self.product_id = product_id

        self.metadata = metadata

        self.data = data

        self.capacity = capacity

    def to_jsonable(self) -> MutableMapping[str, Any]:
        """
        Dispatches the conversion to product_detail_to_jsonable.

        :return: JSON-able representation
        """
        return product_detail_to_jsonable(self)


def new_product_detail() -> ProductDetail:
    """Generates an instance of ProductDetail with default values."""
    return ProductDetail(
        product_id='',
        metadata=None,
        data=None)


def product_detail_from_obj(obj: Any, path: str = "") -> ProductDetail:
    """
    Generates an instance of ProductDetail from a dictionary object.

    :param obj: a JSON-ed dictionary object representing an instance of ProductDetail
    :param path: path to the object used for debugging
    :return: parsed instance of ProductDetail
    """
    if not isinstance(obj, dict):
        raise ValueError('Expected a dict at path {}, but got: {}'.format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError(
                'Expected a key of type str at path {}, but got: {}'.format(path, type(key)))

    product_id_from_obj = from_obj(
        obj['product_id'],
        expected=[str],
        path=path + '.product_id')  # type: str

    metadata_from_obj = obj['metadata']

    data_from_obj = obj['data']

    if 'capacity' in obj:
        capacity_from_obj = from_obj(
            obj['capacity'],
            expected=[int],
            path=path + '.capacity')  # type: Optional[int]
    else:
        capacity_from_obj = None

    return ProductDetail(
        product_id=product_id_from_obj,
        metadata=metadata_from_obj,
        data=data_from_obj,
        capacity=capacity_from_obj)


def product_detail_to_jsonable(
        product_detail: ProductDetail,
        path: str = "") -> MutableMapping[str, Any]:
    """
    Generates a JSON-able mapping from an instance of ProductDetail.

    :param product_detail: instance of ProductDetail to be JSON-ized
    :param path: path to the product_detail used for debugging
    :return: a JSON-able representation
    """
    res = dict()  # type: Dict[str, Any]

    res['product_id'] = product_detail.product_id

    res['metadata'] = product_detail.metadata

    res['data'] = product_detail.data

    if product_detail.capacity is not None:
        res['capacity'] = product_detail.capacity

    return res


class RemoteCaller:
    """Executes the remote calls to the server."""

    def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth

    def list_products(
            self,
            with_attributes: Optional[bool] = None) -> ProductSummary:
        """
        Describe products

        :param with_attributes:

        :return: product summaries
        """
        url = self.url_prefix + '/products'

        params = {}  # type: Dict[str, str]

        if with_attributes is not None:
            params['with_attributes'] = json.dumps(with_attributes)

        resp = requests.request(
            method='get',
            url=url,
            params=params,
            auth=self.auth)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[ProductSummary])

    def get_product(
            self,
            id: str) -> ProductDetail:
        """
        Product detail

        :param id:

        :return: a product object
        """
        url = "".join([
            self.url_prefix,
            '/products/',
            str(id)])

        resp = requests.request(
            method='get',
            url=url,
            auth=self.auth)

        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(
                obj=resp.json(),
                expected=[ProductDetail])


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
