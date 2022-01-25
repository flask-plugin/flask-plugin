from src import Plugin

plugin = Plugin()

@plugin.endpoint('index')
def index():
    return 'index'

plugin.add_url_rule('/', endpoint='index', methods=['GET'])
