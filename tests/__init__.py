
import json
import os
import sys
from typing import Dict, Optional
import unittest

dirname = os.path.dirname(__file__)
workdir = os.path.abspath(dirname)
sys.path.append(os.path.realpath(os.path.join(dirname, '..')))

try:
    __import__('src')
except ImportError:
    raise ImportError('cannot find src package')


class SequentialTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        test_names = super().getTestCaseNames(testCaseClass)
        testcase_methods = list(testCaseClass.__dict__.keys())
        test_names.sort(key=testcase_methods.index)  # type: ignore
        return test_names


def create_empty_plugin(
    dirname: str, config: Optional[Dict] = None,
    casesdir: str = 'app/plugins',
    code: str = 'from src import Plugin\nplugin = Plugin()'
) -> str:
    """Create a empty plugin for testing.

    Args:
        dirname (str): plugin dirname.
        config (Dict): dump to plugin config plugin.json. Defaults to None.
        casesdir (str): dir for storage testcases. Defaults to 'app'.
        code (str): default empty plugin code in `__init__.py`.

    Returns:
        str: absolute plugin workdir.
    """
    casedir = os.path.join(workdir, casesdir, dirname)
    if not os.path.isdir(casedir):
        os.mkdir(casedir)
    if config:
        with open(os.path.join(casedir, 'plugin.json'), 'w') as handler:
            json.dump(config, handler)
    with open(os.path.join(casedir, '__init__.py'), 'w') as handler:
        handler.write(code)
    return casedir


def suite() -> unittest.TestSuite:

    from . import test_states
    from . import test_base
    from . import test_manager
    from . import test_plugin
    from . import test_utils
    from . import test_config

    testcases = [
        test_utils.TestUtils,
        test_states.TestStates,
        test_config.TestConfig,
        test_base.TestBaseApp,
        test_manager.TestManagerApp,
        test_manager.TestInvalidImportManagerApp,
        test_manager.TestNonExistDirectoryManagerApp,
        test_plugin.TestPluginApp
    ]

    loader = SequentialTestLoader()
    suite = unittest.TestSuite()
    for testcase in testcases:
        suite.addTests(loader.loadTestsFromTestCase(testcase))
    return suite
