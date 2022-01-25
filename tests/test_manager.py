
import unittest

from src import PluginManager, Plugin

from .app import init_app


class TestManagerApp(unittest.TestCase):

    def setUp(self) -> None:
        self.app = init_app('BaseDevelopmentConfig')
        self.client = self.app.test_client()
        self.manager: PluginManager = self.app.plugin_manager  # type: ignore

    def test_plugins_not_empty(self) -> None:
        self.assertNotEqual(self.manager.plugins, [])

    def test_scan_plugins_excludes(self) -> None:
        for plugin in self.manager.scan():
            self.assertNotIn(
                plugin.basedir, self.app.config['PLUGINS_EXCLUDES_DIRECTORY'])

    def test_no_plugins_loaded(self) -> None:
        all_plugins_name = set(plugin.name for plugin in self.manager.plugins)
        all_scanned_name = set(plugin.name for plugin in self.manager.scan())
        self.assertSetEqual(all_plugins_name, all_scanned_name)

    def test_load_plugins(self) -> None:
        for plugin in self.manager.plugins:
            try:
                self.manager.load(plugin)
            except RuntimeError as e:
                self.fail(
                    f"load plugin failed: {plugin.name}, {str(e.args[0])}")
        self.assertEqual(list(self.manager.scan()), [])

    def test_find_plugins(self) -> None:
        self.test_load_plugins()
        plugin = self.manager.find(domain='hello')
        self.assertNotEqual(plugin, None)
        self.assertEqual(
            self.manager.find(domain='hello'),
            self.manager.find(name='hello')
        )

    def test_invalid_find_plugins(self) -> None:
        self.test_load_plugins()
        self.assertEqual(self.manager.find(), None)
        self.assertEqual(self.manager.find(id_='non-exists'), None)

    def test_unload_plugins_after_load(self) -> None:
        self.test_load_plugins()
        for plugin in self.manager.plugins:
            try:
                self.manager.unload(plugin)
            except Exception as e:
                self.fail(
                    f"unload plugin failed: {plugin.name}, {str(e.args[0])}")

    def test_reload_and_start_plugins(self) -> None:
        self.test_unload_plugins_after_load()
        for plugin in self.manager.plugins:
            try:
                self.manager.load(plugin)
                self.manager.start(plugin)
            except Exception as e:
                self.fail(
                    f"start plugin failed: {plugin.name}, {str(e.args[0])}")

    def test_stop_plugins(self) -> None:
        self.test_reload_and_start_plugins()
        for plugin in self.manager.plugins:
            try:
                self.manager.stop(plugin)
            except Exception as e:
                self.fail(
                    f"stop plugin failed: {plugin.name}, {str(e.args[0])}")

    def test_unload_plugins_after_all_processes(self) -> None:
        self.test_stop_plugins()
        for plugin in self.manager.plugins:
            try:
                self.manager.unload(plugin)
            except Exception as e:
                self.fail(
                    f"unload plugin failed: {plugin.name}, {str(e.args[0])}")


class TestInvalidImportManagerApp(unittest.TestCase):

    def setUp(self) -> None:
        self.app = init_app('InvalidPluginImportConfig')
        self.manager: PluginManager = self.app.plugin_manager  # type: ignore

    def test_invalid_import_plugin(self) -> None:
        self.assertRaises(ImportError, lambda: list(self.manager.plugins))


class TestNonExistDirectoryManagerApp(unittest.TestCase):

    def setUp(self) -> None:
        self.app = init_app('NonExistDirectoryConfig')
        self.manager: PluginManager = self.app.plugin_manager  # type: ignore

    def test_non_exist_direcotry(self) -> None:
        self.assertRaises(FileNotFoundError,
                          lambda: list(self.manager.plugins))


class TestDuplicatedPluginIDApp(unittest.TestCase):

    def setUp(self) -> None:
        self.app = init_app('DuplicatedPluginId')
        self.manager: PluginManager = self.app.plugin_manager  # type: ignore
    
    def test_load_duplicated_id_plugin(self) -> None:
        def _load_all_plugins():
            for plugin in self.manager.plugins:
                self.manager.load(plugin)
        self.assertRaises(RuntimeError, _load_all_plugins) 
