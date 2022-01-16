
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
from .config import DefaultConfig, ConfigPrefix


class PluginManager:
    """
    PluginManager allows you to load, start, stop and unload plugin.

    After being bound with the Flask application, manager can automatically discover plugins 
    in configuration directory and record their status.
    
    Also, PluginManager provides a set of control functions to manage plugin.

    Config Items:

    - blueprint: will be applied as the name of the plug-in 
      blueprint and the corresponding ``url_prefix``.
    - directory: the plugins path relative to the application directory.
    - excludes_directory: directories that are skipped when scanning.

    If app not provided, you can use :py:meth:`.PluginManager.init_app` with your app
    to initialize and configure later.
    """

    def __init__(self, app: Flask = None) -> None:
        self._loaded: t.Dict[Plugin, str] = {}
        if not app is None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize manager, load configs, create and bind blueprint for plugin management.

        Blueprint named ``config.blueprint`` will be created and registered
        in ``app`` with argument ``url_prefix`` as same as ``config.blueprint``.
        
        Blueprint will have two functioncs registered as ``before_request`` and ``after_request``:

        - ``before_request``: using :py:meth:`.PluginManager.dynamic_select_jinja_loader` to set
          app global jinja_loader in ``app.jinja_env.loader`` to :py:meth:`.Plugin.jinja_loader`.
        - ``after_request``: restore ``app.jinja_env.loader`` to raw ``app.jinja_loader``.

        ``app.plugin_manager`` will be bind to reference of current manager, so it can
        be used with request context using ``current_app.plugin_manager``.

        Args:
            app (Flask): your flask application.
        """
        self._app = app
        self._config = config = self.load_config(app)

        # Register Bluprint for plugin
        url_prefix = '/' + config.blueprint.lstrip('/')
        self._blueprint = Blueprint(config.blueprint, __name__)

        # Replace and restore global `jinja_loader` in `app.jinja_env`
        @self._blueprint.before_request
        def _replace_jinja_loader():
            app.jinja_env.loader = self.dynamic_select_jinja_loader()
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

        # Register ``app.plugin_manager``
        app.plugin_manager = self  # type: ignore

    @staticmethod
    def dynamic_select_jinja_loader() -> t.Optional[FileSystemLoader]:
        """
        Dynamic switch plugin ``jinja_loader`` to replace ``app.jinja_env.loader``.
        
        If routing to an exist plugin, ``request.blueprints`` will be a list like:
        ``['plugins.PLUGIN_DOMAIN', 'plugins']``.

        So select first blueprint and using ``.lstrip(self._config.blueprint + '.')``
        to get current plugin domain.

        Then iter ``self._loaded`` plugins to find which domain are registered into it.
        And becasue ``Plugin`` inherit from ``Scaffold``, it can handle ``plugin.jinja_loader``
        correctly, just return it.

        It cannot use ``locked_cached_property`` because we hope template loader
        switch dynamically everytime.

        Returns:
            Optional[BaseLoader]: plugin.jinja_loader
        """
        # Obtaining ``app.plugin_manager`` object
        if hasattr(current_app, 'plugin_manager'):
            manager: 'PluginManager' = current_app.plugin_manager  # type: ignore
        else:
            return None

        # Check if accessing plugin domain
        names = request.blueprints
        if len(names) != 2:
            return None
        domain = utils.startstrip(names[0], manager._config.blueprint + '.')

        # Dynamic switch plugin ``jinja_loader``
        for plugin in manager._loaded:
            if plugin.domain == domain:
                return plugin.jinja_loader
        return None

    @property
    def status(self) -> t.List[t.Dict]:
        """
        Return all plugins status dict, calling :py:meth:`.Plugin.export_status_to_dict`.

        Returns:
            t.List[t.Dict]: all plugins status.
        """
        return [
            plugin.export_status_to_dict() for plugin in self.plugins
        ]

    @property
    def domain(self) -> str:
        """PluginMangaer domain bound to blueprint name and url_prefix."""
        return self._config.blueprint

    @property
    def plugins(self) -> t.Iterable[Plugin]:
        """
        Iter all plugins, including loaded and not loaded.

        Firstly iter all unloaded plugins using :py:meth:`.scan` for scanning
        unloaded plugins, then give a copy list of loaded plugins references.

        Returns:
            t.Iterable[Plugin]: plugin.
        """
        for plugin in chain(self.scan(), self._loaded.copy()):
            yield plugin

    def find(self, id_: str = None, domain: str = None, name: str = None) -> t.Optional[Plugin]:
        """
        Find a plugin.

        Args:
            id_ (str, optional): plugin id. Defaults to None.
            domain (str, optional): plugin domain. Defaults to None.
            name (str, optional): plugin name. Defaults to None.

        Returns:
            t.Optional[Plugin]: found plugin or None means no plugin found.
        """
        if not any((id_, domain, name)):
            return None
        for plugin in self.plugins:
            if plugin.id_ == id_ or plugin.domain == domain or plugin.name == name:
                return plugin
        return None

    def scan(self) -> t.Iterable[Plugin]:
        """
        Scan all unloaded plugin configured in ``config.directory``.

        After scanning and importing module as plugin, it will bind :py:obj:`.Plugin.basedir` to
        the dir name used for importing.

        Plugin module will be named by rule, 
        which gives hint to Flask for loading static files and templates:
        
        ``app.import_name + '.' + config.directory + '.' + plugin.basedir``.

        Yields:
            Iterator[t.Iterable[t.Tuple[Plugin, str]]]: couple :py:class:`.Plugin` with plugin dirname.
        """
        for directory in utils.listdir(
            os.path.join(self._app.root_path, self._config.directory),
            excludes=self._config.excludes_directory
        ):
            try:
                # Variable ``modname`` represents ``module.__name__`` which will be pass
                # into ``Plugin`` first parameter. Flask uses this variable for locating
                # ``Scaffold.root_path``, so it starts with ``self._config.direcotry``
                # and ends with plugin's direcorty name.
                basedir = os.path.basename(directory)
                if basedir in self._loaded.values():
                    continue

                # Define modname when load from app module
                modname = self._config.directory + '.' + basedir
                if self._app.import_name != '__main__':
                    modname = self._app.import_name + '.' + modname
                file = directory.rstrip('/') + '/__init__.py'

                # Load module using ``importlib``
                spec = imp.spec_from_file_location(modname, file)
                if not spec or not spec.loader:
                    raise ImportError('invalid direcotry.')
                module = imp.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if plugin module contains ``plugin`` variable
                if not hasattr(module, 'plugin'):
                    raise ImportError('module does not have plugin instance.')
            except (ImportError, FileNotFoundError) as error:
                if self._app.propagate_exceptions:
                    raise
                self._app.logger.warn(
                    f'failed import plugin: {os.path.basename(directory)} - {str(error.args[0])}'
                )
                continue

            # Bind ``basedir`` into plugin module
            module.plugin.basedir = basedir
            self._app.logger.info(f'imported plugin: {module.plugin.name}')
            yield module.plugin

    def load_config(self, app: Flask) -> utils.staticdict:
        """
        Load config from Flask app config.

        For configuration values not specified in ``app.config``, 
        default settings in :py:const:`config.DefaultConfig` will be used.

        All configs will also been update in ``app.config``.

        Args:
            app (Flask): Flask instance.

        Returns:
            utils.staticdict: loaded config.
        """
        config = {}
        for key in DefaultConfig:
            setting_key = ConfigPrefix.upper() + key.upper()
            config[key] = app.config.get(setting_key, DefaultConfig[key])
            app.config[setting_key] = config[key]
        return utils.staticdict(config)

    # Controllers
    def load(self, plugin: Plugin) -> None:
        """
        Load plugin.

        Raises:
            RuntimeError: when plugin status not allowed to load.
            RuntimeError: when found deplicated plugin id.
            RuntimeError: when plugin not scanned by :py:class:`.PluginManager`, 
                          which means have invalid attribute :py:obj:`.Plugin.basedir`.
        """
        plugin.status.assert_allow('load')

        # Check if duplicated plugin id
        if plugin.id_ in [_.id_ for _ in self._loaded]:
            raise RuntimeError(f'duplicated plugin id: {plugin.id_}')

        # Check if plugin scaned by manager
        if plugin.basedir is None:
            raise RuntimeError('cannot get plugin basedir')

        plugin.load(self._app, self._config)
        self._loaded[plugin] = plugin.basedir
        self._app.logger.info(f'loaded plugin: {plugin.name}')
        signals.loaded.send(self, plugin)

    def start(self, plugin: Plugin) -> None:
        """
        Start plugin.

        Raises:
            RuntimeError: when plugin status not allowed to start.
        """
        plugin.status.assert_allow('start')
        plugin.register(self._app, self._config)
        self._app.logger.info(f'started plugin: {plugin.name}')
        signals.started.send(self, plugin)

    def stop(self, plugin: Plugin) -> None:
        """
        Stop plugin.

        Raises:
            RuntimeError: when plugin status not allowed to stop.
        """
        plugin.status.assert_allow('stop')
        plugin.unregister(self._app, self._config)
        self._app.logger.info(f'stopped plugin: {plugin.name}')
        signals.stopped.send(self, plugin)

    def unload(self, plugin: Plugin) -> None:
        """
        Unload plugin.

        Raises:
            RuntimeError: when plugin status not allowed to unload.
        """
        plugin.status.assert_allow('unload')
        plugin.clean(self._app, self._config)
        self._loaded.pop(plugin)
        self._app.logger.info(f'unloaded plugin: {plugin.name}')
        signals.unloaded.send(self, plugin)
