# Databricks notebook source
import sys
import os
import string
import unittest
import random
from pyspark.sql import Row, SparkSession

# ローカル開発時に利用するモジュールの呼び出し
try:
    sys.path.append(
        os.path.join(
            os.path.dirname(__file__),
            '../../../src',
        )
    )
    from pyspark_sample import samples
except (NameError, ImportError):
    pass

class test__append_to_table(unittest.TestCase):
    """`append_to_table`関数に対する単体テスト"""

    def tearDown(self):
        spark = SparkSession.builder.getOrCreate()
        spark.sql(f'DROP DATABASE IF EXISTS {self.database_name} CASCADE')

    def test__append_to_table__001(self):
        """
        001 テーブルデータがない状態で、データが追加されることを確認
        """
        # --- 事前準備 ---
        spark = SparkSession.builder.getOrCreate()
        db_name_suffix = ''.join([random.choice(string.ascii_lowercase) for i in range(10)])
        self.database_name = f'_ut_db__append_to_table_001_{db_name_suffix}'

        # テスト用データベース作成
        spark.sql(f'DROP DATABASE IF EXISTS {self.database_name} CASCADE')
        spark.sql(f'CREATE DATABASE IF NOT EXISTS {self.database_name}')

        # テスト用データベースをカレントデータベースとして設定
        spark.catalog.setCurrentDatabase(self.database_name)

        # テスト用テーブル作成
        table_name = '_ut_table___append_to_table'
        spark.sql(
            f'''
            create TABLE {self.database_name}.{table_name}
            (
            string_column string,
            int_column long
            )
            USING delta
            '''
        )

        ## インプットとなるデータフレームを作成
        input_data = [
            Row(string_column='aaa', int_column=1),
            Row(string_column='bbb', int_column=2),
            Row(string_column='ccc', int_column=3),
        ]

        input_schema = """
            string_column string,
            int_column long
        """

        input_df = spark.createDataFrame(input_data, input_schema)

        ## 期待値のデータフレームを作成
        expected_data = [
            Row(string_column='aaa', int_column=1),
            Row(string_column='bbb', int_column=2),
            Row(string_column='ccc', int_column=3),
        ]
        expected_schema = """
            string_column string,
            int_column long
        """
        expected_df = spark.createDataFrame(expected_data, expected_schema)

        # --- テスト対象関数の呼び出し ---
        samples.append_to_table(
            source_df=input_df,
            target_database_name=self.database_name,
            target_table_name=table_name,
        )

        # --- 結果確認 ---
        result_df = spark.table(table_name)

        view_result = f'_result_{table_name}'
        view_expected = f'_expected_{table_name}'

        result_df.createOrReplaceTempView(view_result)
        expected_df.createOrReplaceTempView(view_expected)
        df = spark.sql(
            f'''
            SELECT * FROM {view_result} EXCEPT SELECT * FROM {view_expected}
            UNION ALL
            SELECT * FROM {view_expected} EXCEPT SELECT * FROM {view_result}
        '''
        )

        self.assertTrue(df.count() == 0)

    def test__append_to_table__002(self):
        """002 テーブルデータが存在する状態で、データが追加されることを確認"""
        # --- 事前準備 ---
        spark = SparkSession.builder.getOrCreate()
        db_name_suffix = ''.join([random.choice(string.ascii_lowercase) for i in range(10)])
        self.database_name = f'_ut_db__append_to_table_002_{db_name_suffix}'

        # テスト用データベース作成
        spark.sql(f'DROP DATABASE IF EXISTS {self.database_name} CASCADE')
        spark.sql(f'CREATE DATABASE IF NOT EXISTS {self.database_name}')

        # テスト用データベースをカレントデータベースとして設定
        spark.catalog.setCurrentDatabase(self.database_name)

        # テスト用テーブル作成
        table_name = '_ut_table___append_to_table'
        spark.sql(
            f'''
            create TABLE {self.database_name}.{table_name}(
                string_column string,
                int_column long
                )
            USING delta
            '''
        )

        ## インプットとなるデータフレームを作成
        input_data_01 = [
            Row(string_column='aaa', int_column=1),
            Row(string_column='bbb', int_column=2),
            Row(string_column='ccc', int_column=3),
        ]

        input_schema_01 = """
            string_column string,
            int_column long
        """

        input_df_01 = spark.createDataFrame(input_data_01, input_schema_01)

        input_data_02 = [
            Row(string_column='ddd', int_column=4),
            Row(string_column='eee', int_column=5),
        ]

        input_schema_02 = """
            string_column string,
            int_column long
        """

        input_df_02 = spark.createDataFrame(input_data_02, input_schema_02)

        ## 期待値のデータフレームを作成
        expected_data = [
            Row(string_column='aaa', int_column=1),
            Row(string_column='bbb', int_column=2),
            Row(string_column='ccc', int_column=3),
            Row(string_column='ddd', int_column=4),
            Row(string_column='eee', int_column=5),
        ]
        expected_schema = """
            string_column string,
            int_column long
        """
        expected_df = spark.createDataFrame(expected_data, expected_schema)

        # --- テスト対象関数の呼び出し ---
        samples.append_to_table(
            source_df=input_df_01,
            target_database_name=self.database_name,
            target_table_name=table_name,
        )

        samples.append_to_table(
            source_df=input_df_02,
            target_database_name=self.database_name,
            target_table_name=table_name,
        )

        # --- 結果確認 ---
        result_df = spark.table(table_name)

        view_result = f'_result_{table_name}'
        view_expected = f'_expected_{table_name}'

        result_df.createOrReplaceTempView(view_result)
        expected_df.createOrReplaceTempView(view_expected)
        df = spark.sql(
            f'''
            SELECT * FROM {view_result} EXCEPT SELECT * FROM {view_expected}
            UNION ALL
            SELECT * FROM {view_expected} EXCEPT SELECT * FROM {view_result}
            '''
        )

        self.assertTrue(df.count() == 0)
