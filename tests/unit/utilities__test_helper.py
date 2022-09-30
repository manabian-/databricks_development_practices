# Databricks notebook source
import datetime
import inspect
import json
import math
import os
import random
import string
import sys
import unittest
from collections import OrderedDict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.utils import ParseException
from pyspark.sql.functions import lit

# COMMAND ----------

# モジュールをノートブックから取得するか。Falseとなる場合には、python ファイルを import する場合。
call_modules_from_noteboks = True

# ローカル開発時に利用する自作モジュールの呼び出し
try:
    sys.path.append(os.path.dirname(__file__))
    from utilities.spark_utilities__v1 import SparkUtilities
    call_modules_from_noteboks = False
except (NameError, ImportError):
    pass


# COMMAND ----------


class _TestHelper_000:
    # main_ut_start と ut_runner_start にて利用するウィジェット名をセット
    _DEFAULT_WIDGET_NAME_OF_UT_RUNNER_NOTEBOOK = 'ut_runner_notebook'
    _DEFAULT_WIDGET_NAME_OF_PARALLEL_NUM = 'parallel_num'
    _DEFAULT_WIDGET_NAME_OF_RETRY_NUM = 'retry_num'
    _DEFAULT_WIDGET_NAME_OF_TARGET_TEST_CASES = 'target_test_cases'
    _DEFAULT_WIDGET_NAME_OF_IS_OUTPUT_WITH_XML = 'is_output_with_xml'
    _DEFAULT_WIDGET_NAME_OF_XML_OUTPUT_TARGET_DIRECTORY = 'xml_output_target_directory'
    _DEFAULT_WIDGET_NAME_OF_ASSIGNED_EXECUTION_NUM = 'assigned_execution_num'

    # main_ut_start メソッドのデフォルト値をセット
    _DEFAULT_MAIN_UT_UT_RUNNER_NOTEBOOK = './ut_runner/ut_runner__001__v1'
    _DEFAULT_MAIN_UT_PARALLEL_NUM = '10'
    _DEFAULT_MAIN_UT_RETRY_NUM = '4'
    _DEFAULT_MAIN_UT_IS_OUTPUT_WITH_XML = 'False'
    _DEFAULT_MAIN_UT_XML_OUTPUT_TARGET_DIRECTORY = '/FileStore/unit/junit/test_reports'

    # ut_runner メソッドのデフォルト値をセット
    _DEFAULT_UT_RUNNER_PARALLEL_NUM = '1'
    _DEFAULT_UT_RUNNER_ASSIGNED_EXECUTION_NUM = '1'
    _DEFAULT_UT_RUNNER_TARGET_TEST_CASES = ''
    _DEFAULT_UT_RUNNER_IS_OUTPUT_WITH_XML = 'False'
    _DEFAULT_UT_RUNNER_XML_OUTPUT_TARGET_DIRECTORY = '/FileStore/ut/junit/test_reports'

    # テスト環境構築時の値をセット
    _DEFAULT_TEST_DB_PREFIX = '_test_db__'
    _DEFAULT_TEST_DBS_LOCATION = f"/{_DEFAULT_TEST_DB_PREFIX}"
    _UNITTEST_RESULTS_OUTPUT_SCHEMA = """
        unittest_runner_info string,
        testsRun int,
        test_end_timestamp string,
        target_execution_ut_cases array<string>,
        wasSuccessful boolean,
        faulures_number int,
        failures array<
            MAP<
                STRING,
                STRING
            >
        >,
        skipped_number int,
        skipped array<
            MAP<
                STRING,
                STRING
            >
        >,
        errors_number int,
        errors array<
            MAP<
                STRING,
                STRING
            >
        >,
        expectedFailures_number int,
        expectedFailures array<
            MAP<
                STRING,
                STRING
            >
        >,
        unexpectedSuccesses_number int,
        unexpectedSuccesses array<
            MAP<
                STRING,
                STRING
            >
        >
        """
    _DEFAULT_JSON_INDENT_NUM = 4
    separator = '======================================================================'
    _COL_NAME_OF__assert_spark_dataFrame_equal_datasoure = '_assert_spark_dataFrame_equal_datasoure'

# COMMAND ----------

