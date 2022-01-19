# Plugin Manager

Plugin Manager provides an interface to help you easily manage all your plugins.

## Config

Plugin manager is configured with Flask.

- `plugins_blueprint`: The plugin manager will register a Blueprint on the Flask App to manage the plugin. This configuration value will be used to name the Blueprint and is also the `url_prefix` value for the Blueprint.
- `plugins_direcotry`: Your plug-in set directory, relative to the project startup path.
- `plugins_excludes_directory`: Within the plug-in set directories, there are some directories that you may want to exclude, which do not contain valid plug-in information, or that have other uses; just add their names within this list of configuration items.

You don't have to provide all the configuration, when Flask-Plugin cannot find the above configuration inside the bound App, it will load a default configuration, which is defined here: :py:obj:`.config.DefaultConfig`。

About how to configure Flask, see: https://flask.palletsprojects.com/en/2.0.x/config/

## Create and bind to a Flask app

Once your application is configured, bind it to a :py:class:`.PluginManager` instance to:

```python
from flask import Flask
from flask_plugin import PluginManager

app = Flask(__name__)
manager = PluginManager(app)
```

Of course you can also create a manager first and then bind your application later:

```python
manager = PluginManager()
app = Flask(__name__)
manager.init_app(app)
```

Once the application is bound, the instance of the manager bound to the application can be accessed through `app.plugin_manager`.

The `current_app` proxy also contains its references.

## Auto-discovery of plugins

Once the application binding is complete, you can access all plugins using :py:attr:`.PluginManager.plugins`. This attribute will automatically discover all instances of unloaded plugins, followed by instances of loaded plugins at

```python
for plugin in manager.plugins:
    ...
```

If you want to manually scan all plug-in directories, you can call the :py:meth:`.PluginManager.scan` method, which will iterate over all unloaded plug-in instances (but usually you don't need to do this).

When the specified plugin directory is inaccessible, the method raises a `FileNotFoundError`。

## Plugin Control

After you get the plugin instance, you can use methods :py:meth:`.PluginManager.load`, :py:meth:`.PluginManager.start`, :py:meth:`.PluginManager.stop`, :py:meth:`.PluginManager.unload` to control plugin.

Methods above accept a :py:class:`.Plugin` instance. It will check if the current state of the plugin allows the transfer operation first, and when the operation is prohibited it will raise a `RuntimeError`.

## Get Plugins Info

If you want to get the status information of all plugins at once, the :py:attr:`.PluginManager.status` can help you to call all plugins (including unloaded) of the :py:meth:`.Plugin.export_status_to_dict` and return as a list:

```python
>>> manager.status
[{'domain': 'flaskex',
  'id': '334c997a6c4946aaa920f2ffccc27077',
  'info': {'author': '', 'description': '', 'version': (0, 0, 0)},
  'name': 'flaskex',
  'status': 'Unloaded'},
 {'domain': 'hello',
  'id': '347336b4fcdd447985aec57f2bc5793c',
  'info': {'author': '', 'description': '', 'version': (0, 0, 0)},
  'name': 'Greeting',
  'status': 'Unloaded'}]
```
