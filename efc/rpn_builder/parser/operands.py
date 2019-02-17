# -*- coding: utf8 -*-
from __future__ import unicode_literals
from efc.utils import cached_property, digit, u, col_index_to_str
from efc.base.errors import BaseEFCException
from collections import defaultdict
from six.moves import range

__all__ = ('Operand', 'ErrorOperand', 'ValueErrorOperand', 'WorksheetNotExist',
           'ZeroDivisionErrorOperand', 'SimpleOperand', 'SingleCellOperand',
           'CellSetOperand', 'SimpleSetOperand', 'NamedRangeOperand', 'CellRangeOperand',
           'FunctionNotSupported', 'NotFoundErrorOperand', 'RPNOperand', 'OperandLikeObject')


class OperandLikeObject(object):
    def __init__(self, ws_name=None, source=None, *args, **kwargs):
        super(OperandLikeObject, self).__init__(*args, **kwargs)
        self.ws_name = ws_name
        self.source = source


class Operand(OperandLikeObject):
    value = None

    @property
    def digit(self):
        """Digit type"""
        return digit(self.value) if self.value else 0

    @property
    def string(self):
        """String type"""
        return u(self.value) if self.value is not None else ''

    @property
    def any(self):
        """Any type: digit or string or None"""
        try:
            v = self.digit
        except ValueError:
            v = self.string
        if v in (0, ''):
            v = None
        return v

    @property
    def is_blank(self):
        return self.value in (None, '')

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __str__(self):
        return self.string

    def __deepcopy__(self, memodict):
        return self.__class__(ws_name=self.ws_name, source=self.source)


class ErrorOperand(Operand, BaseEFCException):
    code = 300
    msg = 'Unknown error'
    string_value = '#ERROR!'

    def __init__(self, *args, **kwargs):
        self.formula = kwargs.pop('formula', None)
        super(ErrorOperand, self).__init__(*args, **kwargs)

    @property
    def value(self):
        raise self

    def string(self):
        return self.string_value


class ValueErrorOperand(ErrorOperand):
    code = 301
    msg = 'Cell value error'
    string_value = '#VALUE!'


class WorksheetNotExist(ErrorOperand):
    code = 302
    msg = 'Worksheet does not exist'
    string_value = '#REF!'


class NamedRangeNotExist(ErrorOperand):
    code = 303
    msg = 'Named range "{name}" does not exist'
    string_value = '#NAME?'

    def __init__(self, name, *args, **kwargs):
        super(NamedRangeNotExist, self).__init__(*args, **kwargs)
        self.name = name


class ZeroDivisionErrorOperand(ErrorOperand):
    code = 304
    msg = 'Zero division'
    string_value = '#DIV/0!'


class NotFoundErrorOperand(ErrorOperand):
    code = 305
    msg = 'Result not found'
    string_value = '#VALUE!'


class FunctionNotSupported(ErrorOperand):
    code = 306
    msg = 'Function "{f_name}" not found among available functions'
    string_value = '#NAME?'

    def __init__(self, f_name, *args, **kwargs):
        super(FunctionNotSupported, self).__init__(*args, **kwargs)
        self.f_name = f_name


class SimpleOperand(Operand):
    def __init__(self, value, *args, **kwargs):
        super(SimpleOperand, self).__init__(*args, **kwargs)
        self.value = value

    def __deepcopy__(self, memodict):
        return self.__class__(value=self.value, ws_name=self.ws_name, source=self.source)


class CellsOperand(OperandLikeObject):
    def address_to_value(self):
        raise NotImplementedError

    @cached_property
    def value(self):
        if self.source.is_ws_exists(self.ws_name):
            return self.address_to_value()
        else:
            raise WorksheetNotExist(ws_name=self.ws_name)

    def get_iter(self):
        raise NotImplementedError

    def __iter__(self):
        return self.get_iter()


class SingleCellOperand(CellsOperand, Operand):
    def __init__(self, row, column, *args, **kwargs):
        super(SingleCellOperand, self).__init__(*args, **kwargs)
        self.row = row
        self.column = column

    def address_to_value(self):
        return self.source.cell_to_value(self.row, self.column, self.ws_name)

    def get_iter(self):
        yield self

    @property
    def address(self):
        return "'%s'!%s%d" % (self.ws_name, col_index_to_str(self.column), self.row)

    def __deepcopy__(self, memodict):
        return self.__class__(row=self.row, column=self.column, ws_name=self.ws_name, source=self.source)


