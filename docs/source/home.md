# Introduce to Flask-Plugin

![Python](https://img.shields.io/badge/Python-3.7%2B-blue) ![License](https://img.shields.io/github/license/guiqiqi/flask-plugin) ![test](https://github.com/guiqiqi/flask-plugin/actions/workflows/unittest.yml/badge.svg) ![pylint](https://github.com/guiqiqi/flask-plugin/actions/workflows/pylint.yml/badge.svg) [![codecov](https://codecov.io/gh/guiqiqi/flask-plugin/branch/main/graph/badge.svg?token=DE329H13JM)](https://codecov.io/gh/guiqiqi/flask-plugin)


An extension to add support of Plugin in Flask.

GitHub repo: https://github.com/guiqiqi/flask-plugin

**Features:**

1. Define plugin routes in the same way as Application, Blueprint, while providing all the Flask features (Template rendering, url_for, message flashing, signals, etc.)
2. Each plugin can be started, stopped, reloaded while Flask is *running*.
3. Configured with Flask, no need to configure separately.
4. Auto-discovery and management for plugins.

**Install:**

Install Flask-Plugin using pip:

```bash
pip install flask-plugin
```

Or download Wheel package from [releases](https://github.com/guiqiqi/flask-plugin/releases/) and install using pip:

```bash
pip install flask_plugin-{{ VERSION }}-py3-none-any.whl
```

which `{{ VERSION }}` is release version.
