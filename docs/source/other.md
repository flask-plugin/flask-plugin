# Other

## Signals

Flask supports signals which allow you to decouple your application; in the Flask-Plugin, you can also use several signals:

- :py:obj:`.signals.loaded`: triggered when plugin launched
- :py:obj:`.signals.started`: triggered when plugin started
- :py:obj:`.signals.stopped`: triggered when plugin stopped
- :py:obj:`.signals.unloaded`: triggered when plugin unloaded

The caller of all signals above is the current :py:class:`.PluginManager` instance, and the only parameter is the plugin :py:class:`.Plugin` instance being operated.

If you want to enable signaling in Flask, you may need to install the `blinker` library, for more information see: https://flask.palletsprojects.com/en/2.0.x/signals/

## Plugin State Machine

The state of the plugin in Flask-Plugin is an `enum.Enum` enumeration type that contains the following states.

- :py:const:`.states.PluginStatus.Loaded`
- :py:const:`.states.PluginStatus.Running`
- :py:const:`.states.PluginStatus.Stopped`
- :py:const:`.states.PluginStatus.Unloaded`

Plugin status is managed by the finite state machine :py:class:`.states.StateMachine`; after a plugin is loaded, you can access this state machine instance in :py:attr:`.Plugin.status`.

Generally you don't need to directly access the state of the plugin, but if you are making extension related to it, you can use the :py:meth:`.states.StateMachine.allow` method to check whether the current state allows a certain operation.

The 'operation' is a string, and the mapping of a tuple of the current state and the operation to the target state is called the state transfer table. The default transfer table of Flask-Plugin is defined in :py:const:`.states.TransferTable`.

See more information at :doc:`api`。