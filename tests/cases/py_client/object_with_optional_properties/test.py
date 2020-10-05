import unittest

from .client import test_object_from_obj


class TestFromObj(unittest.TestCase):
    def test_no_field_specified(self) -> None:
        test_obj = test_object_from_obj(obj=dict())
        self.assertIsNone(test_obj.product_id)
        self.assertIsNone(test_obj.capacity)

    def test_all_fields_specified(self) -> None:
        test_obj = test_object_from_obj(
            obj={"product_id": "some-product", "capacity": 3})
        self.assertEqual("some-product", test_obj.product_id)
        self.assertEqual(3, test_obj.capacity)

    def test_all_fields_None(self) -> None:
        test_obj = test_object_from_obj(
            obj={"product_id": None, "capacity": None})
        self.assertIsNone(test_obj.product_id)
        self.assertIsNone(test_obj.capacity)


if __name__ == '__main__':
    unittest.main()
