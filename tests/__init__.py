
import os
import sys
import unittest
dirname = os.path.dirname(__file__)
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
        test_manager.TestDuplicatedPluginIDApp,
        test_plugin.TestPluginApp,
        test_plugin.TestLackingPluginConfig,
        test_plugin.TestInvalidPluginDomain,
        test_plugin.TestEmptyPluginDomainConfig
    ]

    loader = SequentialTestLoader()
    suite = unittest.TestSuite()
    for testcase in testcases:
        suite.addTests(loader.loadTestsFromTestCase(testcase))
    return suite
