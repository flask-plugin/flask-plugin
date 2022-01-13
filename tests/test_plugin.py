
import unittest

from src import PluginManager
from src import states

from .app import init_app


class TestPluginApp(unittest.TestCase):

    RequiredPluginInfoKey = ('name', 'id', 'name', 'status', 'info')
    
    def setUp(self) -> None:
        self.app = init_app('BaseDevelopmentConfig')
        self.client = self.app.test_client()
        self.manager: PluginManager = self.app.plugin_manager  # type: ignore
        for plugin in self.manager.plugins:
            self.manager.load(plugin)

    def start_all_plugins(self) -> None:
        for plugin in self.manager.plugins:
            self.manager.start(plugin)

    def stop_all_plugins(self) -> None:
        for plugin in self.manager.plugins:
            self.manager.stop(plugin)

    def unload_all_plugins(self) -> None:
        for plugin in self.manager.plugins:
            self.manager.unload(plugin)

    def test_index_api(self) -> None:
        data = self.client.get('/api').json
        self.assertNotEqual(data, None)
        assert data
        for plugin_info in data:
            for key in self.RequiredPluginInfoKey:
                self.assertIn(key, plugin_info)
            self.assertEqual(plugin_info['status'], states.PluginStatus.Loaded.name)

    def test_blueprint_no_routing(self) -> None:
        self.assertEqual(self.client.get('/plugins').status_code, 404)

    def test_loaded_plugin_not_working(self) -> None:
        self.assertEqual(self.client.get('/plugins/hello').status_code, 404)

    def test_loaded_plugin_not_added_url_map(self) -> None:
        for rule in self.app.url_map.iter_rules():
            self.assertNotIn(self.manager.domain, rule.rule)

    def test_started_plugin_endpoint(self) -> None:
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/endpoints/raise')
        self.assertEqual(response.status_code, 502)

    def test_started_plugin_html_rendering(self) -> None:
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/admin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'HELLO admin!')

    def test_started_plugin_static_file(self) -> None:
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/staticfile')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'HELLO!')

    def test_started_plugin_static_folder(self) -> None:
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/static/file.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'HELLO!')

    def test_started_plugin_url_for_and_redirect(self) -> None:
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/doge', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'HELLO Doge!')

    def test_started_plugin_error_handler(self) -> None:
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/403')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Hello Forbidden!')

    def test_started_other_plugin(self) -> None:
        self.start_all_plugins()
        response = self.client.get('/plugins/goodbye/admin')
        self.assertEqual(response.data, b'GOODBYE admin!')
        response = self.client.get('/plugins/goodbye/staticfile')
        self.assertEqual(response.data, b'GOODBYE!')
        response = self.client.get('/plugins/goodbye/static/file.txt')
        self.assertEqual(response.data, b'GOODBYE!')
        response = self.client.get('/plugins/goodbye/doge', follow_redirects=True)
        self.assertEqual(response.data, b'GOODBYE Doge!')
        response = self.client.get('/plugins/goodbye/403')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Goodbye Forbidden!')

    def test_stopped_one_plugin_404(self) -> None:
        self.start_all_plugins()
        hello = self.manager.find(domain='hello')
        assert hello
        self.manager.stop(hello)
        response = self.client.get('/plugins/hello/admin')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/plugins/goodbye/admin')
        self.assertEqual(response.data, b'GOODBYE admin!')

    def test_stopped_all_plugins_index_still_working(self):
        self.start_all_plugins()
        self.stop_all_plugins()
        data = self.client.get('/api').json
        self.assertNotEqual(data, None)

    def test_unload_plugins_clean_url_map(self):
        self.start_all_plugins()
        self.stop_all_plugins()
        self.unload_all_plugins()
        for rule in self.app.url_map.iter_rules():
            self.assertNotIn(self.manager.domain, rule.rule)

    def test_unload_plugin_clean_endpoints(self):
        hello = self.manager.find(domain='hello')
        self.start_all_plugins()
        self.assertIn('plugins.hello.raise', self.app.view_functions)
        self.stop_all_plugins()
        self.unload_all_plugins()
        self.assertNotIn('plugins.hello.raise', self.app.view_functions)
        if hello:
            self.assertEqual(len(hello.endpoints), 0)
