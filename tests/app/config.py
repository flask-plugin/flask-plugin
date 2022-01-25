
class BaseDevelopmentConfig:
    DEBUG = True
    TESTING = True
    PLUGINS_BLUEPRINT = 'plugins'
    PLUGINS_DIRECTORY = 'plugins'
    PLUGINS_EXCLUDES_DIRECTORY = [
        '__pycache__',
        'should-not-be-imported',
        'lacking-plugin-json',
        'invalid-plugin-domain',
        'empty-plugin-domain',
        'duplicated-plugin-id'
    ]


class InvalidPluginImportConfig(BaseDevelopmentConfig):
    PLUGINS_EXCLUDES_DIRECTORY = [
        '__pycache__',
        'lacking-plugin-json',
        'invalid-plugin-domain',
        'empty-plugin-domain',
        'duplicated-plugin-id'
    ]

class LackingPluginJsonConfig(BaseDevelopmentConfig):
    PLUGINS_EXCLUDES_DIRECTORY = [
        '__pycache__',
        'should-not-be-imported',
        'invalid-plugin-domain',
        'empty-plugin-domain',
        'duplicated-plugin-id'
    ]

class InvalidPluginDomain(BaseDevelopmentConfig):
    PLUGINS_EXCLUDES_DIRECTORY = [
        '__pycache__',
        'should-not-be-imported',
        'lacking-plugin-json',
        'empty-plugin-domain',
        'duplicated-plugin-id'
    ]

class EmptyPluginDomain(BaseDevelopmentConfig):
    PLUGINS_EXCLUDES_DIRECTORY = [
        '__pycache__',
        'should-not-be-imported',
        'lacking-plugin-json',
        'invalid-plugin-domain',
        'duplicated-plugin-id'
    ]

class DuplicatedPluginId(BaseDevelopmentConfig):
    PLUGINS_EXCLUDES_DIRECTORY = [
        '__pycache__',
        'should-not-be-imported',
        'lacking-plugin-json',
        'invalid-plugin-domain',
        'empty-plugin-domain'
    ]

class NonExistDirectoryConfig(BaseDevelopmentConfig):
    PLUGINS_DIRECTORY = 'non_exist_plugin_directory'
