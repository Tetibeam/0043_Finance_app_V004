from ..lib.file_io import load_parquet, load_csv, save_parquet
from ..lib import reference_data_store as urds
from ..lib.main_helper import safe_load_master, safe_pipe
from ..lib.exceptions import DataLoadError

from ..lib.agg_settings import (
    PATH_ASSET_PROFIT_DETAIL, PATH_OFFSET_UNREALIZED, 
    PATH_BALANCE_RAW_DATA,PATH_ASSET_TYPE_AND_CATEGORY, PATH_BALANCE_DETAIL,
    PATH_ASSET_PROFIT_DETAIL_TEST, PATH_ASSET_PROFIT_DETAIL_TEST2
)
from ..lib.agg_profit_cal import (
    set_unrealized_profit, set_realized_deposit, set_realized_mrf, set_realized_interest,
    set_realized_dividend_and_capital,set_realized_cloud_funds, set_total_returns, set_loan_balance
)
from ..lib.agg_balance_collection import filter_and_clean_raw
from ..lib.agg_init import load_balance_raw_file, get_latest_date_agg

import pandas as pd

PATHS = {
    "asset_type_and_category": PATH_ASSET_TYPE_AND_CATEGORY,
    "offset_unrealized": PATH_OFFSET_UNREALIZED,
    "asset_profit": PATH_ASSET_PROFIT_DETAIL_TEST,
    "balance": PATH_BALANCE_DETAIL
}
PATH_OUTPUT = PATH_ASSET_PROFIT_DETAIL_TEST2

START_DATE = pd.to_datetime("2024/10/01")

def make_profit_main():
    try:
        # ---- load masters safely ----
        masters = safe_load_master({
            "asset_type_and_category": lambda: load_csv(PATHS["asset_type_and_category"]),
            "offset_unrealized": lambda: load_parquet(PATHS["offset_unrealized"]),
            "asset_profit": lambda: load_parquet(PATHS["asset_profit"]),
            "balance": lambda: load_parquet(PATHS["balance"]),
        })
        urds.df_asset_type_and_category = masters["asset_type_and_category"]
        urds.df_offset_unrealized = masters["offset_unrealized"]
        df_asset_profit = masters["asset_profit"]
        df_balance = masters["balance"]

        # ---- date range ----
        end_date = get_latest_date_agg(df_asset_profit)
        if pd.isna(end_date):
            raise DataLoadError("df_asset_profit に有効な日付がありません")

        # ---- raw balance load ----
        df_balance_raw = load_balance_raw_file(start_year=2024, end_year=end_date.year+1, path=PATH_BALANCE_RAW_DATA)
        df_balance_raw_filtered = filter_and_clean_raw(start_date=START_DATE, end_date=end_date, df=df_balance_raw)

        # ---- profit calculation pipeline ----
        df_all_profit = (
            df_asset_profit
            .pipe(safe_pipe(set_unrealized_profit, debug=False))
            .pipe(safe_pipe(set_realized_deposit, df_balance_raw_filtered, debug=False))
            .pipe(safe_pipe(set_realized_mrf, debug=False))
            .pipe(safe_pipe(set_realized_interest, df_balance_raw_filtered, debug=False))
            .pipe(safe_pipe(set_realized_dividend_and_capital, df_balance_raw_filtered, debug=False))
            .pipe(safe_pipe(set_realized_cloud_funds, START_DATE, end_date, df_balance_raw_filtered, debug=False))
            .pipe(safe_pipe(set_total_returns, debug=False))
            .pipe(safe_pipe(set_loan_balance, START_DATE, end_date, df_balance, debug=False))
        )
        df_all_profit.sort_values("date", inplace=True)
        df_all_profit.reset_index(drop=True, inplace=True)

        # ---- save ----
        save_parquet(df_all_profit, PATH_OUTPUT)
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    make_profit_main()
