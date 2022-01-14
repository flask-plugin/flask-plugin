from src import Plugin
from flask import render_template

plugin = Plugin(
    id_='same-domain-as-blueprint',
    domain='plugins',
    name='same-domain-as-blueprint',
    template_folder='templates'
)

@plugin.route('/<string:name>', methods=['GET'])
def index(name: str):
    return render_template('index.html', name=name)
