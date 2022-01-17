# Plugin Development

## Create

Creating a plugin with Flask-Plugin is easy. Just follow these steps:

1. Create a new plugin-set folder (if you dont have one), which is used to store all your plugins; the name of this folder needs to be the same as `directory` in config :py:obj:`.config.DefaultConfig`.

   *If you did not configure it, the default directory name should be plugins.*

2. Create a new directory for your plugin in the plugin-set folder; if there's nothing wrong with it, let its name be the same as the name of your plugin.

3. In the example below, we are going to use `template` and `static` for template and static resource folder, so create these folder inside your plugin folder.

4. Create `__init__.py`, and a instance of :py:class:`.Plugin` named `plugin` like this：

   ```python
   from flask_plugin import Plugin
   
   plugin = Plugin(
       id_='Your Plugin ID',
       domain='Your Plugin Domain', 
       name='Your Plugin Name',
       static_folder='static',
       template_folder='template'
   )
   ```

And that's done!

But if you have more complex needs, you could give more parameters when instantiating the :py:class:`.Plugin` class. All parameters can be devided into three groups:

1. Basic plugin info
   - `id_`: plugin id, for identifying and searching.
   - `domain`: plugin's domain. If you are using `flaskex`, then you could access your plugin in `/plugins/flaskex`.
   - `name`: plugin name.
2. Info for Flask (Optional)
   - `static_folder`: the static resource folder of the plugin, relative to the directory of this plugin.
   - `template_forlder`: the template folder of the plugin, relative to the plugin directory.
   - `static_url_path`: url path of static resource.
   - `import_name`: this parameter used for loacating directory of plugin, defaults to `__name__`, generally not required. If provided this parameter, please also provide the `root_path`.
   - `root_path`: the directory of plugin relative to application startup path, generally noy required.
3. Plugin extensions
   - `author`: author of plugin.
   - `description`: a short description of plugin.
   - `version`: a triplet array gives version of plugin. Like `(0, 0, 1)`

## Usage

The use of the plugin is much the same as `Blueprint`, and anything you can do with Blueprint can also be done here.

```python
@plugin.route('/', methods=['GET'])
def index():
    return 'Hello'
  
@plugin.endpoint('test')
def test():
    return plugin.send_static_file('test.txt')

plugin.add_url_rule('/test', endpoint='test', methods=['GET'])

@plugin.get('/say/<string:name>')
def hello(name):
    return render_template('index.html', name=name)
  
@plugin.get('/doge')
def hello_to_doge():
    return redirect(url_for('.hello', name='doge'))
    
@plugin.before_request
...

@plugin.errorhandler(403)
...
```

You may have noticed that when using the `redirect` function, if you want to jump to an `endpoint` within a plugin, you need to prefix it with a `.` to identify the lookup domain as the current plugin -- in fact, this is the same behavior as Blueprint; of course, you can also call your function via a "pattern" like `plugin_blueprint.plugin_domain.endpoint` to call your function, but the way using dot will make it easier for you.

Note: Any `url_for` that points to a resource inside the plugin can follow the pattern above, which means that when you want to add a static resource reference inside a template file, you can write it like this.

```html
<link rel="stylesheet" href="{{ url_for('.static', filename='css/style.css') }}">
```

## Access Plugin Info

Once the plugin has been initialized, there are a number of properties that provide information about the plugin, they are:

- :py:attr:`.Plugin.id_`: plugin ID.
- :py:attr:`.Plugin.domain`: plugin domain.
- :py:attr:`.Plugin.basedir`: plugin dirname.
- :py:attr:`.Plugin.name`: plugin name.
- :py:attr:`.Plugin.status`: plugin status, a `Enum` value, defined in :py:class:`.states.PluginStatus`.
- :py:attr:`.Plugin.info`: plugin extension info.

:py:attr:`.Plugin.info` is a :py:class:`.utils.attrdict` like a "dict", but you could access or edit it using attributes:

```python
>>> plugin.info.version
(0, 0, 0)
>>> plugin.info.maintainer = 'Doge'
>>> plugin.info.maintainer
'Doge'
```

When you are trying to use an API interface to return full information about a plugin, the function :py:meth:`.Plugin.export_status_to_dict` may helps. It will wrap all the above mentioned plugin information into a dictionary and return.

```python
>>> plugin.export_status_to_dict()
{
    'domain': 'plugins',
    'id': '99c38e87f85f4b7484ff1fac47da2d27',
    'info': {
        'author': 'Doge', 
        'description': 'A Example Plugin', 
        'version': (0, 0, 0)
    },
    'name': 'flaskex',
    'status': 'Running'
}
```

## Plugin Management

Although :py:class:`.Plugin` provides functions :py:meth:`.Plugin.load`、:py:meth:`.Plugin.register`、:py:meth:`.Plugin.unregister`、:py:meth:`.Plugin.clean` for managing resource registered in Flask, but these functions generally called by :py:class:`.PluginManager`. 

In fact, the manager does some processing of the plugins, so please do not call these management functions above directly, but use functions provided by :doc:`manager`.

## Mechanisms

If you are interested in how plugins work, this section may help you.

1. Load

   When the plugin is `imported` by the manager, all the view function definitions are loaded into a list of deferred functions that are used to register the necessary information on the Flask Application instance, just as they are in the Python Module, but note that they are not yet executed.

2. Start

   When the plugin is started on the manager, the manager provides the plugin with an instance of Flask Application and a configuration so that all the deferred functions above can run properly; after that, all the functions of the plugin can be used properly.

3. Stop

   When the plugin is stopped, all the plugin's routes are saved rather than deleted, but the corresponding Endpoint function is replaced with one that returns a direct 404 error; thus the plugin's view function is rendered useless.

4. Unload

   The uninstall operation will wipe all information previously registered with the Flask Application instance; for large applications, wiping `Flask.url_map` will cost some resources.

## Other

If you access the `request.blueprint` variable while accessing the plugin view function, you will find that the current Blueprint is not `plugins` but `plugins.plugin_domain`, thats alright, because Flask find Blueprints based on `.` spliting.

Nested Blueprint is supported for Flask since version 2.0; in fact the behavior of our plugin looks very similar to it, except that nesting is not supported and plugin can dynamically manage routes.