
import importlib.util as imp
import os.path
import typing as t

from flask import Flask
from flask import Blueprint

from . import utils
from .plugin import Plugin, PluginStatus


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

    def __init__(self, app: Flask = None) -> None:
        self._loaded: t.Dict[Plugin, str] = dict()
        if not app is None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self._app = app
        self._config = config = self._load_config(app)

        # Register Bluprint for plugin
        url_prefix = '/' + config.blueprint.lstrip('/')
        self._blueprint = Blueprint(config.blueprint, __name__)
        app.register_blueprint(
            self._blueprint, url_prefix=url_prefix, template_folder='template')

        # Register `app.plugin_manager`
        app.plugin_manager = self  # type: ignore

    @property
    def status(self) -> t.List[t.Dict]:
        return [
            plugin.export_status_to_dict() for plugin in self.plugins
        ]

    @property
    def plugins(self) -> t.Iterable[Plugin]:
        """Iter all plugins.
        Firstly iter all loaded plugins, then use `self._scan` for scanning
        unloaded plugins and check if `self._config.auto_load` enabled.
        If `self._config.auto_start` enabled, it will try to start plugin automatically.

        Returns:
            t.Iterable[Plugin]: plugins.
        """
        for plugin in self._loaded:
            yield plugin
        for plugin in self.scan():
            yield plugin

    def find(self, id_: str = None, domain: str = None, name: str = None) -> t.Optional[Plugin]:
        if not any((id_, domain, name)):
            return None
        for plugin in self.plugins:
            if plugin.id_ == id_ or plugin.domain == domain or plugin.name == name:
                return plugin

    def scan(self) -> t.Iterable[Plugin]:
        """Scan dir configures in `config.directory`, if directory name previous
        loaded, which means dirname found in self._plugins registry, it will skip
        module loading. Otherwise, it will load and check if module contains
        `plugin` attribute, if it contains, yield the plugin instance with dirname,
        if not, continue scanning process.

        Yields:
            Iterator[t.Iterable[t.Tuple[Plugin, str]]]: couple `Plugin` instance with plugin dirname.
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
                modname = self._config.directory + '.' + basedir
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
            except ImportError:
                continue

            # Bind `basedir` into plugin module
            module.plugin.basedir = basedir
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
        config = dict()
        for key in self.DefaultConfig:
            config[key] = app.config.get(key.upper(), self.DefaultConfig[key])
            app.config[key] = config[key]
        return utils.staticdict(config)

    # Controllers
    def load(self, plugin: Plugin) -> None:
        if not plugin.status == PluginStatus.Unloaded:
            return

        # Check if duplicated plugin id
        if plugin in self._loaded:
            raise RuntimeError(f'duplicated plugin id: {plugin.id_}')

        # Check if plugin scaned by manager
        if plugin.basedir is None:
            raise RuntimeError('cannot get plugin basedir.')

        plugin.load(self._app, self._config)
        self._loaded[plugin] = plugin.basedir

    def start(self, plugin: Plugin) -> None:
        if not plugin.status in (PluginStatus.Loaded, PluginStatus.Stopped):
            return
        plugin.register(self._app, self._config)

    def stop(self, plugin: Plugin) -> None:
        if not plugin.status == PluginStatus.Running:
            return
        plugin.unregister(self._app, self._config)

    def unload(self, plugin: Plugin) -> None:
        if not plugin.status in (PluginStatus.Stopped, PluginStatus.Loaded):
            return
        plugin.clean(self._app, self._config)
        self._loaded.pop(plugin)
