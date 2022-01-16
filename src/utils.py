"""
Contains some helper functions and classes.
"""

import os
import typing as t


class attrdict(dict):
    """
    Sub-class like python dict with support for I/O like attr.

    >>> profile = attrdict({
        'languages': ['python', 'cpp', 'javascript', 'c'],
        'nickname': 'doge gui',
        'age': 23
    })
    >>> profile.languages.append('Russian')  # Add language to profile
    >>> profile.languages
    ['python', 'cpp', 'javascript', 'c', 'Russian']
    >>> profile.age == 23
    True

    Attribute-like key should not be methods with dict, and obey python syntax:

    >>> profile.1 = 0
    Traceback (most recent call last):
        ...
    SyntaxError: invalid syntax
    >>> profile.popitem = None  # Rewrite
    """

    def __setattr__(self, name: str, value: t.Any) -> None:
        if name in dir(dict):
            super().__setattr__(name, value)
        else:
            super().__setitem__(name, value)

    def __getattribute__(self, name: str) -> t.Any:
        if name in dir(dict):
            return super().__getattribute__(name)
        return super().__getitem__(name)


class staticdict(attrdict):
    """
    staticdict inherit all behaviors from attrdict but banned all writing operations on it.

    >>> final = staticdict({
        'loaded': False,
        'config': './carental/config.py'
    })
    >>> not final.loaded is True
    True
    >>> final.brand = 'new'
    Traceback (most recent call last):
        ...
    RuntimeError: cannot set value on staticdict
    """

    def __setattr__(self, _key: str, _value: object) -> t.NoReturn:
        if _key in dir(dict):
            super().__setattr__(_key, _value)
        raise RuntimeError('cannot set value on staticdict')

    def __delattr__(self, _key: str):
        raise RuntimeError('cannot delete value on staticdict')


_T = t.TypeVar('_T')


class property_(t.Generic[_T]):
    """
    A one line ``property`` decorator to support reading class attributes with prefix.

    Here is a sub-class inherit from dict which support it,
    by using ``__getattr__``, ``__setattr__``, and ``__delattr__``.
    When we want to declare a property inside class, we always doing this:

    >>> class Bar:
        def __init__(self, size: int, count: int) -> None:
            self._size = size
            self._count = count
        @property
        def size(self) -> int:
            return self._size
        @property
        def count(self) -> int:
            return self._count
    
    Obviously its sth like redundancy, by using this ``property_`` function we could:

    >>> class AnotherBar(Bar):
            size = property_('size', type_=int)
            count = property_('count', type_=int, writeable=True)

    Also you could define which selector using before attribute.
    The default one is '_'.
    """

    def __init__(self, name: str, type_: t.Type[_T] = t.Any, prefix: str = '_',
                 writable: bool = False, delectable: bool = False) -> None:
        """
        Args:
            name (str): variable name.
            _type (Type[_T], optional): type for type hinting. Defaults to Any.
            prefix (str, optional): prefix before variable name. Defaults to '_'.
            writable (bool, optional): if allowed write operation. Defaults to False.
            delectable (bool, optional): if deletable. Defaults to False.
        """
        self.__name, self.__prefix = name, prefix
        self.__writeable, self.__deletable = writable, delectable

    def __gen_prefix(self, obj) -> str:
        prefix = self.__prefix
        if prefix.startswith('__'):
            prefix = '_' + type(obj).__name__ + prefix
        return prefix

    def __get__(self, obj, _objtype) -> _T:
        return getattr(obj, self.__gen_prefix(obj) + self.__name)

    def __set__(self, obj, data: _T) -> None:
        if self.__writeable:
            setattr(obj, self.__gen_prefix(obj) + self.__name, data)

    def __delete__(self, obj) -> None:
        if self.__deletable:
            delattr(obj, self.__gen_prefix(obj) + self.__name)


def listdir(path: str, excludes: t.Container[str] = None) -> t.Iterator[str]:
    """
    List all dir inside specific path.

    Args:
        path (str): path to be explore.
        excludes (Container[str], optional): dirname to exclude. Defaults to None.

    Yields:
        Iterator[str]: dirname.

    Raises:
        FileNotFoundError: when given invalid ``path``.
    """
    if excludes is None:
        excludes=set()
    for itemname in os.listdir(path.strip('\\')):
        fullname=os.path.join(path, itemname)
        if os.path.isdir(fullname) and not itemname in excludes:
            yield os.path.abspath(fullname)


def startstrip(string: str, part: str) -> str:
    """
    Remove ``part`` from beginning of ``string`` if ``string`` startswith ``part``.

    Args:
        string (str): source string.
        part (str): removing part.

    Returns:
        str: removed part.
    """
    if string.startswith(part):
        return string[len(part):]
    return string