class _TestHelper_002:
    @staticmethod
    def _get_ut_notebook_info_with_parallel(
        parallel_num,
        notebooK_parameters,
        retry_num,
        ut_runner_notebook,
    ):
        """テスト実行情報を並列数に合わせて取得する
        Args:
            parallel_num(int): テスト並列実行数
            notebook_parameters(dictionary): ウィジェットのパラメータ辞書
            retry_num(int): リトライ回数
            ut_runner_notebook(str): 実行するnotebookのパス

        Returns:
            list: widgetsから設定されたnotebookの情報
        """
        _START_NUM = 1
        stop_num = int(parallel_num) + 1
        notebooks = []
        for num_of_assigned_execution in range(_START_NUM, stop_num):
            num_of_assigned_execution_str = str(num_of_assigned_execution)
            notebooK_para_of_assigned_execution_num = notebooK_parameters.copy()
            notebooK_para_of_assigned_execution_num[
                TestHelper._DEFAULT_WIDGET_NAME_OF_ASSIGNED_EXECUTION_NUM
            ] = num_of_assigned_execution_str

            notebooks.append(
                SparkUtilities.get_dbutils_notebook_info(
                    ut_runner_notebook,
                    retry=retry_num,
                    parameters=notebooK_para_of_assigned_execution_num,
                )
            )

        return notebooks.copy()

    @staticmethod
    def main_ut_start():
        """main_ut にて最初に実行すべき処理を実施

        Returns:
            tuple: 
                ut_runner_notebook(str), 
                parallel_num(int): テストの並列実行数, 
                retry_num(int)：リトライ回数, 
                notebooK_parameters(dict)：ウィジェットのパラメータ辞書
        """
        spark = SparkSession.getActiveSession()

        # widgetの情報をセット
        widget_info = {
            TestHelper._DEFAULT_WIDGET_NAME_OF_UT_RUNNER_NOTEBOOK: TestHelper._DEFAULT_MAIN_UT_UT_RUNNER_NOTEBOOK,
            TestHelper._DEFAULT_WIDGET_NAME_OF_PARALLEL_NUM: TestHelper._DEFAULT_MAIN_UT_PARALLEL_NUM,
            TestHelper._DEFAULT_WIDGET_NAME_OF_RETRY_NUM: TestHelper._DEFAULT_MAIN_UT_RETRY_NUM,
            TestHelper._DEFAULT_WIDGET_NAME_OF_IS_OUTPUT_WITH_XML: TestHelper._DEFAULT_MAIN_UT_IS_OUTPUT_WITH_XML,
            TestHelper._DEFAULT_WIDGET_NAME_OF_XML_OUTPUT_TARGET_DIRECTORY: TestHelper._DEFAULT_MAIN_UT_XML_OUTPUT_TARGET_DIRECTORY,
        }

        # widgetを定義
        for widget_name, widget_value in widget_info.items():
            SparkUtilities.widgets_text(widget_name, widget_value)

        # グローバル変数として定義
        global ut_runner_notebook, parallel_num, retry_num, notebooK_parameters

        # グローバル変数にwidgetの値をセット
        ut_runner_notebook = SparkUtilities.widgets_get(TestHelper._DEFAULT_WIDGET_NAME_OF_UT_RUNNER_NOTEBOOK)
        parallel_num = int(SparkUtilities.widgets_get(TestHelper._DEFAULT_WIDGET_NAME_OF_PARALLEL_NUM))
        retry_num = int(SparkUtilities.widgets_get(TestHelper._DEFAULT_WIDGET_NAME_OF_RETRY_NUM))
        notebooK_parameters = {
            TestHelper._DEFAULT_WIDGET_NAME_OF_PARALLEL_NUM: parallel_num,
            TestHelper._DEFAULT_WIDGET_NAME_OF_IS_OUTPUT_WITH_XML: SparkUtilities.widgets_get(
                TestHelper._DEFAULT_WIDGET_NAME_OF_IS_OUTPUT_WITH_XML
            ),
            TestHelper._DEFAULT_WIDGET_NAME_OF_XML_OUTPUT_TARGET_DIRECTORY: SparkUtilities.widgets_get(
                TestHelper._DEFAULT_WIDGET_NAME_OF_XML_OUTPUT_TARGET_DIRECTORY
            ),
        }
        return ut_runner_notebook, parallel_num, retry_num, notebooK_parameters

    @staticmethod
    def main_ut_execution(
        parallel_num,
        notebooK_parameters,
        retry_num,
        ut_runner_notebook,
    ):
        """main__ut にて、並列でテストを実行

        Args:
            parallel_num(int): テスト並列実行数
            notebook_parameters(dictionary): ウィジェットのパラメータ辞書
            retry_num(int): リトライ回数
            ut_runner_notebook(str): # ToDo

        Returns:
            list: 並列実行した単体テストnotebookの結果
        """
        # テストを実行するノートブックの情報を取得
        notebooks_info = TestHelper._get_ut_notebook_info_with_parallel(
            parallel_num=parallel_num,
            notebooK_parameters=notebooK_parameters,
            retry_num=retry_num,
            ut_runner_notebook=ut_runner_notebook,
        )

        # ut_runner_notebookにて設定したnotebookの実行
        run_results = SparkUtilities.run_notebooks_in_pararell(
            notebooks_info=notebooks_info,
            parallel_num=parallel_num,
        )
        
        results = []
        for result in run_results:
            results.extend(json.loads(result))

        return results


    @staticmethod
    def main_ut_display_results(
        unittest_results_output,
    ):
        """main__ut にて、実行済みテスト結果を表示

        Args:
            unittest_results_output(dictionary): main_ut_execution　にて出力されるテスト結果

        """
        spark = SparkSession.getActiveSession()
        if unittest_results_output != []:
            df = spark.createDataFrame(
                unittest_results_output,
                TestHelper._UNITTEST_RESULTS_OUTPUT_SCHEMA,
            )
            SparkUtilities.display(df)

    @staticmethod
    def main_ut_end():
        """main_ut 実行後に実施する処理"""
        pass

    @staticmethod
    def ut_runner_start():
        """ut_runner にて最初に実行すべき処理を実施
        returns:
            tuple:
                parallel_num(int): テスト並列実行数
                assigned_execution_num(int) ：実行回数
                target_test_cases(str)：実行するテストケースのクラス名
                is_output_with_xml(bool)：テスト結果のxml出力オプション
                xml_output_target_directory(str)：xml出力パス
        """
        # widgetの情報をセット
        widget_info = {
            TestHelper._DEFAULT_WIDGET_NAME_OF_ASSIGNED_EXECUTION_NUM: TestHelper._DEFAULT_UT_RUNNER_ASSIGNED_EXECUTION_NUM,
            TestHelper._DEFAULT_WIDGET_NAME_OF_PARALLEL_NUM: TestHelper._DEFAULT_UT_RUNNER_PARALLEL_NUM,
            TestHelper._DEFAULT_WIDGET_NAME_OF_TARGET_TEST_CASES: TestHelper._DEFAULT_UT_RUNNER_TARGET_TEST_CASES,
            TestHelper._DEFAULT_WIDGET_NAME_OF_IS_OUTPUT_WITH_XML: TestHelper._DEFAULT_UT_RUNNER_IS_OUTPUT_WITH_XML,
            TestHelper._DEFAULT_WIDGET_NAME_OF_XML_OUTPUT_TARGET_DIRECTORY: TestHelper._DEFAULT_UT_RUNNER_XML_OUTPUT_TARGET_DIRECTORY,
        }

        # widgetを定義
        for widget_name, widget_value in widget_info.items():
            SparkUtilities.widgets_text(widget_name, widget_value)

        # グローバル変数として定義
        global parallel_num, assigned_execution_num, target_test_cases, is_output_with_xml, xml_output_target_directory

        # グローバル変数にwidgetの値をセット
        parallel_num = int(SparkUtilities.widgets_get(TestHelper._DEFAULT_WIDGET_NAME_OF_PARALLEL_NUM))
        assigned_execution_num = int(
            SparkUtilities.widgets_get(TestHelper._DEFAULT_WIDGET_NAME_OF_ASSIGNED_EXECUTION_NUM)
        )
        target_test_cases = SparkUtilities.widgets_get(TestHelper._DEFAULT_WIDGET_NAME_OF_TARGET_TEST_CASES)
        is_output_with_xml = eval(SparkUtilities.widgets_get(TestHelper._DEFAULT_WIDGET_NAME_OF_IS_OUTPUT_WITH_XML))
        xml_output_target_directory = SparkUtilities.widgets_get(
            TestHelper._DEFAULT_WIDGET_NAME_OF_XML_OUTPUT_TARGET_DIRECTORY
        )

        return parallel_num, assigned_execution_num, target_test_cases, is_output_with_xml, xml_output_target_directory

    @staticmethod
    def _get_unittest_detail_results_by_status(
        unittest_status_runner_results,
    ):
        """テスト結果から必要な情報を保持した辞書型リストをリターン
        args:
            unittest_status_runner_results(dict): テスト結果
        returns: 
            list: テスト実行結果の詳細
        """
        ut_result_detail = []
        for result in unittest_status_runner_results:
            if isinstance(result, tuple):
                # ToDo solve error
