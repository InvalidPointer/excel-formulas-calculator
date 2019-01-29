# coding: utf8

from __future__ import unicode_literals, print_function


def add_func(a, b):
    return a + b


def subtract_func(a, b):
    return a - b


def divide_func(a, b):
    return a / b


def multiply_func(a, b):
    return a * b


def concat_func(a, b):
    return '%s%s' % (a, b)


def exponent_func(a, b):
    return a ** b


def compare_not_eq_func(a, b):
    return a != b


def compare_gte_func(a, b):
    return a >= b


def compare_lte_func(a, b):
    return a <= b


def compare_gt_func(a, b):
    return a > b


def compare_lt_func(a, b):
    return a < b


def compare_eq_func(a, b):
    return a == b


def sum_func(*args):
    result = 0.0
    for arg in (a for a in args if a):
        if isinstance(arg, list):
            if isinstance(arg[0], list):
                for row in arg:
                    result += sum(i for i in row if i)
            else:
                result += sum(i for i in arg if i)
        else:
            result += arg
    return result


ARITHMETIC_FUNCTIONS = {
    '+': add_func,
    '-': subtract_func,
    '/': divide_func,
    '*': multiply_func,
    '&': concat_func,
    '^': exponent_func,
    '<>': compare_not_eq_func,
    '>=': compare_gte_func,
    '<=': compare_lte_func,
    '>': compare_gt_func,
    '<': compare_lt_func,
    '=': compare_eq_func,
}

EXCEL_FUNCTIONS = {}
EXCEL_FUNCTIONS.update(ARITHMETIC_FUNCTIONS)
EXCEL_FUNCTIONS['SUM'] = sum_func
