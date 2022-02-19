
import json
import jsonschema
import typing as t
from os import path
from functools import lru_cache as cache

from .utils import attrdict, staticdict

RequirementsFile = 'requirements.txt'
"""Plugin requirements.txt filename."""

ConfigFile = 'plugin.json'
"""Plugin description filename."""


@cache(None)
def __load_config_schema():
    with open(path.join(path.dirname(__file__), 'plugin.schema.json')) as handler:
        return json.load(handler)


ConfigSchema = __load_config_schema()
"""
Plugin config schema using formatted with JSON Schema. 

Required config file like:

.. code-block:: python

    {
        "id": "e9d78b6e91644381823c1aa6bdef5606",
        "domain": "flaskex",
        "plugin": {
            "name": "flaskex",
            "author": "anfederico",
            "summary": "Ported version of flaskex example."
        },
        "releases": [
            {
                "version": "0.0.1",
                "download": "https://github.com/anfederico/flaskex/releases/0.0.1.zip"
            }
        ]
    }
"""

ConfigPrefix = 'plugins_'
"""All configs in ``app.config`` should startswith it."""

DefaultConfig: t.Dict[str, t.Any] = staticdict({
    'blueprint': 'plugins',
    'directory': 'plugins',
    'excludes_directory': ['__pycache__'],
    'temporary_directory': '.temp'
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


def validate(config: attrdict) -> None:
    """Validate a plugin config in `plugin.json`.

    Args:
        config (attrdict): config dict like.

    Raises:
        jsonschema.ValidationError: if not valid config.
    """
    jsonschema.validate(instance=config, schema=ConfigSchema)
