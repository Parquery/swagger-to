#!bin/bash/python3
# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
"""Implements the client for uber."""

# pylint: skip-file
# pydocstyle: add-ignore=D105,D107,D401

import contextlib
from typing import Any, BinaryIO, Dict, List, Optional

import requests
import requests.auth


def from_obj(obj: Any, expected: List[type], path: str = '') -> Any:
    """
    Checks and converts the given obj along the expected types.

    :param obj: to be converted
    :param expected: list of types representing the (nested) structure
    :param path: to the object from the root object
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

        raise ValueError("Expected object of type int or float at {!r}, but got {}.".format(path, type(obj)))

    if exp in [bool, int, str, list, dict]:
        if not isinstance(obj, exp):
            raise ValueError("Expected object of type {} at {!r}, but got {}.".format(exp, path, type(obj)))

    if exp in [bool, int, float, str]:
        return obj

    if exp == list:
        lst = []  # type: List[Any]
        for i, value in enumerate(obj):
            lst.append(from_obj(value, expected=expected[1:], path=path + '[{}]'.format(i)))

        return lst

    if exp == dict:
        adict = dict()  # type: Dict[str, Any]
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError("Expected a key of type str at path {!r}, got: {}".format(path, type(key)))

            adict[key] = from_obj(value, expected=expected[1:], path=path + '["{}"]'.format(key))

        return adict

    if exp == Product:
        return product_from_obj(obj, path=path)

    if exp == ProductList:
        return product_list_from_obj(obj, path=path)

    if exp == PriceEstimate:
        return price_estimate_from_obj(obj, path=path)

    if exp == Profile:
        return profile_from_obj(obj, path=path)

    if exp == Activity:
        return activity_from_obj(obj, path=path)

    if exp == Activities:
        return activities_from_obj(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


def to_jsonable(obj: Any, expected: List[type], path: str = "") -> Any:
    """
    Checks and converts the given object along the expected types to a JSON-able representation.

    :param obj: to be converted
    :param expected: list of types representing the (nested) structure
    :return: JSON-able representation of the object

    """
    if not expected:
        raise ValueError("`expected` is empty, but at least one type needs to be specified.")

    exp = expected[0]
    if not isinstance(obj, exp):
        raise ValueError("Expected object of type {} at path {!r}, but got {}.".format(exp, path, type(obj)))

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
            lst.append(to_jsonable(value, expected=expected[1:], path=''.join([path, '[', str(i), ']'])))

        return lst

    if exp == dict:
        assert isinstance(obj, dict)

        adict = dict()  # type: Dict[str, Any]
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError("Expected a key of type str at path {!r}, got: {}".format(path, type(key)))

            adict[key] = to_jsonable(value, expected=expected[1:], path=''.join([path, '[', key, ']']))

        return adict

    if exp == Product:
        assert isinstance(obj, Product)
        return product_to_jsonable(obj, path=path)

    if exp == ProductList:
        assert isinstance(obj, ProductList)
        return product_list_to_jsonable(obj, path=path)

    if exp == PriceEstimate:
        assert isinstance(obj, PriceEstimate)
        return price_estimate_to_jsonable(obj, path=path)

    if exp == Profile:
        assert isinstance(obj, Profile)
        return profile_to_jsonable(obj, path=path)

    if exp == Activity:
        assert isinstance(obj, Activity)
        return activity_to_jsonable(obj, path=path)

    if exp == Activities:
        assert isinstance(obj, Activities)
        return activities_to_jsonable(obj, path=path)

    raise ValueError("Unexpected `expected` type: {}".format(exp))


class Product:
    def __init__(self,
                 product_id: str,
                 desc: str,
                 display_name: str,
                 capacity: int,
                 image: str) -> None:
        # Unique identifier representing a specific product for a given latitude & longitude.
        # For example, uberX in San Francisco will have a different product_id than uberX in Los Angeles.
        self.product_id = product_id

        # Description of product.
        self.desc = desc

        # Display name of product.
        self.display_name = display_name

        # Capacity of product. For example, 4 people.
        self.capacity = capacity

        # Image URL representing the product.
        self.image = image

    def to_jsonable(self) -> Dict[str, Any]:
        """
        Dispatches the conversion to product_to_jsonable.

        :return: JSON-able representation

        """
        return product_to_jsonable(self)


def new_product() -> Product:
    """Generates a default instance of Product."""
    return Product(product_id='',
                   desc='',
                   display_name='',
                   capacity=0,
                   image='')


def product_from_obj(obj: Any, path: str = "") -> Product:
    """Generates an instance of Product from a dictionary object."""
    if not isinstance(obj, dict):
        raise ValueError("Expected a dict at path {}, but got: {}".format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError("Expected a key of type str at path {}, but got: {}".format(path, type(key)))

    product_id_from_obj = from_obj(obj["product_id"],
                                   expected=[str],
                                   path=path + ".product_id")  # type: str

    desc_from_obj = from_obj(obj["desc"],
                             expected=[str],
                             path=path + ".desc")  # type: str

    display_name_from_obj = from_obj(obj["display_name"],
                                     expected=[str],
                                     path=path + ".display_name")  # type: str

    capacity_from_obj = from_obj(obj["capacity"],
                                 expected=[int],
                                 path=path + ".capacity")  # type: int

    image_from_obj = from_obj(obj["image"],
                              expected=[str],
                              path=path + ".image")  # type: str

    return Product(product_id=product_id_from_obj,
                   desc=desc_from_obj,
                   display_name=display_name_from_obj,
                   capacity=capacity_from_obj,
                   image=image_from_obj)


def product_to_jsonable(product: Product, path: str = "") -> Dict[str, Any]:
    """Generates a dictionary JSON-able object from an instance of Product."""
    res = dict()  # type: Dict[str, Any]

    res["product_id"] = product.product_id

    res["desc"] = product.desc

    res["display_name"] = product.display_name

    res["capacity"] = product.capacity

    res["image"] = product.image
    return res


class ProductList:
    def __init__(self, products: List[Product]) -> None:
        # Contains the list of products
        self.products = products

    def to_jsonable(self) -> Dict[str, Any]:
        """
        Dispatches the conversion to product_list_to_jsonable.

        :return: JSON-able representation

        """
        return product_list_to_jsonable(self)


def new_product_list() -> ProductList:
    """Generates a default instance of ProductList."""
    return ProductList(products=[])


def product_list_from_obj(obj: Any, path: str = "") -> ProductList:
    """Generates an instance of ProductList from a dictionary object."""
    if not isinstance(obj, dict):
        raise ValueError("Expected a dict at path {}, but got: {}".format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError("Expected a key of type str at path {}, but got: {}".format(path, type(key)))

    products_from_obj = from_obj(obj["products"],
                                 expected=[list, Product],
                                 path=path + ".products")  # type: List[Product]

    return ProductList(products=products_from_obj)


def product_list_to_jsonable(product_list: ProductList, path: str = "") -> Dict[str, Any]:
    """Generates a dictionary JSON-able object from an instance of ProductList."""
    res = dict()  # type: Dict[str, Any]

    res["products"] = to_jsonable(product_list.products,
                                  [list, Product],
                                  "{}.products".format(path))
    return res


class PriceEstimate:
    def __init__(self,
                 product_id: str,
                 currency_code: str,
                 display_name: str,
                 estimate: str,
                 low_estimate: Optional[float] = None,
                 high_estimate: Optional[float] = None,
                 surge_multiplier: Optional[float] = None) -> None:
        # Unique identifier representing a specific product for a given latitude & longitude. For example,
        # uberX in San Francisco will have a different product_id than uberX in Los Angeles
        self.product_id = product_id

        # [ISO 4217](http://en.wikipedia.org/wiki/ISO_4217) currency code.
        self.currency_code = currency_code

        # Display name of product.
        self.display_name = display_name

        # Formatted string of estimate in local currency of the start location.
        # Estimate could be a range, a single number (flat rate) or "Metered" for TAXI.
        self.estimate = estimate

        # Lower bound of the estimated price.
        self.low_estimate = low_estimate

        # Upper bound of the estimated price.
        self.high_estimate = high_estimate

        # Expected surge multiplier. Surge is active if surge_multiplier is greater than 1.
        # Price estimate already factors in the surge multiplier.
        self.surge_multiplier = surge_multiplier

    def to_jsonable(self) -> Dict[str, Any]:
        """
        Dispatches the conversion to price_estimate_to_jsonable.

        :return: JSON-able representation

        """
        return price_estimate_to_jsonable(self)


def new_price_estimate() -> PriceEstimate:
    """Generates a default instance of PriceEstimate."""
    return PriceEstimate(product_id='',
                         currency_code='',
                         display_name='',
                         estimate='')


def price_estimate_from_obj(obj: Any, path: str = "") -> PriceEstimate:
    """Generates an instance of PriceEstimate from a dictionary object."""
    if not isinstance(obj, dict):
        raise ValueError("Expected a dict at path {}, but got: {}".format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError("Expected a key of type str at path {}, but got: {}".format(path, type(key)))

    product_id_from_obj = from_obj(obj["product_id"],
                                   expected=[str],
                                   path=path + ".product_id")  # type: str

    currency_code_from_obj = from_obj(obj["currency_code"],
                                      expected=[str],
                                      path=path + ".currency_code")  # type: str

    display_name_from_obj = from_obj(obj["display_name"],
                                     expected=[str],
                                     path=path + ".display_name")  # type: str

    estimate_from_obj = from_obj(obj["estimate"],
                                 expected=[str],
                                 path=path + ".estimate")  # type: str

    low_estimate = None  # type: Optional[float]
    if "low_estimate" in obj:
        low_estimate_from_obj = from_obj(obj["low_estimate"],
                                         expected=[float],
                                         path=path + ".low_estimate")  # type: float

    high_estimate = None  # type: Optional[float]
    if "high_estimate" in obj:
        high_estimate_from_obj = from_obj(obj["high_estimate"],
                                          expected=[float],
                                          path=path + ".high_estimate")  # type: float

    surge_multiplier = None  # type: Optional[float]
    if "surge_multiplier" in obj:
        surge_multiplier_from_obj = from_obj(obj["surge_multiplier"],
                                             expected=[float],
                                             path=path + ".surge_multiplier")  # type: float

    return PriceEstimate(product_id=product_id_from_obj,
                         currency_code=currency_code_from_obj,
                         display_name=display_name_from_obj,
                         estimate=estimate_from_obj,
                         low_estimate=low_estimate_from_obj,
                         high_estimate=high_estimate_from_obj,
                         surge_multiplier=surge_multiplier_from_obj)


def price_estimate_to_jsonable(price_estimate: PriceEstimate, path: str = "") -> Dict[str, Any]:
    """Generates a dictionary JSON-able object from an instance of PriceEstimate."""
    res = dict()  # type: Dict[str, Any]

    res["product_id"] = price_estimate.product_id

    res["currency_code"] = price_estimate.currency_code

    res["display_name"] = price_estimate.display_name

    res["estimate"] = price_estimate.estimate

    if price_estimate.low_estimate is not None:
        res["low_estimate"] = price_estimate.low_estimate

    if price_estimate.high_estimate is not None:
        res["high_estimate"] = price_estimate.high_estimate

    if price_estimate.surge_multiplier is not None:
        res["surge_multiplier"] = price_estimate.surge_multiplier
    return res


class Profile:
    def __init__(self,
                 last_name: str,
                 email: str,
                 picture: str,
                 first_name: Optional[str] = None,
                 promo_code: Optional[str] = None) -> None:
        # Last name of the Uber user.
        self.last_name = last_name

        # Email address of the Uber user
        self.email = email

        # Image URL of the Uber user.
        self.picture = picture

        # First name of the Uber user.
        self.first_name = first_name

        # Promo code of the Uber user.
        self.promo_code = promo_code

    def to_jsonable(self) -> Dict[str, Any]:
        """
        Dispatches the conversion to profile_to_jsonable.

        :return: JSON-able representation

        """
        return profile_to_jsonable(self)


def new_profile() -> Profile:
    """Generates a default instance of Profile."""
    return Profile(last_name='', email='', picture='')


def profile_from_obj(obj: Any, path: str = "") -> Profile:
    """Generates an instance of Profile from a dictionary object."""
    if not isinstance(obj, dict):
        raise ValueError("Expected a dict at path {}, but got: {}".format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError("Expected a key of type str at path {}, but got: {}".format(path, type(key)))

    last_name_from_obj = from_obj(obj["last_name"],
                                  expected=[str],
                                  path=path + ".last_name")  # type: str

    email_from_obj = from_obj(obj["email"],
                              expected=[str],
                              path=path + ".email")  # type: str

    picture_from_obj = from_obj(obj["picture"],
                                expected=[str],
                                path=path + ".picture")  # type: str

    first_name = None  # type: Optional[str]
    if "first_name" in obj:
        first_name_from_obj = from_obj(obj["first_name"],
                                       expected=[str],
                                       path=path + ".first_name")  # type: str

    promo_code = None  # type: Optional[str]
    if "promo_code" in obj:
        promo_code_from_obj = from_obj(obj["promo_code"],
                                       expected=[str],
                                       path=path + ".promo_code")  # type: str

    return Profile(last_name=last_name_from_obj,
                   email=email_from_obj,
                   picture=picture_from_obj,
                   first_name=first_name_from_obj,
                   promo_code=promo_code_from_obj)


def profile_to_jsonable(profile: Profile, path: str = "") -> Dict[str, Any]:
    """Generates a dictionary JSON-able object from an instance of Profile."""
    res = dict()  # type: Dict[str, Any]

    res["last_name"] = profile.last_name

    res["email"] = profile.email

    res["picture"] = profile.picture

    if profile.first_name is not None:
        res["first_name"] = profile.first_name

    if profile.promo_code is not None:
        res["promo_code"] = profile.promo_code
    return res


class Activity:
    def __init__(self, uuid: str) -> None:
        # Unique identifier for the activity
        self.uuid = uuid

    def to_jsonable(self) -> Dict[str, Any]:
        """
        Dispatches the conversion to activity_to_jsonable.

        :return: JSON-able representation

        """
        return activity_to_jsonable(self)


def new_activity() -> Activity:
    """Generates a default instance of Activity."""
    return Activity(uuid='')


def activity_from_obj(obj: Any, path: str = "") -> Activity:
    """Generates an instance of Activity from a dictionary object."""
    if not isinstance(obj, dict):
        raise ValueError("Expected a dict at path {}, but got: {}".format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError("Expected a key of type str at path {}, but got: {}".format(path, type(key)))

    uuid_from_obj = from_obj(obj["uuid"],
                             expected=[str],
                             path=path + ".uuid")  # type: str

    return Activity(uuid=uuid_from_obj)


def activity_to_jsonable(activity: Activity, path: str = "") -> Dict[str, Any]:
    """Generates a dictionary JSON-able object from an instance of Activity."""
    res = dict()  # type: Dict[str, Any]

    res["uuid"] = activity.uuid
    return res


class Activities:
    def __init__(self,
                 offset: int,
                 limit: int,
                 count: int,
                 history: List[Activity]) -> None:
        # Position in pagination.
        self.offset = offset

        # Number of items to retrieve (100 max).
        self.limit = limit

        # Total number of items available.
        self.count = count

        self.history = history

    def to_jsonable(self) -> Dict[str, Any]:
        """
        Dispatches the conversion to activities_to_jsonable.

        :return: JSON-able representation

        """
        return activities_to_jsonable(self)


def new_activities() -> Activities:
    """Generates a default instance of Activities."""
    return Activities(offset=0, limit=0, count=0, history=[])


def activities_from_obj(obj: Any, path: str = "") -> Activities:
    """Generates an instance of Activities from a dictionary object."""
    if not isinstance(obj, dict):
        raise ValueError("Expected a dict at path {}, but got: {}".format(path, type(obj)))

    for key in obj:
        if not isinstance(key, str):
            raise ValueError("Expected a key of type str at path {}, but got: {}".format(path, type(key)))

    offset_from_obj = from_obj(obj["offset"],
                               expected=[int],
                               path=path + ".offset")  # type: int

    limit_from_obj = from_obj(obj["limit"],
                              expected=[int],
                              path=path + ".limit")  # type: int

    count_from_obj = from_obj(obj["count"],
                              expected=[int],
                              path=path + ".count")  # type: int

    history_from_obj = from_obj(obj["history"],
                                expected=[list, Activity],
                                path=path + ".history")  # type: List[Activity]

    return Activities(offset=offset_from_obj,
                      limit=limit_from_obj,
                      count=count_from_obj,
                      history=history_from_obj)


def activities_to_jsonable(activities: Activities, path: str = "") -> Dict[str, Any]:
    """Generates a dictionary JSON-able object from an instance of Activities."""
    res = dict()  # type: Dict[str, Any]

    res["offset"] = activities.offset

    res["limit"] = activities.limit

    res["count"] = activities.count

    res["history"] = to_jsonable(activities.history,
                                 [list, Activity],
                                 "{}.history".format(path))
    return res


class RemoteCaller:
    """Executes the remote calls to the server."""

    def __init__(self, url_prefix: str, auth: Optional[requests.auth.AuthBase] = None) -> None:
        self.url_prefix = url_prefix
        self.auth = auth

    def products(self, latitude: float, longitude: float) -> Dict[str, Product]:
        """
        The Products endpoint returns information about the Uber products offered at a given location.

        :param latitude: Latitude component of location.
        :param longitude: Longitude component of location.

        """
        url = self.url_prefix + "/products"

        params = {
            "latitude": latitude,
            "longitude": longitude}

        resp = requests.request(method='get', url=url, params=params, auth=self.auth)
        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(obj=resp.json(), expected=[dict, Product], path="")

    def estimates_price(self,
                        start_latitude: float,
                        start_longitude: float,
                        end_latitude: float,
                        end_longitude: float,
                        max_lines: Optional[int] = None) -> List[Product]:
        """
        The Price Estimates endpoint returns an estimated price range for each product offered at a given
        location. The price estimate is provided as a formatted string with the full price range and the localized
        currency symbol.

        :param start_latitude: Latitude component of start location.
        :param start_longitude: Longitude component of start location.
        :param end_latitude: Latitude component of end location.
        :param end_longitude: Longitude component of end location.
        :param max_lines: A maximum number of lines in the produced json.

        """
        url_parts = [self.url_prefix]
        url_parts.append("/estimates/price/")
        url_parts.append(str(start_latitude))
        url_parts.append("/")
        url_parts.append(str(start_longitude))
        url_parts.append("/")
        url_parts.append(str(end_latitude))
        url_parts.append("/")
        url_parts.append(str(end_longitude))
        url = "".join(url_parts)

        params = {
            "max_lines": max_lines}

        resp = requests.request(method='get', url=url, params=params, auth=self.auth)
        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(obj=resp.json(), expected=[list, Product], path="")

    def estimates_time(self,
                       start_latitude: float,
                       start_longitude: float,
                       customer_uuid: Optional[str] = None,
                       product_id: Optional[str] = None) -> Dict[str, Product]:
        """
        The Time Estimates endpoint returns ETAs for all products.

        :param start_latitude: Latitude component of start location.
        :param start_longitude: Longitude component of start location.
        :param customer_uuid: Unique customer identifier to be used for experience customization.
        :param product_id: Unique identifier representing a specific product for a given latitude & longitude.

        """
        url = self.url_prefix + "/estimates/time"

        params = {
            "start_latitude": start_latitude,
            "start_longitude": start_longitude,
            "customer_uuid": customer_uuid,
            "product_id": product_id}

        resp = requests.request(method='get', url=url, params=params, auth=self.auth)
        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(obj=resp.json(), expected=[dict, Product], path="")

    def update_me(self, update_user: Profile) -> Profile:
        """
        Update an User Profile.

        :param update_user: profile of a user to update

        """
        url = self.url_prefix + "/me"

        data = to_jsonable(update_user, expected=[Profile])

        resp = requests.request(method='patch', url=url, json=data, auth=self.auth)
        with contextlib.closing(resp):
            resp.raise_for_status()
            return from_obj(obj=resp.json(), expected=[Profile], path="")

    def history(self,
                offset: Optional[int] = None,
                limit: Optional[int] = None) -> bytes:
        """
        The User Activity endpoint returns data about a user's lifetime activity with Uber. The response will
        include pickup locations and times, dropoff locations and times, the distance of past requests, and
        information about which products were requested.

        :param offset: Offset the list of returned results by this amount. Default is zero.
        :param limit: Number of items to retrieve. Default is 5, maximum is 100.

        """
        url = self.url_prefix + "/history"

        params = {
            "offset": offset,
            "limit": limit}

        resp = requests.request(method='get', url=url, params=params, auth=self.auth)
        with contextlib.closing(resp):
            resp.raise_for_status()
            return resp.content


# Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
