# Quick Start

1. Entering the `example` directory, you will find the following directory structure, the plugin `hello` inside  `plugins` directory:

   ```
   example
   ├── app.py
   └── plugins
       └── hello
           ├── __init__.py
           ├── static
           │   └── test.txt
           └── templates
               └── index.html
   ```

2. The plugin manager is loaded in the `app.py` file, and the hello plugin is started:

   ```python
   from flask import Flask
   from flask_plugin import PluginManager
   
   app = Flask(__name__)
   manager = PluginManager(app)
   plugin = manager.find(id_='347336b4fcdd447985aec57f2bc5793c')
   if plugin:
       manager.load(plugin)
       manager.start(plugin)
   
   ...
   # API Management code here
   app.run()
   ```

3. Instantiated the `Plugin` in `SayHello/__init__.py` and define the route as you did in `Flask`:

   ```python
   from flask_plugin import Plugin
   from flask import redirect, url_for
   
   plugin = Plugin(
    id_ = '347336b4fcdd447985aec57f2bc5793c', 
    domain='hello', name='Greeting',
    static_folder='static',
    template_folder='templates'
   )
   
   ...
   # Other routes defined here
   
   @plugin.route('/', methods=['GET'])
   def index():
       return render_template('index.html', name='Anonymous')
   ```

4. Accessing `/plugins/hello/` and see the greeting:

   ```
   Hello Anonymous!
   ```

   Stop the plugin with accessing `/api/stop/347336b4fcdd447985aec57f2bc5793c`, check url above again, and get a `HTTP 404` error.