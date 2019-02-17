# coding: utf8

from __future__ import unicode_literals, print_function
from efc.rpn_builder.errors import OperandsMissing
from efc.rpn_builder.parser.operands import (SimpleOperand, SingleCellOperand, CellSetOperand,
                                             ErrorOperand, SimpleSetOperand, ValueErrorOperand, OperandLikeObject,
                                             ZeroDivisionErrorOperand)
from efc.rpn_builder.parser.operations import Operation
from efc.utils import Array

from six.moves import range

__all__ = ('RPN',)


class RPN(Array):
    def __init__(self, formula):
        super(RPN, self).__init__()
        self.formula = formula

    def handle_result(self, result, ws_name, source):
        if len(result) == 1:
            return result[0]
        else:
            # Trying to get first error in result
            for item in (i for i in result if isinstance(i, ErrorOperand)):
                return item

            if isinstance(result[0], SingleCellOperand):
                set_type = CellSetOperand
            elif isinstance(result[0], SimpleOperand):
                set_type = SimpleSetOperand
            else:
                return result

            # Trying to build set from result
            try:
                result_set = set_type(ws_name=ws_name, source=source)
                result_set.add_row(result)
                return result_set
            except ValueErrorOperand as err:
                return err

    def calc(self, ws_name, source):
        result = []

        result_append = result.append
        result_pop = result.pop
        for token in self:
            if isinstance(token, OperandLikeObject):
                result_append(token)
            elif isinstance(token, Operation):
                try:
                    args = [result_pop() for _ in range(token.operands_count)]
                except IndexError:
                    raise OperandsMissing(token.f_name, self.formula)

                args.reverse()

                try:
                    v = token.eval(*args)
                except ErrorOperand as err:
                    v = err
                except (TypeError, ValueError):
                    v = ValueErrorOperand()
                except ZeroDivisionError:
                    v = ZeroDivisionErrorOperand()

                if isinstance(v, ErrorOperand):
                    v.formula = self.formula
                    if v.ws_name is None:
                        v.ws_name = ws_name
                result_append(v)

        return self.handle_result(result, ws_name, source)