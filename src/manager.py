
import importlib.util as imp
from itertools import chain
import os.path
import typing as t

from flask import Flask
from flask import Blueprint
from flask import current_app
from flask.globals import request
from jinja2.loaders import FileSystemLoader

from . import utils
from . import signals
from .plugin import Plugin


class PluginManager:
    """After being bound with the Flask application, 
    the plugin manager can automatically discover the plugins 
    in the configuration directory and record their status.
    At the same time, the manager provides a set of control 
    functions to control the state of the plug-in.

    Config Items:
        blueprint - will be applied as the name of the plug-in 
                    blueprint and the corresponding url_prefix.
        directory - the path relative to the application directory,
                    used to store the plug-in.
        excludes_directory - directories that are skipped when scanning.
    """

    DefaultConfig: t.Dict[str, t.Any] = utils.staticdict({
        'blueprint': 'plugins',
        'directory': 'plugins',
        'excludes_directory': [
            '__pycache__'
        ]
    })

    ConfigPrefix = 'plugins_'

    def __init__(self, app: Flask = None) -> None:
        self._loaded: t.Dict[Plugin, str] = {}
        if not app is None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self._app = app
        self._config = config = self._load_config(app)

        # Register Bluprint for plugin
        url_prefix = '/' + config.blueprint.lstrip('/')
        self._blueprint = Blueprint(config.blueprint, __name__)

        # Replace and restore global `jinja_loader` in `app.jinja_env`
        @self._blueprint.before_request
        def _replace_jinja_loader():
            app.jinja_env.loader = self._dynamic_select_jinja_loader()
            searchpath = app.jinja_env.loader.searchpath if app.jinja_env.loader else ''
            app.logger.debug(
                f'switched into plugin jinja loader: {searchpath}')

        @self._blueprint.after_request
        def _restore_jinja_loader(response):
            app.jinja_env.loader = app.jinja_loader
            searchpath = app.jinja_loader.searchpath if app.jinja_loader else ''
            app.logger.debug(f'switched to app jinja loader: {searchpath}')
            return response

        # Register blueprint into app
        app.register_blueprint(self._blueprint, url_prefix=url_prefix)

        # Register `app.plugin_manager`
        app.plugin_manager = self  # type: ignore

    @staticmethod
    def _dynamic_select_jinja_loader() -> t.Optional[FileSystemLoader]:
        """Replace raw `app.jinja_env.loader`.
        If routing to an exist plugin, `request.blueprints` will be list like:
            ```
            ['plugins.PLUGIN_DOMAIN', 'plugins']
            ```
        So select first blueprint and using `.lstrip(self._config.blueprint + '.')`
        to get current plugin domain.
        Then iter `self._loaded` plugins to find which domain are registered into it.
        And becasue `Plugin` inherit from `Scaffold`, it can handle `plugin.jinja_loader`
        correctly, just return it.

        It cannot use `locked_cached_property` because we hope template loader
        switch dynamically everytime.

        Returns:
            Optional[BaseLoader]: plugin.jinja_loader
        """
        # Obtaining `app.plugin_manager` object
        if hasattr(current_app, 'plugin_manager'):
            manager: 'PluginManager' = current_app.plugin_manager  # type: ignore
        else:
            return None

        # Check if accessing plugin domain
        names = request.blueprints
        if len(names) != 2:
            return None
        domain = names[0].replace(manager._config.blueprint + '.', '')

        # Dynamic switch plugin `jinja_loader`
        for plugin in manager._loaded:
            if plugin.domain == domain:
                return plugin.jinja_loader
        return None

    @property
    def status(self) -> t.List[t.Dict]:
        return [
            plugin.export_status_to_dict() for plugin in self.plugins
        ]

    @property
    def domain(self) -> str:
        return self._config.blueprint

    @property
    def plugins(self) -> t.Iterable[Plugin]:
        """Iter all plugins.
        Firstly iter all loaded plugins, then use `self._scan` for scanning
        unloaded plugins and check if `self._config.auto_load` enabled.
        If `self._config.auto_start` enabled, it will try to start plugin automatically.

        Returns:
            t.Iterable[Plugin]: plugins.
        """
        for plugin in chain(self.scan(), self._loaded.copy()):
            yield plugin

    def find(self, id_: str = None, domain: str = None, name: str = None) -> t.Optional[Plugin]:
        if not any((id_, domain, name)):
            return None
        for plugin in self.plugins:
            if plugin.id_ == id_ or plugin.domain == domain or plugin.name == name:
                return plugin
        return None

    def scan(self) -> t.Iterable[Plugin]:
        """Scan dir configures in `config.directory`, if directory name previous
        loaded, which means dirname found in self._plugins registry, it will skip
        module loading. Otherwise, it will load and check if module contains
        `plugin` attribute, if it contains, yield the plugin instance with dirname,
        if not, continue scanning process.

        Yields:
            Iterator[t.Iterable[t.Tuple[Plugin, str]]]: couple `Plugin` with plugin dirname.
        """
        for directory in utils.listdir(
            os.path.join(self._app.root_path, self._config.directory),
            excludes=self._config.excludes_directory
        ):
            try:
                # Variable `modname` represents `module.__name__` which will be pass
                # into `Plugin` first parameter. Flask uses this variable for locating
                # `Scaffold.root_path`, so it starts with `self._config.direcotry`
                # and ends with plugin's direcorty name.
                basedir = os.path.basename(directory)
                if basedir in self._loaded.values():
                    continue

                # Define modname when load from app module
                modname = self._config.directory + '.' + basedir
                if self._app.import_name != '__main__':
                    modname = self._app.import_name + '.' + modname
                file = directory.rstrip('/') + '/__init__.py'

                # Load module using `importlib`
                spec = imp.spec_from_file_location(modname, file)
                if not spec or not spec.loader:
                    raise ImportError('invalid direcotry.')
                module = imp.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if plugin module contains `plugin` variable
                if not hasattr(module, 'plugin'):
                    raise ImportError('module does not have plugin instance.')
            except (ImportError, FileNotFoundError) as error:
                if self._app.propagate_exceptions:
                    raise
                self._app.logger.warn(
                    f'failed import plugin: {os.path.basename(directory)} - {str(error.args[0])}'
                )
                continue

            # Bind `basedir` into plugin module
            module.plugin.basedir = basedir
            self._app.logger.info(f'imported plugin: {module.plugin.name}')
            yield module.plugin

    def _load_config(self, app: Flask) -> utils.staticdict:
        """Load config from Flask app config.
        For configuration values not specified in `app.config`, 
        default settings in `Manager.DefaultConfig` will be used.
        All configs will also been update in `app.config`.

        Args:
            app (Flask): Flask instance.

        Returns:
            utils.staticdict: loaded config.
        """
        config = {}
        for key in self.DefaultConfig:
            setting_key = self.ConfigPrefix.upper() + key.upper()
            config[key] = app.config.get(setting_key, self.DefaultConfig[key])
            app.config[setting_key] = config[key]
        return utils.staticdict(config)

    # Controllers
    def load(self, plugin: Plugin) -> None:
        plugin.status.assert_allow('load')

        # Check if duplicated plugin id
        if plugin in self._loaded:
            raise RuntimeError(f'duplicated plugin id: {plugin.id_}')

        # Check if plugin scaned by manager
        if plugin.basedir is None:
            raise RuntimeError('cannot get plugin basedir')

        plugin.load(self._app, self._config)
        self._loaded[plugin] = plugin.basedir
        self._app.logger.info(f'loaded plugin: {plugin.name}')
        signals.loaded.send(self, plugin)

    def start(self, plugin: Plugin) -> None:
        plugin.status.assert_allow('start')
        plugin.register(self._app, self._config)
        self._app.logger.info(f'started plugin: {plugin.name}')
        signals.started.send(self, plugin)

    def stop(self, plugin: Plugin) -> None:
        plugin.status.assert_allow('stop')
        plugin.unregister(self._app, self._config)
        self._app.logger.info(f'stopped plugin: {plugin.name}')
        signals.stopped.send(self, plugin)

    def unload(self, plugin: Plugin) -> None:
        plugin.status.assert_allow('unload')
        plugin.clean(self._app, self._config)
        self._loaded.pop(plugin)
        self._app.logger.info(f'unloaded plugin: {plugin.name}')
        signals.unloaded.send(self, plugin)
