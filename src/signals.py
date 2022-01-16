"""
Contains all custom signals based on ``flask.signals.Namespace``.

All these signals send with caller as instance of :py:class:`.PluginManager`,
and the only argument is plugin instance operated.

If you want to receive these signals, please install the blinker library, 
see: https://flask.palletsprojects.com/en/2.0.x/signals/
"""

from flask.signals import Namespace  # type: ignore

plugins = Namespace()
loaded = plugins.signal('plugin-loaded')
"""Plugin loaded signal."""
started = plugins.signal('plugin-started')
"""Plugin started signal."""
stopped = plugins.signal('plugin-stopped')
"""Plugin stopped signal."""
unloaded = plugins.signal('plugin-unloaded')
"""Plugin unloaded signal."""

__all__ = [
    'loaded',
    'started',
    'stopped',
    'unloaded'
]
