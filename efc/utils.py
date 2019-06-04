# coding: utf8
from __future__ import absolute_import, division, print_function, unicode_literals

from string import ascii_uppercase

import six

__all__ = ('col_str_to_index', 'col_index_to_str', 'u', 'cached_property', 'digit',
           'Array')


def col_str_to_index(col_str):
    """
    A -> 1
    B -> 2
    Z -> 26
    AA -> 27
    :param basestring col_str: [A-Z]+
    :rtype: int
    """
    str_len = len(col_str)
    base = len(ascii_uppercase)
    return sum((ascii_uppercase.index(s) + 1) * base ** (str_len - i)
               for i, s in enumerate(col_str, 1))


def col_index_to_str(i):
    base = len(ascii_uppercase)
    chars = []
    while i:
        i, r = divmod(i, base)
        if r == 0:
            r = base
            i -= 1
        chars.append(ascii_uppercase[r - 1])
    chars.reverse()
    return ''.join(chars)


def u(value):
    if isinstance(value, six.binary_type):
        return value.decode('utf8')
    elif isinstance(value, six.text_type):
        return value
    elif isinstance(value, (six.integer_types, float)):
        return six.text_type(value)
    else:
        return six.u(value)


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


def digit(v):
    if isinstance(v, six.string_types):
        v = float(v)
    elif isinstance(v, bool):
        v = int(v)
    elif v is None:
        v = 0
    return v


class Array(object):
    def __init__(self, array=None):
        self._array = array or []
        self._pos = -1

    def append(self, v):
        self._array.append(v)

    @property
    def is_ended(self):
        return self._pos + 1 >= len(self._array)

    def __next__(self):
        if self.is_ended:
            raise StopIteration()
        else:
            self._pos += 1
            v = self._array[self._pos]
            return v

    def next(self):
        return self.__next__()

    def prev(self):
        return self._array[self._pos - 1] if self._pos > 0 else None

    def current(self):
        return self._array[self._pos] if self._pos >= 0 else None

    def __len__(self):
        return len(self._array)

    def reset(self):
        self._pos = -1

    def __iter__(self):
        return iter(self._array)

    def step_back(self, step=1):
        if step > self._pos + 1:
            self.reset()
        else:
            self._pos -= step

    def __getitem__(self, item):
        return self._array[item]
