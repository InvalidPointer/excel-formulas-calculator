# coding: utf8

from __future__ import unicode_literals, print_function
import unittest

from efc import get_calculator


class TestFormulaCalculator(unittest.TestCase):
    arithmetic_examples = (
        ('4', 4),
        ('4 + 4', 8),
        ('4 - 2', 2),
        ('4 * 4', 16),
        ('9 ^ 2', 81),
        ('9 / 3', 3),
        ('1 + 2 * 3', 7),
        ('2 * 3 + 1', 7),
        ('2 - (2 - 3)', 3),
        ('2 - 2 * 8 - 3', -17),
        ('2 - 2 - 3 - 6', -9),
        ('2 - 2 - 3', -3),
        ('2 - 2 + 3', 3),
        ('2 - (2 + 3)', -3),
    )

    compare_examples = (
        ('4 > 3', True),
        ('4 = 3', False),
        ('4 <> 3', True),
        ('4 < 3', False),
        ('4 + 1 > 4', True),
        ('4 > 4 - 3', True),
        ('4 * 2 + 2 <> 4 / 3 - 1', True),
    )

    def setUp(self):
        self.calc = get_calculator(None)

    def run_test_on_examples(self, examples):
        for expr, result in examples:
            calc_result = self.calc(expr)
            self.assertEqual(calc_result, result, '%s = %s, expected: %s' % (expr, calc_result, result))

    def test_arithmetic(self):
        self.run_test_on_examples(self.arithmetic_examples)

    def test_compare(self):
        self.run_test_on_examples(self.compare_examples)

    def test_cell_address(self):
        self.calc('B4')
