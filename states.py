
import enum
import typing as t


@enum.unique
class PluginStatus(enum.Enum):
    """Plugin Status Enumerating
    Plugin status could be 4 `enum.Enum` values:
        0. Loaded
            When we called `__import__` for importing plugin moudule
            and all view function has been added to `Plugin.endpoints`.
            But in `app.url_map` there's no record added.
        1. Running
            After called `Plugin.register` all mapping from endpoint to function
            will be added to `app.url_map` so plugin will run functionally.
        2. Stopped
            After we called `Plugin.unregister`, all record inside `app.url_map`
            will still exist, but mapping from endpoints to view functions in `app.view_functions` 
            will be point to `Plugin.notfound` which will directly return HTTP 404.
        3. Unloaded
            After calling `Plugin.clean`, records in `app.url_map` will be remapped,
            and `app.view_functions` will also be removed.
            All data inner `Plugin` instance will be cleaned also.
    """
    Loaded = 0
    Running = 1
    Stopped = 2
    Unloaded = 3


# Default State Transfer Table
TransferTable: t.Dict[t.Tuple[PluginStatus, str], PluginStatus] = {
    (PluginStatus.Unloaded, 'load'): PluginStatus.Loaded,
    (PluginStatus.Loaded, 'unload'): PluginStatus.Unloaded,
    (PluginStatus.Loaded, 'start'): PluginStatus.Running,
    (PluginStatus.Running, 'stop'): PluginStatus.Stopped,
    (PluginStatus.Stopped, 'start'): PluginStatus.Running,
    (PluginStatus.Stopped, 'unload'): PluginStatus.Unloaded
}


class StateMachine:
    """We dont want check `Plugin.status` everytime to ensure if an operation
    is suitable for execution, so it's better to write an simple finite-state-machine
    to manage this:
        ```
        machine = StateMachine(transfer_table, current_state)
        if machine.allow('start'):
            ...
        @machine.limit('start')
        def test():
            ...
        ```
    """

    def __init__(self, table: t.Dict[t.Tuple[PluginStatus, str], PluginStatus],
                 current: PluginStatus = PluginStatus.Unloaded) -> None:
        """
        Args:
            table (t.Dict[t.Tuple[PluginStatus, str], PluginStatus]): transfer table
            current (t.Optional[PluginStatus]): default state. Default to PluginStatus.Unloaded
        """
        self._transfers = table
        self._current = current

    @property
    def value(self) -> PluginStatus:
        return self._current

    @value.setter
    def value(self, state: PluginStatus) -> None:
        for rule, dest in self._transfers.items():
            if rule[0] == self._current and dest == state:
                self._current = state
                return
        raise RuntimeError(
            f"cannot transfer state from '{self._current.name}' to '{state}'")

    def allow(self, operation: str) -> bool:
        if (self._current, operation) in self._transfers:
            return True
        return False

    def assert_allow(self, operation):
        if not self.allow(operation):
            raise RuntimeError(
                f"operation '{operation}' not allowed in state '{self._current.name}'")

    def limit(self, function: t.Callable, operation: str) -> t.Callable:
        if self.allow(operation):
            return function

        def _empty(*_, **kwargs):
            raise RuntimeError(
                f"operation '{operation}' not allowed in state '{self._current.name}'")
        return _empty
