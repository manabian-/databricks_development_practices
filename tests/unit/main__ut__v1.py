# Databricks notebook source
# MAGIC %run ../../src/utilities__v1

# COMMAND ----------

TestHelper.main_ut_start()

# COMMAND ----------

unittest_results_output = TestHelper.main_ut_execution(
    parallel_num,
    notebooK_parameters,
    retry_num,
    ut_runner_notebook,
)

# COMMAND ----------

TestHelper.main_ut_display_results(unittest_results_output)

# COMMAND ----------

TestHelper.main_ut_end()
