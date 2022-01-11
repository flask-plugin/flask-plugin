
import unittest

from flask_plugin import utils


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.attrdict = utils.attrdict()
        self.staticdict = utils.staticdict({
            'a': 1, 'b': 2
        })

        class TestClass:
            value = utils.property_('value', type_=int, writable=True, delectable=True)
            hidden = utils.property_('hidden', type_=int, prefix='__')

            def __init__(self) -> None:
                self._value = 1
                self.__hidden = 2

        self.test_instance = TestClass()

    def test_attrdict_read_write(self):
        self.attrdict.a, self.attrdict.b = 1, 2
        self.assertEqual(self.attrdict.a, 1)
        self.assertEqual(self.attrdict.pop('b'), 2)

    def test_staticdict_write(self):
        def _set_wrap():
            self.staticdict.c = 1
        def _del_wrap():
            del self.staticdict.a  # type: ignore
        self.assertRaises(RuntimeError, _set_wrap)
        self.assertRaises(RuntimeError, _del_wrap)

    def test_property_decorator(self):
        self.assertEqual(self.test_instance.value, 1)
        self.assertEqual(self.test_instance.hidden, 2)
        self.test_instance.value = 2
        self.assertEqual(self.test_instance.value, 2)
