
class BaseDevelopmentConfig:
    DEBUG = True
    TESTING = True
    PLUGINS_BLUEPRINT = 'plugins'
    PLUGINS_DIRECTORY = 'plugins'
    PLUGINS_EXCLUDES_DIRECTORY = [
        '__pycache__',
        'should_not_be_imported'
    ]


class InvalidPluginImportConfig(BaseDevelopmentConfig):
    PLUGINS_EXCLUDES_DIRECTORY = [
        '__pycache__'
    ]


class NonExistDirectoryConfig(BaseDevelopmentConfig):
    PLUGINS_DIRECTORY = 'non_exist_plugin_directory'
