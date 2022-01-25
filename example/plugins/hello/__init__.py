
from flask_plugin import Plugin
from flask import redirect, url_for, abort

plugin = Plugin()


@plugin.route('/say/<string:name>', methods=['GET'])
def say(name: str):
    return 'Hello ' + name


@plugin.route('/admin', methods=['GET'])
def hello2admin():
    return redirect(url_for('.say', name='Doge'))


@plugin.route('/403', methods=['GET'])
def test_forbidden():
    abort(403)


@plugin.errorhandler(403)
def forbidden(error):
    return 'My Forbidden!', 403


@plugin.before_request
def before_request():
    print('Handled before request.')
