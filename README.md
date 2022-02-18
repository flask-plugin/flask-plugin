# Flask-Plugin

![Python](https://img.shields.io/badge/Python-3.7%2B-blue) ![License](https://img.shields.io/github/license/guiqiqi/flask-plugin) ![test](https://github.com/guiqiqi/flask-plugin/actions/workflows/unittest.yml/badge.svg) ![pylint](https://github.com/guiqiqi/flask-plugin/actions/workflows/pylint.yml/badge.svg) [![codecov](https://codecov.io/gh/guiqiqi/flask-plugin/branch/main/graph/badge.svg?token=DE329H13JM)](https://codecov.io/gh/guiqiqi/flask-plugin)


[中文版本](https://github.com/guiqiqi/flask-plugin/blob/main/readme-zh.md)

An extension to add support of Plugin in Flask.

**Features:**

1. Define plugin routes in the same way as Application, Blueprint, while providing all the Flask features (Template rendering, url_for, message flashing, signals, etc.)
2. Each plugin can be started, stopped, reloaded while Flask is *running*.
3. Configured with Flask, no need to configure separately.
4. Auto-discovery and management for plugins.

## Install

Install Flask-Plugin using pip:

```bash
pip install flask-plugin
```

## Quick Start

1. Entering the `example` directory, you will find the following directory structure, the plugin `hello` inside  `plugins` directory:

   ```
   example
   ├── app.py
   └── plugins
       └── hello
           ├── __init__.py
           └── plugin.json
   ```

2. The plugin manager is loaded in the `app.py` file, and the hello plugin is started:

   ```python
   from flask import Flask
   from flask_plugin import PluginManager
   
   app = Flask(__name__)
   manager = PluginManager(app)
   plugin = manager.find(id_='962e3b6cd8b74d02a5a02f1e3651ef87')
   if plugin:
       manager.load(plugin)
       manager.start(plugin)
   
   ...
   # API Management code here
   app.run()
   ```

3. Define plugin info in `SayHello/plugin.json` file:

   ```json
   {
        "id": "962e3b6cd8b74d02a5a02f1e3651ef87",
        "domain": "hello",
        "plugin": {
            "name": "Greeting",
            "author": "Doge",
            "summary": "Hello Flask-Plugin."
        },
        "releases": []
   }
   ```
   
3. Instantiated the `Plugin` in `SayHello/__init__.py` and define the route as you did in `Flask`:

   ```python
   from flask_plugin import Plugin
   from flask import redirect, url_for
   
   plugin = Plugin()
   
   ...
   # Other routes defined here
   
   @plugin.route('/say/<string:name>', methods=['GET'])
   def say(name: str):
       return 'Hello ' + name
   ```
   
4. Accessing `/plugins/hello/` and see the greeting:

   ```
   Hello Anonymous!
   ```

   Stop the plugin with accessing `/api/stop/347336b4fcdd447985aec57f2bc5793c`, check url above again, and get a `HTTP 404` error.

Documentation for Flask-Plugin avaliable on: [Flask-Plugin Documentation](https://docs.flask-plugin.org)

## Thanks

This project is based on many open source projects of the [Pallets group](https://palletsprojects.com/), and I would like to express my thanks here.

Also thanks to my family and friends.