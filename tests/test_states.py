
import typing as t
import unittest

from src import states


class TestStates(unittest.TestCase):

    def setUp(self) -> None:
        self.default_state = current = states.PluginStatus.Unloaded
        self.state = states.StateMachine(states.TransferTable, current)
        self.table = states.TransferTable

        # Map source state to transferable destination states
        allowed: t.Dict[states.PluginStatus,
                        t.Set[states.PluginStatus]] = dict()
        for rule, dest in self.table.items():
            allowed.setdefault(rule[0], set()).add(dest)

        # Filter all states which able to transfer to all states
        self.allowed = {src: dests for src, dests in allowed.items() if len(
            dests) != len(states.PluginStatus)}

    def test_transfer_table(self) -> None:
        for rule, dest in self.table.items():
            src, _op = rule
            self.assertIsInstance(src, states.PluginStatus)
            self.assertIsInstance(dest, states.PluginStatus)

    def test_state_reading(self) -> None:
        self.assertEqual(self.state.value, self.default_state)

    def test_transfer_directly_correctly(self) -> None:
        for rule, dest in self.table.items():
            src, _op = rule
            if self.state.value == src:
                try:
                    self.state.value = dest
                except RuntimeError:
                    self.fail(
                        f'failed transfer state from {src.name} to {dest.name}')

    def test_transfer_directly_wrongly(self) -> None:
        if not self.state.value in self.allowed:
            self.skipTest('current state is able to transfer to any others')

        # Select one not allowed dest state and test
        for dest in states.PluginStatus:
            if dest not in self.allowed[self.state.value]:
                def _transfer():
                    self.state.value = dest
                self.assertRaises(RuntimeError, _transfer)
                return

    def test_all_states_tranferable(self) -> None:
        for state in states.PluginStatus:
            assrc, asdest = False, False
            for rule, dest in self.table.items():
                if rule[0] == state:
                    assrc = True
                if dest == state:
                    asdest = True
            self.assertTrue(
                assrc, msg=f"state '{state.name}' not reachable from other state")
            self.assertTrue(
                asdest, msg=f"state '{state.name}' not transferable to other state")

    def test_allow_positive_checking(self) -> None:
        for src, op in self.table.keys():
            if src == self.state.value:
                self.assertTrue(self.state.allow(op))

    def test_allow_negative_checking(self) -> None:
        self.assertFalse(self.state.allow(
            '_operation_which_never_been_allowed'))

    def test_assert_allow(self) -> None:
        self.assertRaises(RuntimeError, lambda: self.state.assert_allow(
            '_operation_which_never_been_allowed'))
