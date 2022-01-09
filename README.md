# Flask-Plugin 扩展开发

## 项目目标

一个基于 Flask、可以热插拔、方便管理的插件系统。

**Features:**

1. 每个插件都可以在 Flask 运行时启动、停止、**热更新**。
2. 在插件内部可以使用与 Application、Blueprint 类似的路由定义方式，并且可以使用 Flask 的所有功能（Jinja 模板渲染、URL 构造、消息闪现等等）。
4. 无需单独配置，与 Flask 一同配置即可使用。
5. 方便的插件自动发现与管理。

## 快速开始

1. 加载插件管理器并启动插件：

   ```python
   from flask import Flask
   from flask_plugin import Manager
   
   app = Flask(__name__)
   manager = Manager(app)
   plugin = manager.find(id_='347336b4fcdd447985aec57f2bc5793c')
   if plugin:
       manager.load(plugin)
       manager.start(plugin)
   app.run()
   ```

2. 使用默认的插件目录 `plugins`，您的 `hello` 插件应该存放在 `plugins/hello` 文件夹中，此时项目的目录结构应该类似这样：

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
   
3. 在 `SayHello/__init__.py` 中实例化 `Plugin` 类，即可像在 `Flask` 中一样定义路由：

   ```python
   from flask_plugin import Plugin
   from flask import redirect, url_for
   
   plugin = Plugin(
    id_ = '347336b4fcdd447985aec57f2bc5793c', 
    domain='hello', name='Greeting',
    static_folder='static',
    template_folder='templates'
   )
   
   @plugin.route('/say/<string:name>', methods=['GET'])
   def say(name: str):
       return 'Hello ' + name
   
   @plugin.route('/admin', methods=['GET'])
   def hello2admin():
       return redirect(url_for('.say', name='Doge'))
   
   @plugin.route('/', methods=['GET'])
   def index():
       return render_template('index.html', name='Anonymous')
   
   @plugin.route('/static', methods=['GET'])
   def staticfile():
       return plugin.send_static_file('test.txt')
   ```

4. 在 `/plugins/hello/` 下访问您的服务！

## 注意

大部分时候，`Plugin` 实例的行为与 `Blueprint/Flask` 类似，但是仍需要注意以下几点：

1. 从管理器上“卸载”已经启动过的插件时，会对整个 Flask 应用的 `url_map` 进行替换，如果您的应用较为庞大，这可能会消耗一些资源。
2. 插件管理器将会注册配置中的 `blueprint` 作为自己的蓝图名称以及 `url_prefix`。
3. 与 Application、Blueprint 不同，Plugin 作为最小的功能实现模块，不允许嵌套（Nested Plugin Not Allowed）。
