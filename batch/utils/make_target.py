from ..lib.target_settings import(
    PATH_TARGET_PARAMETER, PATH_TARGET_ASSET_PROFIT,
    PATH_TARGET_BALANCE, PATH_TARGET_RATE, PATH_TARGET_INITIAL_VALUE
)
from ..lib.file_io import load_parquet, save_parquet
from ..lib.target_balance_cal import build_balance_target
from ..lib.target_asset_cal import build_asset_profit_target
from ..lib.main_helper import safe_load_master, get_value_as_str
from ..lib import reference_data_store as urds
import pandas as pd
import numpy as np

PATHS = {
    "target_balance_parameter": PATH_TARGET_PARAMETER,
    "target_rate": PATH_TARGET_RATE,
    "target_initial_value": PATH_TARGET_INITIAL_VALUE,
}

def make_target_main():
    try:
        # ---- load masters safely ----
        masters = safe_load_master({
            "target_balance_parameter": lambda: load_parquet(PATHS["target_balance_parameter"]),
            "target_rate": lambda: load_parquet(PATHS["target_rate"]),
            "target_initial_value": lambda: load_parquet(PATHS["target_initial_value"])
        })
        urds.df_target_balance_parameter = masters["target_balance_parameter"]
        urds.df_target_rate = masters["target_rate"]
        urds.df_target_initial_value = masters["target_initial_value"]

        df = urds.df_target_initial_value.copy()

        # ---- extract parameters safely ----
        start_date = get_value_as_str(df, "開始日")
        end_date = get_value_as_str(df, "終了日")
        initial_asset = get_value_as_str(df, "開始資産額")
        initial_loan = get_value_as_str(df, "ローン残高")
        try:
            initial_asset = float(initial_asset)
            initial_loan = float(initial_loan)
        except ValueError:
            raise ValueError(f"初期値が数値に変換できません: {initial_asset}, {initial_loan}")

        # ---- balance cal ----
        df_balance = build_balance_target(
            urds.df_target_balance_parameter,
            start_date,
            end_date
        )
        # ---- asset profit cal ----
        df_asset_profit = build_asset_profit_target(
            df_balance,
            start_date,
            end_date,
            initial_asset,
            initial_loan
        )

        # ---- save ----
        save_parquet(df_balance, PATH_TARGET_BALANCE)
        save_parquet(df_asset_profit, PATH_TARGET_ASSET_PROFIT)

    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    make_target_main()
