
import unittest

from .app import config, init_app


class TestBaseApp(unittest.TestCase):

    # Methods defined
    def assertHasAttr(self, obj, attrname, message=None):
        if not hasattr(obj, attrname):
            if message is not None:
                self.fail(message)
            else:
                self.fail(
                    'lacking an attribute. obj: %s, intendedAttr: %s'.format(obj, attrname))

    def setUp(self) -> None:
        self.app = init_app('BaseDevelopmentConfig')
        self.config = config.BaseDevelopmentConfig

    # Tests test fixture env
    def test_testing_mode_enabled(self) -> None:
        self.assertEqual(self.app.config['TESTING'], True)

    def test_load_config_plugin_manager(self) -> None:
        self.assertEqual(
            self.app.config['PLUGINS_BLUEPRINT'], self.config.PLUGINS_BLUEPRINT)
        self.assertEqual(
            self.app.config['PLUGINS_DIRECTORY'], self.config.PLUGINS_DIRECTORY)
        self.assertEqual(
            self.app.config['PLUGINS_EXCLUDES_DIRECTORY'], self.config.PLUGINS_EXCLUDES_DIRECTORY)

    def test_app_has_template_directory(self) -> None:
        self.assertEqual(self.app.template_folder, 'templates')
