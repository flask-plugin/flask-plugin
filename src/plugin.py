
import inspect
import typing as t

import flask.typing as ft
from flask import abort
from flask.app import Flask
from flask.scaffold import Scaffold
from flask.wrappers import Response

from . import utils
from . import states


class Plugin(Scaffold):
    """Users can create their own plugin by instantiating this class. 
    After binding with the Flask application, 
    the instance will be automatically discovered by the manager.
    The `Plugin` class inherits from the `Scaffold` class, 
    and its working principle is roughly similar to `Blueprint`, 
    but the difference is that the `Plugin` class implements dynamic routing management.
    """

    id_ = utils.property_('id', type_=str)
    domain = utils.property_('domain', type_=str)
    info = utils.property_('info', type_=utils.attrdict)
    basedir = utils.property_('basedir', type_=str, writable=True)

    def __init__(
        self,

        # Plugin parameters
        id_: str,
        name: str,
        domain: str,
        author: str = '',
        description: str = '',
        version: t.Tuple[int, int, int] = (0, 0, 0),

        # Same parameters for Scaffold
        import_name: str = None,
        static_folder: str = None,
        static_url_path: str = None,
        template_folder: str = None,
        root_path: str = None
    ) -> None:
        """
        Args:
            id_ (str): using for identify and search plugin, is recommended to use 
            `uuid` to generate a fixed and unique id for your plugin.

            domain (str): scope of the plug-in determines the path through 
            which the plug-in can be accessed, your plugin will be accessible in 
            `f'/{PluginManager.config.blueprint}/{Plugin.domain}/#view_func`

            Below are plugin info for end-user:
                name (str, optional): plugin name. Defaults to ''.
                author (str, optional): author of plugin, email or name. Defaults to ''.
                description (str, optional): a brief explanation for your plugin. Defaults to ''.
                version (t.Tuple[int, int, int], optional): version tuple. Defaults to (0, 0, 0).

            These parameters as same as initializing `flask.Flask`:
                import_name (str, optional): plugin will inspect your module `__name__`, 
                but unless you have other reasons, please use `__name__` as the parameter 
                value when registering the plug-in, otherwise don't pass it in. Defaults to None.

                static_folder (str, optional): static resource directory. Defaults to None.

                static_url_path (str, optional): static url path. Defaults to None.

                root_path (str, optional): when you initialize the plugin with 
                a not `__name__` parameter `import_name`, you should pass this 
                parameter as your plugin directory, because flask will unable to 
                locate your plugin. Defaults to None.

        Raises:
            ValueError: if we could not use `inspect` to get valid module `__name__`
            it will raise `ValueError`.
        """

        # Get caller stack info and module using `inspect` module.
        if not import_name:
            import_name = inspect.stack()[1][0].f_locals.get('__name__')
            if not import_name or not '.' in import_name:
                raise ValueError('cannot inspect module name.')

        self._id, self._basedir = id_, None
        self.status = states.StateMachine(states.TransferTable)
        self._domain = domain if domain else self._make_domain_by_name(name)
        if '.' in self._domain:
            raise ValueError("plugin 'domain' cannot contain '.'")
        if not domain:
            raise ValueError("empty puugin 'domain' not allowed")

        # Editable information dict for end-user
        self._info = utils.attrdict({
            'author': author,
            'version': version,
            'description': description
        })

        # Deferred function, executing when registering into Manager
        self._register: t.List[t.Callable[[
            Flask, utils.staticdict], None]] = []
        self._unregister: t.List[t.Callable[[
            Flask, utils.staticdict], None]] =[]
        self._clean: t.Dict[str, t.Callable[[
            Flask, utils.staticdict], None]] = {}
        self._endpoints = set()

        # Initialize Scaffold
        super().__init__(import_name, static_folder=static_folder,
                         static_url_path=static_url_path, root_path=root_path,
                         template_folder=template_folder)
        self.name = name

        # Add static file sending support
        if static_folder:
            self.add_url_rule(
                f'{self.static_url_path}/<path:filename>',
                endpoint='static',
                view_func=self.send_static_file
            )

        # Add context handlers manager
        context_handlers_and_preprocessors = {
            'before_request': 'before_request_funcs',
            'after_request': 'after_request_funcs',
            'teardown_request': 'teardown_request_funcs',
            'context_processor': 'template_context_processors',
            'url_value_preprocessor': 'url_value_preprocessors',
            'url_defaults': 'url_default_functions'
        }
        for handler_name, target in context_handlers_and_preprocessors.items():
            self._decorable_setter(handler_name, prefix='_prepared_handlers_')
            self._manage_context_handlers_and_processors(
                handler_name, target, prefix='_prepared_handlers_')

    def __repr__(self) -> str:
        return f'<Plugin registered at {self._domain} - {self.status.value.name}>'

    def __hash__(self) -> int:
        return hash(self._id)

    @property
    def endpoints(self) -> t.Set[str]:
        """When `Plugin.status` is `PluginStatus.Unloaded`, means plugin not loaded
        endpoints refers to empty set.
        Once loaded plugins, return all registered endpoints.

        Returns:
            t.Set[str]: all endpoints.
        """
        if self.status.value == states.PluginStatus.Unloaded:
            return set()
        return self._endpoints

    @staticmethod
    def _make_domain_by_name(name: str) -> str:
        """Using plugin name when user did not provide domain,
        although is NOT encouraged. It will replace any non-alphabet characters
        to '_'.

        Args:
            name (str): raw plugin name

        Returns:
            str: valid endpoint name
        """
        return ''.join(
            map(lambda c: c if c.isalpha() else '_', name)
        )

    @staticmethod
    def notfound(*args, **kwargs) -> Response:
        """When we stopped or removed a plugin, followed mapping from urls to endpoints
        should be removed also. However, after binding url to `werkzeug.routing.Map`, we
        need to call `werkzeug,routing.Map.remap` for remapping, it will re-compile all
        Regex instances, which will also caused huge performance cost.
        So here is a more elegant and easier way:
        Just remap these endpoints to an 'invalid' function which will directly call
        `flask.abort(404)`.

        Returns:
            Response: 404 Not Found.
        """
        abort(404)

    def _decorable_setter(self, name: str, prefix: str):
        """Set getattr(self, `prefix + attr`) to empty list for storaging functions,
        and set correspoding attributes like decorators.
        """
        setattr(self, prefix + name, [])
        setattr(self, name, lambda value: getattr(
            self, prefix + name).append(value))

    def _record_clean_function(
        self, key: str, function:
        t.Callable[[Flask, utils.staticdict], None]
    ) -> None:
        """Unlike register and unregister functions executed every time route changes,
        clean functions should just run once. So using a dict for record key and function,
        if key exists in `self._clean`, just skip adding - like `Blueprint.record_once`.

        Args:
            key (str): record function key.
            function (t.Callable[[Flask, utils.staticdict], None]): clean function.
        """
        if not key in self._clean:
            self._clean[key] = function

    def add_url_rule(
            self, rule: str,
            endpoint: str = None,
            view_func: t.Callable = None,
            provide_automatic_options: t.Optional[bool] = None,
            **options: t.Any
    ) -> None:
        if endpoint and "." in endpoint:
            raise ValueError("'endpoint' may not contain a dot '.' character.")

        # Add url rule locally
        if endpoint is None:
            assert view_func is not None, "expected view func if endpoint is not provided."
            endpoint = view_func.__name__
        endpoint = self._domain + '.' + endpoint
        self._endpoints.add(endpoint)

        # Deferred functions
        def _register_url_rule(app: Flask, config: utils.staticdict) -> None:
            full_url = '/' + config.blueprint + '/' + self._domain + rule
            full_endpoint = config.blueprint + '.' + endpoint
            if full_endpoint in app.view_functions and view_func:
                app.view_functions[full_endpoint] = view_func
            else:
                app.add_url_rule(full_url, config.blueprint + '.' + endpoint, view_func,
                                 provide_automatic_options, **options)

        def _unregister_url_rule(app: Flask, config: utils.staticdict) -> None:
            if config.blueprint + '.' + endpoint in app.view_functions:
                app.view_functions[
                    config.blueprint + '.' + endpoint] = self.notfound

        def _clean_url_rule(app: Flask, config: utils.staticdict) -> None:
            # Remove URL Rule from `app.url_map`
            def _belong_to_plugin(rule):
                return rule.endpoint.replace(config.blueprint + '.', '') in self._endpoints
            filtered = map(
                lambda url_rule: url_rule.empty(), filter(
                    lambda url_rule: not _belong_to_plugin(url_rule),
                    app.url_map.iter_rules()
                )
            )
            app.url_map = app.url_map_class(filtered)

        def _clean_view_function(app: Flask, config: utils.staticdict) -> None:
            # Endpoints cleaner should be call here, againist user just used
            # `self.endpoint` registered functions
            for endpoint in app.view_functions.copy():
                if endpoint.startswith(config.blueprint + '.' + self._domain):
                    app.view_functions.pop(endpoint)
            self._endpoints.clear()

        self._register.append(_register_url_rule)
        self._unregister.append(_unregister_url_rule)
        self._record_clean_function('clean_url_rule', _clean_url_rule)
        self._record_clean_function('clean_view_function', _clean_view_function)

    def endpoint(self, endpoint: str) -> t.Callable:
        """Decorate a view function to register it for the given
        endpoint. Used if a rule is added without a `view_func` with
        `Plugin.add_url_rule`.

        Args:
            endpoint (str): endpoint name

        Returns:
            t.Callable: decorated function
        """
        if endpoint and "." in endpoint:
            raise ValueError("'endpoint' may not contain a dot '.' character.")

        def _decorator(function: t.Callable):
            self._endpoints.add(endpoint)

            # Deferred functions
            def _register_view_function(app: Flask, config: utils.staticdict) -> None:
                self._endpoints.add(endpoint)
                app.endpoint(
                    '.'.join([config.blueprint, self._domain, endpoint]))(function)

            def _unregister_view_function(app: Flask, config: utils.staticdict) -> None:
                app_view_endpoint = '.'.join(
                    [config.blueprint, self._domain, endpoint])
                app.view_functions[app_view_endpoint] = self.notfound

            def _clean_view_function(app: Flask, config: utils.staticdict) -> None:
                for endpoint in app.view_functions.copy():
                    if endpoint.startswith(config.blueprint + '.' + self._domain):
                        app.view_functions.pop(endpoint)
                self._endpoints.clear()

            self._register.append(_register_view_function)
            self._unregister.append(_unregister_view_function)
            self._record_clean_function(
                'clean_view_function', _clean_view_function)

            return function
        return _decorator

    def register_error_handler(
        self, code_or_exception: t.Union[t.Type[ft.GenericException], int],
        f: "ft.ErrorHandlerCallable[ft.GenericException]"
    ) -> None:

        # Same as `Scaffold.register_error_handler`
        try:
            exc_class, code = self._get_exc_class_and_code(code_or_exception)
        except KeyError:
            raise KeyError(
                f"'{code_or_exception}' is not a recognized HTTP error"
                " code. Use a subclass of HTTPException with that code"
                " instead."
            ) from None

        # Register and clean deferred functions.
        def _register_error_handler(app: Flask, config: utils.staticdict) -> None:
            endpoint = config.blueprint + '.' + self._domain
            app.error_handler_spec[endpoint][code][exc_class] = t.cast(
                "ft.ErrorHandlerCallable[Exception]", f)

        def _clean_error_handler(app: Flask, config: utils.staticdict) -> None:
            endpoint = config.blueprint + '.' + self._domain
            if endpoint in app.error_handler_spec:
                app.error_handler_spec.pop(endpoint)

        self._register.append(_register_error_handler)
        self._record_clean_function(
            'clean_error_handler', _clean_error_handler)

    def _manage_context_handlers_and_processors(
            self, name: str, target: str, prefix: str = '_handler_') -> None:
        """Manage register and unregister deferred behaviours for context related functions.
        In flask we could use: `before_request`, `after_request` and `teardown_request` for 
        adding action inner context.
        These context handler functions storage at `app.before_request_funcs`, 
        `app.after_request_funcs` and `app.teardown_request_funcs`.
        Here add deferred function to check if handlers above set in `Plugin` instance. if so,
        add/remove it.
        Processor and preprocessor can also been set this way, they are: `context_processor`,
        `url_value_preprocessor` and `url_defaults`.

        Args:
            name (str): context handler name, like `'before_request'`
            target (str): attribute name going to be used in `Flask`, e.g. `before_request_funcs`
            prefix (str, optional): prefix adding before variable of storing context handler.
                Defaults to '_handler_'.
        """

        def _register_context_handler(app: Flask, config: utils.staticdict) -> None:
            endpoint = config.blueprint + '.' + self._domain
            handlers = getattr(self, prefix + name, None)
            if handlers and isinstance(handlers, list):
                getattr(app, target).setdefault(
                    endpoint, []).append(getattr(self, prefix + name).pop())

        def _clean_context_handler(app: Flask, config: utils.staticdict) -> None:
            endpoint = config.blueprint + '.' + self._domain
            if endpoint in getattr(app, target):
                getattr(app, target).pop(endpoint)

        self._register.append(_register_context_handler)
        self._record_clean_function(
            'clean_context_handler', _clean_context_handler)

    def export_status_to_dict(self) -> t.Dict:
        return {
            'id': self._id,
            'name': self.name,
            'status': self.status.value.name,
            'domain': self._domain,
            'info': dict(self._info)
        }

    def _is_setup_finished(self) -> bool:
        return False

    # Controllers
    def load(self, app: Flask, config: utils.staticdict) -> None:
        self.status.value = states.PluginStatus.Loaded

    def register(self, app: Flask, config: utils.staticdict) -> None:
        for defferd in self._register:
            defferd(app, config)
        self.status.value = states.PluginStatus.Running

    def unregister(self, app: Flask, config: utils.staticdict) -> None:
        for defferd in self._unregister:
            defferd(app, config)
        self.status.value = states.PluginStatus.Stopped

    def clean(self, app: Flask, config: utils.staticdict) -> None:
        for _key, function in self._clean.items():
            function(app, config)
        self.status.value = states.PluginStatus.Unloaded
