
from flask_plugin import Plugin
from flask import redirect, url_for, render_template, abort

plugin = Plugin(
    id_='347336b4fcdd447985aec57f2bc5793c',
    domain='hello', name='Greeting',
    static_folder='static'
)


@plugin.route('/say/<string:name>', methods=['GET'])
def say(name: str):
    return 'Hello ' + name


@plugin.route('/admin', methods=['GET'])
def hello2admin():
    return redirect(url_for('.say', name='Doge'))


@plugin.route('/', methods=['GET'])
def index():
    return render_template('plugins/hello/index.html', name='Anonymous')


@plugin.route('/staticfile', methods=['GET'])
def static_file():
    return plugin.send_static_file('test.txt')


@plugin.route('/403', methods=['GET'])
def test_forbidden():
    abort(403)


@plugin.errorhandler(403)
def forbidden(error):
    return 'My Forbidden!', 403


@plugin.before_request
def before_request():
    print('Handled before request.')