#                 test_method_name = result[0]._testMethodName
#                 test_method_doc = None
#                 if result[0]._testMethodDoc is not None:
#                     test_method_doc = result[0]._testMethodDoc.strip()
#                 message = result[1]
#                 ut_result_detail.append(
#                     {
#                         '_testMethodName': test_method_name,
#                         '_testMethodDoc': test_method_doc,
#                         'message': message,
#                     }
#                 )
                pass
            else:
                    test_method_name = result._testMethodName
                    test_method_doc = None
                    if result._testMethodDoc is not None:
                        test_method_doc = result._testMethodDoc.strip()
                    ut_result_detail.append(
                    {
                        '_testMethodName': test_method_name,
                        '_testMethodDoc': test_method_doc,
                    }
                )

        return ut_result_detail

    def _get__ut_cases(
        target_test_cases,
        current_globals,
        unittest_test_case = unittest.TestCase,
    ):
        """単体テストのテストケースの辞書を取得する
            {テストケースメソッド名： テストケースメソッドのインスタンス}
        
        Args:
            target_test_cases(str): 対象テストケースのメソッド名をカンマ区切りで記載した文字列
            current_globals(class): 対象とするテストケースの親クラス
            unittest_test_case: unittest.TestCaseインスタンス
            
        Returns:
            list: テストケースメソッドのインスタンスリスト

        Raises:
            Exception: テストケースとして定義されていない場合、あるいは、テストケースではないオブジェクトが指定された場合にエラーとする
        """
        tgt_ut_cases = []
        
        # テストクラスの指定がない場合には、 unittest.TestCase のサブクラスのリストをリターン
        if target_test_cases == '':           
            for current_obj_value in current_globals.values():
                current_globals = current_globals.copy()
                if isinstance(current_obj_value, type) and issubclass(current_obj_value, unittest_test_case):
                    tgt_ut_cases.append(current_obj_value)

        # テストクラスの指定がある場合には、テストクラスのリストをリターン
        else:
            for ut_class_name in target_test_cases.split(','):
                ut_class = current_globals.get(ut_class_name)
                if not (isinstance(ut_class, type) and issubclass(ut_class, unittest_test_case)):
                    raise Exception(f"The `{ut_class_name}` specified in target_test_cases is either undefined or not a test case.")
                tgt_ut_cases.append(ut_class)

        return tgt_ut_cases

    def _split__ut_cases(
        tgt_ut_cases,
        parallel_num,
        assigned_execution_num,
    ):
        """並列実行数(parallel_num)に応じてテストメソッドを分割
        
        Args:
            tgt_ut_cases(list): 分割対象となるテストケースのリスト
            parallel_num(int): テストケースの分割数
            assigned_execution_num(int): 分割されたうちの何番目を返すか指定
            
        Returns:
            list: 割り当て実行番号に応じてスライスしたテストケースのリスト
        """
        
        ## 総テストケース数をセット
        test_cases_num = len(tgt_ut_cases)

        if parallel_num <= 1:
            assigned_ut_cases = tgt_ut_cases
        else:
            execution_num = math.ceil(test_cases_num / parallel_num)
            start_num = execution_num * (assigned_execution_num - 1)
            end_num = execution_num * assigned_execution_num
            
            ## 実施対象テストケースの並び替えを実施
            tgt_ut_cases.sort(key=str)
            assigned_ut_cases = tgt_ut_cases[start_num:end_num]

        return assigned_ut_cases

    def _execute__ut_cases(
        tgt_execution_ut_cases,
        unittest_verbosity = 1,
        is_output_with_xml = False,
        xml_output_target_directory='/dbfs/FileStore/ut/junit/test_reports',
        has_run_as_a_single_test_case = False,
        text_test_runner_stream = None,
    ):
        """unittest の runner を実行
        Args: 
            tgt_execution_ut_cases(list): 実行対象の単体テストケースのインスタンスリスト
            unittest_verbosity(int, optional): unittest.TextTestRunner の引数である verbosity と同等 Defaults to 1
            is_output_with_xml(bool, optional): テスト結果の xml を出力する Defaults to False
            xml_output_target_directory(str, optional): テスト結果の xml 保存先ディレクトリ  Defaults to '/dbfs/FileStore/ut/junit/test_reports'
            has_run_as_a_single_test_case(bool, optional): 複数のテストケースをまとめて実行するか Defaults to False
            text_test_runner_stream(str, optional): unittest.TextTestRunner の引数である stream と同等 Defaults to None
            
        Returns: 
            list: unittest の実行結果のリスト
        """
        if is_output_with_xml:
            # XMLで出力する際には、`unittest-xml-reporting`を利用
            import xmlrunner

            runner = xmlrunner.XMLTestRunner(
                output = xml_output_target_directory,
                verbosity = unittest_verbosity,
                stream = text_test_runner_stream,
            )
        else:
            runner = unittest.TextTestRunner(
                verbosity=unittest_verbosity,
                stream = text_test_runner_stream,
            )
        a = TestHelper._output_ut_result
        print(a)

        # unittest のテストを実行
        unittest_results = []
        if not has_run_as_a_single_test_case:
            for tgt_execution_ut_case in tgt_execution_ut_cases:
                test_suite = unittest.TestLoader().loadTestsFromTestCase(tgt_execution_ut_case)
                unittest_result = runner.run(test_suite)
                unittest_results.extend(
                    TestHelper._output_ut_result(
                        [tgt_execution_ut_case],
                        [unittest_result],
                    )
                )
        else:
            test_suite = unittest.TestSuite()
            for case in tgt_execution_ut_cases:
                test_suite.addTest(unittest.makeSuite(case))

            unittest_result = runner.run(test_suite)
            unittest_results.extend(
                TestHelper._output_ut_result(
                    tgt_execution_ut_cases,
                    [unittest_result],
                )
            )

        return unittest_results

    def _output_ut_result(
        tgt_execution_ut_cases,
        unittest_results,
        current_timestamp = datetime.datetime.now(),
    ):
        """単体テスト結果の出力を行う
        
        Args:
            tgt_execution_ut_cases(list): 実行対象のテストケースメソッド
            unittest_results(list): 単体テストの実行結果
            current_timestamp(datetime, optional): 出力結果に記載するタイムスタンプ
            
        Returns:
            list: 実行結果の出力
        """
        unittest_results_output = []
        current_timestamp_str = str(current_timestamp)

        for result in unittest_results:
            test_result_info = OrderedDict(
                {
                    'unittest_runner_info': f'{result}',
                    'testsRun': result.testsRun,
                    'test_end_timestamp': current_timestamp_str,
                    'target_execution_ut_cases': [str(case) for case in tgt_execution_ut_cases],
                    #テストの実行結果
                    'wasSuccessful': result.wasSuccessful(),
                    # テストの失敗関連
                    'faulures_number': len(result.failures),
                    'failures': TestHelper._get_unittest_detail_results_by_status(result.failures),
                    # テストのスキップ関連
                    'skipped_number': len(result.skipped),
                    'skipped': TestHelper._get_unittest_detail_results_by_status(result.skipped),
                    # エラー関連
                    'errors_number': len(result.errors),
                    'errors': TestHelper._get_unittest_detail_results_by_status(result.errors),
                    # expectedFailures 関連
                    'expectedFailures_number': len(result.expectedFailures),
                    'expectedFailures': TestHelper._get_unittest_detail_results_by_status(result.expectedFailures),
                    # unexpectedSuccesses 関連
                    'unexpectedSuccesses_number': len(result.unexpectedSuccesses),
                    'unexpectedSuccesses': TestHelper._get_unittest_detail_results_by_status(
                        result.unexpectedSuccesses
                    ),
                }
            )

            unittest_results_output.append(test_result_info)

        return unittest_results_output

    @staticmethod
    def _raise_error_when_unittest_is_not_success(
        unittest_results_output
    ):
        """テスト失敗時に例外を発生させる
        Args:
            unittest_results_output(list): TestHelper._output_ut_resultの実行結果
        """
        contains_errors = False in [result.get('wasSuccessful') for result in unittest_results_output]
        if contains_errors:
            not_successful_results = [result for result in unittest_results_output if result.get('wasSuccessful') is False]
            spark = SparkSession.getActiveSession()
            unitetest_results_df = spark.createDataFrame(
                not_successful_results,
                TestHelper._UNITTEST_RESULTS_OUTPUT_SCHEMA,
            )
            SparkUtilities.display(unitetest_results_df)
            raise Exception("The unittest results contain errors.")

    @staticmethod
    def ut_runner_execution(
        assigned_execution_num=1,
        parallel_num=1,
        target_test_cases='',
        unittest_verbosity = 2,
        is_output_with_xml = False,
        xml_output_target_directory = '/dbfs/FileStore/ut/junit/test_reports',
        has_run_as_a_single_test_case = False,
        current_globals = globals(),
        unittest = unittest,
        should_raise_error_when_not_successful = False,
    ):
        """テストメソッドを実行
        
        Args:
            assigned_execution_num(int, optional): 分割されたうちの何番目を返すか指定 Defaults to 1
            parallel_num(int, optional): テストケースの分割数 Defalts to 1
            target_test_cases(str, optional): 実行対象のテストケースのリスト Defaults to ''
            unittest_verbosity(int, optional): 冗長性 Defaults to 2
            is_output_with_xml(bool, optional): テスト結果の xml を出力する Defaluts to False
            xml_output_target_directory(str, optional): テスト結果の xml 保存先ディレクトリ Defaults to '/dbfs/FileStore/ut/junit/test_reports'
            has_run_as_a_single_test_case(bool, optional): 複数のテストケースをまとめて実行するか Defaults to False
            current_globals(dict, optional): 実行時点での globals の実行結果 Defaults to globals()
            unittest(unittest, optional): unittest のインスタンス Defaluts to unittest
            should_raise_error_when_not_successful(bool, optional): unittest の実行結果に成功でないものが含まれる場合にエラーとするか Defaults to False
            
        Returns:
            list: unittest の実行結果
        """
        # テストケース取得 -> 並列数に応じて分割 -> 実行 -> 結果表示
        tgt_ut_cases = TestHelper._get__ut_cases(
            target_test_cases = target_test_cases,
            current_globals = current_globals,
            unittest_test_case = unittest.TestCase,
        )

        tgt_execution_ut_cases = TestHelper._split__ut_cases(
            tgt_ut_cases = tgt_ut_cases,
            parallel_num = parallel_num,
            assigned_execution_num = assigned_execution_num,
        )

        unittest_results = TestHelper._execute__ut_cases(
            tgt_execution_ut_cases = tgt_execution_ut_cases,
            unittest_verbosity = unittest_verbosity,
            is_output_with_xml = is_output_with_xml,
            xml_output_target_directory = xml_output_target_directory,
            has_run_as_a_single_test_case = has_run_as_a_single_test_case,
        )

        if should_raise_error_when_not_successful:
            TestHelper._raise_error_when_unittest_is_not_success(unittest_results)

        return unittest_results

    @staticmethod
    def ut_runner_end(unittest_results_output):
        """実行結果をjson形式で返す
        Args:
            unittest_results_output (list): unittest の実行結果。 ut_runner_execution　のリターン値
        
        Returns:
            str : テストの実行結果 json 文字列
        """
        SparkUtilities.exit_notebook(
            json.dumps(
                unittest_results_output,
                indent=TestHelper._DEFAULT_JSON_INDENT_NUM,
            )
        )

    @staticmethod
    def get_test_method_name(
        expcted_method_name_prefix = 'test',
        should_contain_random_stirng_suffix = True,
        random_stirng_suffix_length = 10,
    ):
        """テストメソッド名を、ランダムな文字例を含めて返す。
        Args:
            expcted_method_name_prefix (str, optional): 想定のテストメソッド名の説頭語 Defaults to 'test'
            should_contain_randam_stirng_suffix (Bool, optional): ランダムな文字例の説頭語を含めるかどうか。 Defaults to False
            random_stirng_suffix_length (int, optional): ランダムな文字例の文字数。Defaults to 10

        Raises:
            Exception: `expcted_method_name_prefix` （想定のテストメソッド名の説頭語）でない場合のエラー。

        Returns:
            str : テストメソッド名
        """
        called_method_index_number = 1
        method_name_index_number = 0
        method_name = inspect.stack()[called_method_index_number][method_name_index_number].f_code.co_name

        if not method_name.startswith(expcted_method_name_prefix):
            raise Exception(f"The method name is incorrect. The method name should start with the word `{expcted_method_name_prefix}`.current name : {method_name}")

        if should_contain_random_stirng_suffix:
            method_name_suffix = ''.join([random.choice(string.ascii_lowercase) for i in range(random_stirng_suffix_length)])
            method_name = method_name + "__" + method_name_suffix

        return method_name


