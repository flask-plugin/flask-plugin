
from .plugin import Plugin
from .manager import PluginManager
from . import signals, utils, states, config

__version__ = '.'.join(str(num) for num in (0, 0, 2))


__all__ = [
    '__version__',
    'Plugin',
    'PluginManager',
    'config',
    'signals',
    'states',
    'utils'
]
