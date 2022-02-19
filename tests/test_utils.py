
import os
import unittest

from src import utils


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

    def test_attrdict_read_write(self) -> None:
        self.attrdict.a, self.attrdict.b = 1, 2
        self.assertEqual(self.attrdict.a, 1)
        self.assertEqual(self.attrdict.pop('b'), 2)

    def test_staticdict_write(self) -> None:
        def _set_wrap():
            self.staticdict.c = 1
        def _del_wrap():
            del self.staticdict.a  # type: ignore
        self.assertRaises(RuntimeError, _set_wrap)
        self.assertRaises(RuntimeError, _del_wrap)

    def test_property_decorator(self) -> None:
        self.assertEqual(self.test_instance.value, 1)
        self.assertEqual(self.test_instance.hidden, 2)
        self.test_instance.value = 2
        self.assertEqual(self.test_instance.value, 2)
        del self.test_instance.value
        self.assertRaises(AttributeError, lambda: self.test_instance.value)

    def test_listdir(self) -> None:
        workpath = os.path.dirname(os.path.abspath(__file__))
        self.assertEqual(list(utils.listdir(workpath)), [
            os.path.join(workpath, 'app')
        ])

    def test_startstrip_invalid(self) -> None:
        self.assertEqual(
            utils.startstrip('plugins.domain.endpoint', 'abc'),
            'plugins.domain.endpoint'
        )

    def test_startstrip_valid(self) -> None:
        self.assertEqual(
            utils.startstrip('plugins.domain.endpoint', 'plugins.'),
            'domain.endpoint'
        )

    def test_remove_none_exist_dir(self) -> None:
        dirname = 'tests/testdir'
        self.assertRaises(FileNotFoundError, lambda: utils.rmdir(dirname))

    def test_remove_dir(self) -> None:
        dirname = 'tests/testdir'
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        with open(os.path.join(dirname, 'test.txt'), 'w') as handler:
            handler.write('test')
        utils.rmdir(dirname)
        self.assert_(not os.path.isdir(dirname))

    def test_download_valid_file(self) -> None:
        dirname, filename = 'tests/testdir', 'flask-plugin.zip'
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        url = 'https://github.com/guiqiqi/flask-plugin/archive/refs/tags/v0.1.0.zip'
        progress = 0.
        for progress in utils.download(url, saveto=os.path.join(dirname, filename)):
            self.assertLessEqual(progress, 1.0)
        self.assertEqual(progress, 1.0)
        self.assert_(os.path.isfile(os.path.join(dirname, filename)))
        utils.rmdir(dirname)
