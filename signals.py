
from flask.signals import Namespace  # type: ignore

plugins = Namespace()
loaded = plugins.signal('plugin-loaded')
started = plugins.signal('plugin-started')
stopped = plugins.signal('plugin-stopped')
unloaded = plugins.signal('plugin-unloaded')
