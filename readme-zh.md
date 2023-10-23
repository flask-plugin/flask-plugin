# Flask-Plugin

![Python](https://img.shields.io/badge/Python-3.7%2B-blue) ![License](https://img.shields.io/github/license/guiqiqi/flask-plugin) ![test](https://github.com/guiqiqi/flask-plugin/actions/workflows/unittest.yml/badge.svg) ![pylint](https://github.com/guiqiqi/flask-plugin/actions/workflows/pylint.yml/badge.svg) [![codecov](https://codecov.io/gh/guiqiqi/flask-plugin/branch/main/graph/badge.svg?token=DE329H13JM)](https://codecov.io/gh/guiqiqi/flask-plugin)


[English Version](https://github.com/guiqiqi/flask-plugin/blob/main/readme.md)

一个用于支持插件功能的 Flask 扩展。

**注意：Flask 3及以上版本将不再被支持。**

**它能提供什么：**

1. 与 Application、Blueprint 相同的方式定义插件路由，同时提供所有的 Flask 功能（模板渲染、URL 构造、消息闪现、信号等等）
1. 每个插件都可以在 Flask *运行时* 启动、停止、重载。
4. 与 Flask 一同配置，无需加载单独的配置文件。
5. 插件自动发现与管理。

## 安装

使用 pip 安装：

```bash
pip install flask-plugin
```

## 快速开始

1. 进入 `example` 目录，查看目录结构，可以看到在 `plugins` 目录下有一个名为 `hello` 的插件：

   ```
   example
   ├── app.py
   └── plugins
       └── hello
           ├── __init__.py
           └── plugin.json
   ```
   
2. 在 `app.py` 文件中加载插件管理器，并启动 `hello` 插件：

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

2. 在 `SayHello/plugin.json` 中定义插件信息：

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
   
2. 在 `SayHello/__init__.py` 中实例化 `Plugin` 类，并像在 `Flask` 中一样定义路由：

   ```python
   from flask_plugin import Plugin
   from flask import redirect, url_for
   
   plugin = Plugin()
   
   ...
   # Other routes defined here
   
   @plugin.route('/<string:name>', methods=['GET'])
   def say(name: str):
       return 'Hello ' + name
   ```
   
4. 访问 `/plugins/hello/doge` ，看到一个给匿名用户的问候：

   ```
   Hello doge!
   ```

   通过访问  `/api/stop/347336b4fcdd447985aec57f2bc5793c` 停止插件，再次检查上面的链接，会得到一个 `HTTP 404` 错误。

更多信息和文档参见：[Flask-Plugin Documentation](https://docs.flask-plugin.org)

## 致谢

该项目基于 [Pallets项目组](https://palletsprojects.com/) 的诸多开源项目，在此表示感谢.

同时感谢我的家人和朋友们。
