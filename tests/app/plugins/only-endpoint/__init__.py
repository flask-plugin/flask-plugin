from src import Plugin

plugin = Plugin(
    id_='only-endpoint',
    domain='oe',
    name='only-endpoint'
)

@plugin.endpoint('index')
def index():
    return 'index'

plugin.add_url_rule('/', endpoint='index', methods=['GET'])