# COMMAND ----------


class TestHelper(
    _TestHelper_000,
    _TestHelper_002,
):
    pass

# COMMAND ----------

import inspect
import json
import os
from concurrent.futures import ThreadPoolExecutor

from pyspark.sql import DataFrame, SparkSession

# Databricksでのみ利用できるライブラリを呼び出し
try:
    from pyspark.dbutils import DBUtils
except ImportError:
    pass


# COMMAND ----------

class SparkUtilities:
    _spark_servies = 'databricks'  # databrick,synapse, or local
    _spark_servies_databricks = 'databricks'
    _spark_servies_azure_synapse = 'synapse'
    _CHECK_CONSTRAINT_KEY_PREFIX = 'delta.constraints.'

    # `get_table_location`メソッドにて削除対象の説頭語
    _DELETED_TBL_LOCATION_PROTOCOLS_PREFIX = ['dbfs:', 'abfss:', 'wasbs:']

    @staticmethod
    def display(df: DataFrame):
        """DataFrameをコンソールに表示する

        args:
          df(DataFrame): 出力するデータフレーム
        """
        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_databricks:
            if not SparkUtilities.get_has_executed_on_local():
                display(df)
            else:
                df.show()

        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_azure_synapse:
            # display.config('0') と display.execute('0')については、2021年11月までの暫定対応。その後は不要となる可能性あり。
            display.config('0')
            display(df)
            display.execute('0')
            
    @staticmethod
    def run_notebook(
        path: str,
        timeout_seconds: int,
        arguments: dict,
    ):
        """Notebookを実行する

        args:
            path(string): 実行するNotebookのパス
            timeout_seconds(int): タイムアウト(秒)
            arguments(dict): Notebookの引数(widget)

        returns:
            Notebook実行結果
        """
        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_databricks:
            spark = SparkSession.getActiveSession()
            dbutils = DBUtils(spark)
            return dbutils.notebook.run(path, timeout_seconds, arguments)

        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_azure_synapse:
            # todo
            return None

    @staticmethod
    def exit_notebook(result):
        """ノートブックの実行を終了させ、指定値をリターン

        args:
            result(string): 終了時のリターン値
        """
        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_databricks:
            spark = SparkSession.getActiveSession()
            dbutils = DBUtils(spark)
            dbutils.notebook.exit(result)

        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_azure_synapse:
            # todo
            mssparkutils.notebook.exit(result)

    @staticmethod
    def get_dbutils_notebook_info(
        notebook_path,
        timeout=1200,
        parameters=None,
        retry=0,
    ):
        """Notebook 実行パラメータを辞書型で返す

        args:
            notebook_path(string):
            timeout(int, optional): default=1200
            parameters(dict, optional): default=None
            retry(int, optional): リトライ回数 default=0

        return:
            dict: Notebook実行パラメータの辞書
        """
        return {
            'notebook_path': notebook_path,
            'timeout': timeout,
            'parameters': parameters,
            'retry': retry,
        }

    @staticmethod
    def submit_notebook(notebook):
        """Notebookを実行する

        args:
            notebook(dict): {'notebook_path', 'timeout', 'parameters', 'retry'} をキーに持つ辞書

        returns:
            Notebook 実行結果
        """
        try:
            if notebook.get('parameters'):
                return SparkUtilities.run_notebook(
                    notebook.get('notebook_path'), notebook.get('timeout'), notebook.get('parameters')
                )
            else:
                return SparkUtilities.run_notebook(notebook.get('notebook_path'), notebook.get('timeout'), {})
        except Exception:
            if notebook.get('retry') < 1:
                raise
            notebook['retry'] = notebook.get('retry') - 1
            SparkUtilities.submit_notebook(notebook)

    @staticmethod
    def run_notebooks_in_pararell(
        notebooks_info,
        parallel_num,
        timeout=3600,
    ):
        """Notebook を並列実行する

        args:
            notebooks_info(list): {notebook_path, timeout, parameters, retry} をキーに持つ辞書のリスト
            parallel_num(int): 並列実行数
            timeout(int, optional): タイムアウト(ms)

        returns:
            list: 実行結果のリスト
        """
        with ThreadPoolExecutor(max_workers=parallel_num) as ec:
            submited_notebooks = [ec.submit(SparkUtilities.submit_notebook, notebook) for notebook in notebooks_info]
        return [l.result(timeout=timeout) for l in submited_notebooks]

    @staticmethod
    def get_or_create_sparksession():
        """SparkSession を取得するか、既存のものがなければ作成する

        returns:
            SparkSession
        """
        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_databricks:
            return SparkSession.builder.getOrCreate()

        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_azure_synapse:
            return SparkSession.builder.getOrCreate()

    @staticmethod
    def widgets_text(
        key: str,
        value: str,
    ):
        """テキスト入力ウィジェットを作成する

        args:
            key(string): ウィジェットの名前
            value(string): ウィジェットのデフォルト値
        """
        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_databricks:
            spark = SparkSession.getActiveSession()
            if not SparkUtilities.get_has_executed_on_local():
                dbutils = DBUtils(spark)
                dbutils.widgets.text(key, value)
            else:
                os.environ[key] = value

        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_azure_synapse:
            # todo
            todo = True

    @staticmethod
    def widgets_get(key: str):
        """ウィジェットの値を取得する

        args:
            key(string): ウィジェット名

        returns:
            any: ウィジェットの現在値、またはデフォルト値
        """
        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_databricks:
            spark = SparkSession.getActiveSession()
            if not SparkUtilities.get_has_executed_on_local():
                dbutils = DBUtils(spark)
                return dbutils.widgets.get(key)
            else:
                return os.getenv(key)

        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_azure_synapse:
            # todo
            return None

    @staticmethod
    def widgets_remove(key: str):
        """ウィジェットを削除する

        args:
            key(string): ウィジェット名

        returns:
            any: ウィジェット削除後のリターン結果
        """
        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_databricks:
            spark = SparkSession.getActiveSession()
            if not SparkUtilities.get_has_executed_on_local():
                dbutils = DBUtils(spark)
                return dbutils.widgets.remove(key)
            else:
                return os.getenv(key)

        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_azure_synapse:
            # todo
            return None

    @staticmethod
    def get_has_executed_on_local():
        """ローカル環境からの実行であるかを確認

        returns:
            bool: ローカル環境からの実行であるか(`True`)、ローカル環境以外からの実行であるか(`False`)
        """
        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_databricks:
            spark = SparkSession.getActiveSession()

            # ローカル環境から実行されている場合には、 local ではじまる値を取得可能
            return SparkUtilities.get_spark_conf("spark.master").startswith("local")

        if SparkUtilities._spark_servies == SparkUtilities._spark_servies_azure_synapse:
            # todo
            todo = True

    @staticmethod
    def get_spark_conf(key):
        """キーをもとに Spark の構成値を取得

        args:
            key(string): spark config のキー

        returns:
            string: spark config のキーの現在の設定値
        """
        spark = SparkSession.getActiveSession()
        return spark.conf.get(key)