class SetOperand(OperandLikeObject):
    operands_type = None

    def __init__(self, *args, **kwargs):
        super(SetOperand, self).__init__(*args, **kwargs)
        self._items = defaultdict(list)

    def check_type(self, items):
        if isinstance(items, list):
            if any(not isinstance(i, self.operands_type) for i in items):
                raise ValueErrorOperand()
        elif not isinstance(items, self.operands_type):
            raise ValueErrorOperand()

    def add_cell(self, item, row=0):
        self.check_type(item)
        self._items[row].append(item)

    def add_many(self, items, row=0):
        self.check_type(items)
        append = self._items[row].append
        for item in items:
            append(item)

    def add_row(self, items):
        self.check_type(items)
        r = max(self._items) + 1 if self._items else 1
        self.add_many(items, r)

    def get_iter(self):
        for r in sorted(self._items.keys()):
            for item in self._items[r]:
                yield item

    def __iter__(self):
        return self.get_iter()

    @cached_property
    def value(self):
        return list(self)


class CellSetOperand(SetOperand):
    operands_type = SingleCellOperand


class SimpleSetOperand(SetOperand):
    operands_type = SimpleOperand


class CellRangeOperand(CellsOperand):
    def __init__(self, row1, column1, row2, column2, *args, **kwargs):
        super(CellRangeOperand, self).__init__(*args, **kwargs)
        self.row1 = row1
        self.column1 = column1
        self.row2 = row2
        self.column2 = column2

    def get_iter(self):
        column1 = self.source.min_column(self.ws_name) if self.column1 is None else self.column1
        column2 = self.source.max_column(self.ws_name) if self.column2 is None else self.column2
        row1 = self.source.min_row(self.ws_name) if self.row1 is None else self.row1
        row2 = self.source.max_row(self.ws_name) if self.row2 is None else self.row2

        if row1 == row2:
            for c in range(column1, column2 + 1):
                yield SingleCellOperand(row1, c, self.ws_name, self.source)
        elif column1 == column2:
            for r in range(row1, row2 + 1):
                yield SingleCellOperand(r, column1, self.ws_name, self.source)
        else:
            for r in range(row1, row2 + 1):
                for c in range(column1, column2 + 1):
                    yield SingleCellOperand(r, c, self.ws_name, self.source)

    def address_to_value(self):
        return self.get_iter()

    @property
    def address(self):
        return "'%s'!%s%d:%s%d" % (self.ws_name,
                                   col_index_to_str(self.column1), self.row1,
                                   col_index_to_str(self.column2), self.row2)

    def __deepcopy__(self, memodict):
        return self.__class__(row1=self.row1, column1=self.column1,
                              row2=self.row2, column2=self.column2,
                              ws_name=self.ws_name, source=self.source)


class NamedRangeOperand(CellsOperand):
    def __init__(self, name, *args, **kwargs):
        super(NamedRangeOperand, self).__init__(*args, **kwargs)
        self.name = name

    def address_to_value(self):
        return self.source.named_range_to_cells(self.name, self.ws_name)

    @cached_property
    def value(self):
        if not self.source.is_ws_exists(self.ws_name):
            raise WorksheetNotExist(ws_name=self.ws_name)
        elif not self.source.is_named_range_exists(self.name, self.ws_name):
            raise NamedRangeNotExist(self.name, self.ws_name)
        else:
            return self.address_to_value()

    def get_iter(self):
        return iter(self.value)

    def __deepcopy__(self, memodict):
        return self.__class__(name=self.name, ws_name=self.ws_name, source=self.source)


class RPNOperand(OperandLikeObject):
    def __init__(self, rpn, *args, **kwargs):
        super(RPNOperand, self).__init__(*args, **kwargs)
        self.rpn = rpn
        self._result = None

    @cached_property
    def evaluated_value(self):
        return self.rpn.calc(ws_name=self.ws_name, source=self.source)

    def __getattr__(self, item):
        return getattr(self.evaluated_value, item)