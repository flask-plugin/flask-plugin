from flask_plugin import Plugin
from flask import redirect, url_for, render_template, abort

plugin = Plugin(
    id_='hello',
    domain='hello',
    name='hello',
    static_folder='static',
    template_folder='templates'
)


@plugin.route('/doge', methods=['GET'])
def hello2admin():
    return redirect(url_for('.index', name='Doge'))


@plugin.route('/<string:name>', methods=['GET'])
def index(name: str):
    return render_template('index.html', name=name)


@plugin.route('/staticfile', methods=['GET'])
def static_file():
    return plugin.send_static_file('file.txt')


@plugin.route('/403', methods=['GET'])
def test_forbidden():
    abort(403)

@plugin.endpoint('raise')
def raising():
    abort(502)

plugin.add_url_rule('/endpoints/raise', endpoint='raise', methods=['GET'])

@plugin.errorhandler(403)
def forbidden(error):
    return 'Hello Forbidden!', 403
