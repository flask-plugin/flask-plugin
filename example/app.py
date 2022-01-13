
import os
from flask import Flask, jsonify, abort
from flask_plugin import PluginManager

app = Flask(__name__)
app.secret_key = os.urandom(12)
manager = PluginManager(app)
for plugin in manager.plugins:
    manager.load(plugin)
    manager.start(plugin)

@app.route('/api', methods=['GET'])
def api():
    return jsonify(manager.status)

@app.route('/<string:action>/<string:id>', methods=['GET'])
def operate(action, id):
    plugin = manager.find(id_=id)
    if not plugin or not action in {'load', 'unload', 'start', 'stop'}:
        abort(404)
    getattr(manager, action)(plugin)
    return 'Success'

app.run(host='localhost', port=8000)
