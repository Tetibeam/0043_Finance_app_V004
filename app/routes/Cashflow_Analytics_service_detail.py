from app.utils.data_loader import (
    get_latest_date,
    query_table_date_filter,
    query_table_aggregated,
    get_raw_table
)
import pandas as pd

def read_table_from_db():

    # 12か月前の月初を計算
    latest_date = get_latest_date()
    start_date = max(
        (latest_date - pd.DateOffset(months=12)).replace(day=1),
        pd.to_datetime("2024-10-01")
    )
    df_balance = query_table_date_filter("balance_detail", start_date, latest_date)
    #print(df_balance)
    
    # atrribute
    df_item_attribute = get_raw_table("item_attribute")
    
    # 最新の生活防衛資金
    sub_types = df_item_attribute.loc[df_item_attribute["資産目的"] == "Emergency Buffer","項目"].unique().tolist()
    
    df_emergency_buffer = query_table_aggregated(
        table_name="asset_profit_detail",
        aggregates={
            "資産額": "SUM",
        },
        group_by=["date"],
        start_date=latest_date-pd.DateOffset(months=7),
        end_date=latest_date,
        filters={"資産サブタイプ": sub_types},
        order_by=["date"]
    )
    #print(df_emergency_buffer)
    
    return df_balance, df_item_attribute, df_emergency_buffer