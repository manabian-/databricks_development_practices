# Databricks notebook source
import sys
import os
import unittest

# ローカル開発時に利用するモジュールの呼び出し
try:
    sys.path.append(
        os.path.join(
            os.path.dirname(__file__),
            '../../../src',
        )
    )
    from add_num import add_num
except (NameError, ImportError):
    pass

class test__add_num(unittest.TestCase):
    """`add_num`関数に対する単体テスト"""

    def test__add_num__001(self):
        """successes（正常系テスト）"""
        self.assertTrue(add_num(1, 1) == 2)

    def test__add_num__002(self):
        """successes（異常系テスト）"""
        # 文字を引数とすることでエラーとなる想定
        with self.assertRaises(TypeError):
            add_num(1, 'ABC')

    def test__add_num__003(self):
        """failures"""
        self.assertTrue(add_num(1, 1) == 1)

    def test__add_num__004(self):
        """errors"""
        self.assertTrue(1 + "a")

    @unittest.skip("スキップ用")
    def test__add_num__005(self):
        """skipped"""
        assert a

    @unittest.expectedFailure
    def test__add_num__006(self):
        """expectedFailure"""
        self.assertTrue(add_num(1, 1) == 1)

    @unittest.expectedFailure
    def test__add_num__007(self):
        """unexpectedSuccesses"""
        self.assertTrue(add_num(1, 1) == 2)

