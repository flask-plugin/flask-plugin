
import unittest

from jsonschema import ValidationError
from src import config


class TestConfig(unittest.TestCase):

    Configs = {
        False: [
            {
                'id': 'test',
                'domain': 'test'
            },
            {
                'id': 'test',
                'plugin': {
                    'name': 'test',
                    'author': 'test',
                    'summary': 'test',
                },
                'releases': [
                    {
                        'version': 'v0.0.1',
                        'download': 'test_address'
                    }
                ]
            },
            {
                'id': 'test',
                'domain': 'test',
                'plugin': {
                    'author': 'test',
                    'summary': 'test',
                },
                'releases': [
                    {
                        'version': 'v0.0.1',
                        'download': 'test_address'
                    }
                ]
            },
            {
                'id': 'test',
                'domain': 'test',
                'plugin': {
                    'name': 'test',
                    'author': 'test',
                    'summary': 'test',
                },
                'releases': {
                    'v0.0.1': 'test_address'
                }
            },
            {
                'id': 123456,
                'domain': 'test',
                'plugin': {
                    'name': 'test',
                    'author': 'test',
                    'summary': 'test',
                },
                'releases': {
                    'v0.0.1': 'test_address'
                }
            }
        ],
        True: [
            {
                'id': 'test',
                'domain': 'test',
                'plugin': {
                    'name': 'test',
                    'author': 'test',
                    'summary': 'test',
                },
                'releases': [
                    {
                        'version': 'v0.0.1',
                        'download': 'test_address'
                    }
                ]
            },
            {
                'id': 'test',
                'domain': 'test',
                'plugin': {
                    'name': 'test',
                    'author': 'test',
                    'summary': 'test',
                    'repo': 'test',
                    'url': 'plugin_site_url'
                },
                'releases': [
                    {
                        'version': 'v0.0.1',
                        'download': 'test_address'
                    }
                ]
            }
        ]
    }

    def test_validate(self) -> None:
        for wrong_config in self.Configs[False]:
            self.assertRaises(ValidationError, lambda: config.validate(wrong_config))
        for ok_config in self.Configs[True]:
            config.validate(ok_config)
