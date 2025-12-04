from ..lib.file_io import load_parquet, save_parquet
from ..lib.main_helper import safe_load_master, safe_pipe
from ..lib import reference_data_store as urds

from ..lib.agg_init import get_latest_date_agg, load_balance_raw_file
from ..lib.agg_settings import (
    PATH_BALANCE_TYPE_AND_CATEGORY, PATH_ASSET_PROFIT_DETAIL, PATH_BALANCE_RAW_DATA,
    PATH_BALANCE_DETAIL, PATH_ASSET_PROFIT_DETAIL_TEST
)
from ..lib.target_settings import PATH_TARGET_BALANCE

from ..lib.agg_balance_collection import filter_and_clean_raw, collect_balance,\
    collect_living_adjust, collect_year_end_tax_adjustment, collect_points
from ..lib.agg_balance_finalize import finalize_data

import pandas as pd
from ..lib.exceptions import DataLoadError

PATHS = {
    "balance_type_category": PATH_BALANCE_TYPE_AND_CATEGORY,
    "asset_profit": PATH_ASSET_PROFIT_DETAIL_TEST,
    "balance_target": PATH_TARGET_BALANCE
}
PATH_OUTPUT = PATH_BALANCE_DETAIL
START_DATE = pd.to_datetime("2024/10/01")

def make_balance_main():
    try:
        # ---- load masters safely ----
        masters = safe_load_master({
            "balance_type_category": lambda: load_parquet(PATHS["balance_type_category"]),
            "asset_profit": lambda: load_parquet(PATHS["asset_profit"]),
            "balance_target": lambda: load_parquet(PATHS["balance_target"]),
        })

        urds.df_balance_type_and_category = masters["balance_type_category"]
        df_asset_profit = masters["asset_profit"]
        urds.df_balance_target = masters["balance_target"]

        # ---- date range ----
        end_date = get_latest_date_agg(df_asset_profit)
        if pd.isna(end_date):
            raise DataLoadError("df_asset_profit に有効な日付がありません")

        # ---- raw balance load ----
        df_balance_raw = load_balance_raw_file(start_year=2024, end_year=end_date.year+1, path=PATH_BALANCE_RAW_DATA)
        df_balance_raw_filtered = filter_and_clean_raw(start_date=START_DATE, end_date=end_date, df=df_balance_raw)

        # ---- balance detail calculation ----
        df_balance_detail = pd.DataFrame()
        df_pre = (
            df_balance_detail
            .pipe(safe_pipe(collect_balance, df_balance_raw_filtered))
            .pipe(safe_pipe(collect_living_adjust))
            .pipe(safe_pipe(collect_year_end_tax_adjustment, START_DATE, end_date))
            .pipe(safe_pipe(collect_points, df_asset_profit))
        )
        # ---- finalize & save ----
        df_final = finalize_data(START_DATE, end_date, df_pre)
        df_final.sort_values("date", inplace=True)

        save_parquet(df_final, PATH_OUTPUT)
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    make_balance_main()
