
from flask import Flask, jsonify, abort
from flask.templating import render_template
from src import PluginManager

from . import config


def init_app(config_name: str) -> Flask:
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(getattr(config, config_name, None))
    manager = PluginManager(app)

    @app.route('/api', methods=['GET'])
    def api():
        return jsonify(manager.status)

    @app.route('/<string:action>/<string:id>', methods=['GET'])
    def operate(action, id):
        plugin = manager.find(id_=id)
        if not plugin or not action in {'load', 'unload', 'start', 'stop'}:
            abort(404)
        try:
            getattr(manager, action)(plugin)
        except Exception as error:
            return str(error.args[0]), 502
        return 'success'

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    return app
