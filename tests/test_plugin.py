
import unittest
from os import path

from src import PluginManager, utils
from src import states
from src.plugin import Plugin

from .app import init_app
from . import create_empty_plugin


class TestPluginApp(unittest.TestCase):

    RequiredPluginInfoKey = ('name', 'id', 'name', 'status', 'info')

    def setUp(self) -> None:
        self.app = init_app('BaseDevelopmentConfig')
        self.client = self.app.test_client()
        self.manager: PluginManager = self.app.plugin_manager  # type: ignore
        
    def load_all_plugins(self) -> None:
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

    def test_invalid_plugin_endpoint(self) -> None:
        self.load_all_plugins()
        for plugin in self.manager.plugins:
            self.assertRaises(
                ValueError, lambda: plugin.add_url_rule('/', endpoint='a.b.c'))
            self.assertRaises(ValueError, lambda: plugin.endpoint('a.b.c'))

    def test_repr_plugin(self) -> None:
        self.load_all_plugins()
        for plugin in self.manager.plugins:
            self.assertEqual(repr(plugin), f'<Plugin registered at {plugin.domain} - {plugin.status.value.name}>')

    def test_index_api(self) -> None:
        self.load_all_plugins()
        data = self.client.get('/api').json
        self.assertNotEqual(data, None)
        assert data
        for plugin_info in data:
            for key in self.RequiredPluginInfoKey:
                self.assertIn(key, plugin_info)
            self.assertEqual(plugin_info['status'],
                             states.PluginStatus.Loaded.name)

    def test_blueprint_no_routing(self) -> None:
        self.load_all_plugins()
        self.assertEqual(self.client.get('/plugins').status_code, 404)

    def test_loaded_plugin_not_working(self) -> None:
        self.load_all_plugins()
        self.assertEqual(self.client.get('/plugins/hello').status_code, 404)

    def test_loaded_plugin_not_added_url_map(self) -> None:
        self.load_all_plugins()
        for rule in self.app.url_map.iter_rules():
            self.assertNotIn(self.manager.domain, rule.rule)

    def test_started_plugin_endpoint(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/endpoints/raise')
        self.assertEqual(response.status_code, 502)

    def test_started_plugins_endpoints_equal_view_function(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        for plugin in self.manager.plugins:
            perfix_endpoint = self.manager._config.blueprint + '.' + plugin.domain
            registered_endpoints = []
            for endpoint in self.app.view_functions:
                if endpoint.startswith(perfix_endpoint):
                    registered_endpoints.append(utils.startstrip(
                        endpoint, self.manager._config.blueprint + '.'))
            self.assertEqual(set(registered_endpoints), set(plugin.endpoints))

    def test_started_plugin_html_rendering(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/admin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'HELLO admin!')

    def test_started_plugin_static_file(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/staticfile')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'HELLO!')

    def test_started_plugin_static_folder(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/static/file.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'HELLO!')

    def test_started_plugin_url_for_and_redirect(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        response = self.client.get(
            '/plugins/hello/doge', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'HELLO Doge!')

    def test_started_plugin_error_handler(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        response = self.client.get('/plugins/hello/403')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Hello Forbidden!')

    def test_started_other_plugin(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        response = self.client.get('/plugins/goodbye/admin')
        self.assertEqual(response.data, b'GOODBYE admin!')
        response = self.client.get('/plugins/goodbye/staticfile')
        self.assertEqual(response.data, b'GOODBYE!')
        response = self.client.get('/plugins/goodbye/static/file.txt')
        self.assertEqual(response.data, b'GOODBYE!')
        response = self.client.get(
            '/plugins/goodbye/doge', follow_redirects=True)
        self.assertEqual(response.data, b'GOODBYE Doge!')
        response = self.client.get('/plugins/goodbye/403')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Goodbye Forbidden!')

    def test_started_only_endpoint_plugin(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        oe = self.manager.find(domain='oe')
        assert oe
        response = self.client.get('/plugins/oe/')
        self.assertEqual(response.data, b'index')

    def test_same_domain_as_manager_blueprint_plugin(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        sdab = self.manager.find(domain='plugins')
        assert sdab
        response = self.client.get('/plugins/plugins/test')
        self.assertEqual(response.data, b'same name works for test')

    def test_stopped_one_plugin_404(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        hello = self.manager.find(domain='hello')
        assert hello
        self.manager.stop(hello)
        response = self.client.get('/plugins/hello/admin')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/plugins/goodbye/admin')
        self.assertEqual(response.data, b'GOODBYE admin!')

    def test_stoppped_all_plugins_point_notfound(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        self.stop_all_plugins()
        for plugin in self.manager.plugins:
            plugin_endpoint = self.manager._config.blueprint + plugin.domain
            for endpoint in self.app.view_functions:
                if endpoint.startswith(plugin_endpoint):
                    self.assertEqual(
                        self.app.view_functions[endpoint], Plugin.notfound)

    def test_stopped_plugins_ednpoints_equal_view_function(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        self.stop_all_plugins()
        for plugin in self.manager.plugins:
            perfix_endpoint = self.manager._config.blueprint + '.' + plugin.domain
            registered_endpoints = []
            for endpoint in self.app.view_functions:
                if endpoint.startswith(perfix_endpoint):
                    registered_endpoints.append(utils.startstrip(
                        endpoint, self.manager._config.blueprint + '.'))
            self.assertSetEqual(set(registered_endpoints),
                                set(plugin.endpoints))

    def test_stopped_all_plugins_index_still_working(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        self.stop_all_plugins()
        data = self.client.get('/api').json
        self.assertNotEqual(data, None)

    def test_unload_plugins_clean_url_map(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        self.stop_all_plugins()
        self.unload_all_plugins()
        for rule in self.app.url_map.iter_rules():
            self.assertNotIn(self.manager.domain, rule.rule)

    def test_unload_plugins_has_no_endpoints(self) -> None:
        self.load_all_plugins()
        self.start_all_plugins()
        self.stop_all_plugins()
        self.unload_all_plugins()
        for plugin in self.manager.plugins:
            self.assertEqual(list(plugin.endpoints), [])

    def test_unload_plugin_clean_endpoints(self) -> None:
        self.load_all_plugins()
        hello = self.manager.find(domain='hello')
        assert hello
        self.start_all_plugins()
        self.stop_all_plugins()
        self.unload_all_plugins()
        plugin_endpoint = self.manager._config.blueprint + hello.domain
        for endpoint in self.app.view_functions:
            if endpoint.startswith(plugin_endpoint):
                self.fail(
                    f"'{endpoint}' still exists after '{plugin_endpoint}' unloaded")

    def test_invalid_plugin_domain(self):
        dirname = 'invalid-plugin-domain'
        create_empty_plugin(dirname, {
            'id': 'invalid-plugin-domain',
            'domain': 'test.test',
            'plugin': {
                'name': 'invalid-plugin-domain',
                'author': 'test',
                'summary': 'test.'
            },
            'releases': []
        })
        self.assertRaises(ValueError, self.load_all_plugins)
        utils.rmdir(path.join(self.manager.basedir, dirname))

    def test_lacking_plugin_config(self) -> None:
        dirname = 'lacking-plugin-json'
        create_empty_plugin(dirname)
        self.assertRaises(FileNotFoundError, self.load_all_plugins)
        utils.rmdir(path.join(self.manager.basedir, dirname))

    def test_empty_domain_plugin(self) -> None:
        dirname = 'empty-plugin-domain'
        create_empty_plugin(dirname, {
            'id': 'invalid-plugin-domain',
            'domain': '',
            'plugin': {
                'name': 'invalid-plugin-domain',
                'author': 'test',
                'summary': 'test.'
            },
            'releases': []
        })
        utils.rmdir(path.join(self.manager.basedir, dirname))
