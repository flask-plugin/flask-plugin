
import typing as t

from .utils import staticdict

ConfigPrefix = 'plugins_'  
"""All configs in ``app.config`` should startswith it."""

DefaultConfig: t.Dict[str, t.Any] = staticdict({
    'blueprint': 'plugins',
    'directory': 'plugins',
    'excludes_directory': ['__pycache__']
})
"""
It will be using when config item not found in ``app.config``.

.. code-block:: python

    DefaultConfig: t.Dict[str, t.Any] = staticdict({
        'blueprint': 'plugins',
        'directory': 'plugins',
        'excludes_directory': ['__pycache__']
    })

:meta hide-value:
"""