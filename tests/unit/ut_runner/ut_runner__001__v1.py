# Databricks notebook source
# MAGIC %python
# MAGIC # install unittest-xml-reporting
# MAGIC # `unittest-xml-reporting`のインストール（XMLでエクスポートしない場合にはコメントアウト）
# MAGIC %pip install unittest-xml-reporting -q

# COMMAND ----------

# MAGIC %run ../utilities__test_helper

# COMMAND ----------

TestHelper.ut_runner_start()

# COMMAND ----------

# 単体テストの スイートの呼び出し

# COMMAND ----------

# MAGIC %run ../ut_suite/ut_suite__001

# COMMAND ----------

unittest_results_output = TestHelper.ut_runner_execution(
    parallel_num=parallel_num,
    assigned_execution_num=assigned_execution_num,
    target_test_cases=target_test_cases,
    unittest=unittest,
    is_output_with_xml=is_output_with_xml,
    xml_output_target_directory=xml_output_target_directory,
)

# COMMAND ----------

TestHelper.ut_runner_end(unittest_results_output)
