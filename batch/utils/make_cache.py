from batch.lib.agg_settings import (
    PATH_ASSET_PROFIT_DETAIL_TEST2, PATH_BALANCE_DETAIL,
    PATH_ASSET_CACHE_DAILY, PATH_ASSET_CACHE_MONTHLY, PATH_ASSET_CACHE_YEARLY,
    PATH_CATEGORY_CACHE_DAILY, PATH_CATEGORY_CACHE_MONTHLY, PATH_CATEGORY_CACHE_YEARLY,
)
from batch.lib.target_settings import PATH_TARGET_ASSET_PROFIT
from batch.lib.file_io import load_parquet, save_parquet
from batch.lib.main_helper import safe_load_master, safe_pipe
from batch.lib.agg_init import get_latest_date_agg

from batch.lib.cache_table_cal import (
    make_asset_cache_daily, make_asset_cache_monthly, make_asset_cache_yearly,
    make_category_cache_daily, make_category_cache_monthly, make_category_cache_yearly,
)

import pandas as pd

PATHS = {
    "asset_profit": PATH_ASSET_PROFIT_DETAIL_TEST2,
    "balance": PATH_BALANCE_DETAIL,
    "target": PATH_TARGET_ASSET_PROFIT
}
PATH_OUTPUT = {
    "asset_cache_daily": PATH_ASSET_CACHE_DAILY,
    "asset_cache_monthly": PATH_ASSET_CACHE_MONTHLY,
    "asset_cache_yearly": PATH_ASSET_CACHE_YEARLY,
    "category_cache_daily": PATH_CATEGORY_CACHE_DAILY,
    "category_cache_monthly": PATH_CATEGORY_CACHE_MONTHLY,
    "category_cache_yearly": PATH_CATEGORY_CACHE_YEARLY,
}
def make_cache_table_by_asset_name(df_asset_profit, start_date, start_date_monthly_yearly, end_date):
    df_asset_profit_daily = make_asset_cache_daily(df_asset_profit, start_date, end_date)

    prev_month_end = pd.to_datetime(end_date) - pd.offsets.MonthEnd(1)

    df_asset_profit_monthly = make_asset_cache_monthly(df_asset_profit, start_date_monthly_yearly, prev_month_end)
    df_asset_profit_yearly = make_asset_cache_yearly(df_asset_profit, start_date_monthly_yearly, prev_month_end)
    
    return df_asset_profit_daily, df_asset_profit_monthly, df_asset_profit_yearly

def make_cache_table_by_asset_category(df_asset_profit, df_balance, df_target, start_date, start_date_monthly_yearly, end_date):
    df_asset_category_daily = make_category_cache_daily(df_asset_profit, df_balance, df_target, start_date, end_date)
    
    prev_month_end = pd.to_datetime(end_date) - pd.offsets.MonthEnd(1)
    
    df_asset_category_monthly = make_category_cache_monthly(df_asset_profit, df_balance, df_target, start_date_monthly_yearly, prev_month_end)
    df_asset_category_yearly = make_category_cache_yearly(df_asset_profit, df_balance, df_target, start_date_monthly_yearly, prev_month_end)

    return df_asset_category_daily, df_asset_category_monthly, df_asset_category_yearly

def make_cache_main():
    #マスターファイルを読み込む
    try:
        # ---- load masters safely ----
        masters = safe_load_master({
            "asset_profit": lambda: load_parquet(PATHS["asset_profit"]),
            "balance": lambda: load_parquet(PATHS["balance"]),
                "target": lambda: load_parquet(PATHS["target"]),
        })

        df_asset_profit = masters["asset_profit"]
        df_balance = masters["balance"]
        df_target = masters["target"]

        # ---- date range ----
        end_date = get_latest_date_agg(df_asset_profit)
        if pd.isna(end_date):
            raise DataLoadError("df_asset_profit に有効な日付がありません")
        start_date = max(
            (end_date - pd.DateOffset(years=1)).replace(day=1),
            pd.Timestamp("2024-10-01")
        )
        start_date_monthly_yearly = max(
            (end_date - pd.DateOffset(years=12)).replace(day=1),
            pd.Timestamp("2024-10-01")
        )

        # ---- make cache ----
        df_asset_profit_daily, df_asset_profit_monthly, df_asset_profit_yearly = \
            make_cache_table_by_asset_name(
                df_asset_profit, start_date, start_date_monthly_yearly, end_date
            )

        df_asset_category_daily, df_asset_category_monthly, df_asset_category_yearly = \
            make_cache_table_by_asset_category(
                df_asset_profit, df_balance, df_target, start_date, start_date_monthly_yearly, end_date
            )
        
        # ---- save ----
        save_parquet(df_asset_profit_daily, PATH_OUTPUT["asset_cache_daily"])
        save_parquet(df_asset_profit_monthly, PATH_OUTPUT["asset_cache_monthly"])
        save_parquet(df_asset_profit_yearly, PATH_OUTPUT["asset_cache_yearly"])
        save_parquet(df_asset_category_daily, PATH_OUTPUT["category_cache_daily"])
        save_parquet(df_asset_category_monthly, PATH_OUTPUT["category_cache_monthly"])
        save_parquet(df_asset_category_yearly, PATH_OUTPUT["category_cache_yearly"])
    
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    
    make_cache_main()
