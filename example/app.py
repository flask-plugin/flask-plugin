
from flask import Flask, jsonify, abort
from flask_plugin import PluginManager

app = Flask(__name__)
manager = PluginManager(app)
manager.start(manager.find(id_='347336b4fcdd447985aec57f2bc5793c'))

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

app.run()
