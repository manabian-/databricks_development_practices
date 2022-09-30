# Databricks notebook source
class samples:
    @staticmethod
    def append_to_table(
        source_df,
        target_database_name,
        target_table_name,
    ):
        """データフレームをターゲットのテーブルにappendする関数"""
        tgt_tble_name = f'{target_database_name}.{target_table_name}'

        (source_df.write.format('delta').mode('append').saveAsTable(tgt_tble_name))
