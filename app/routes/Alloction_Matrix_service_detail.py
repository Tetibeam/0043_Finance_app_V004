from app.utils.data_loader import (
    get_latest_date,
    query_table_aggregated,
    get_raw_table
)
from typing import Dict, Any
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json

from app.utils.dashboard_utility import make_vector, graph_individual_setting
from app import cache
from app.utils.calculation import cal_total_return, cal_sharpe_ratio
from app.utils.dashboard_utility import get_map_jp_to_en_sub_type
from app.routes.routes_helper import key_generator_with_params

def read_table_from_db():
    # 12か月前の月初を計算
    latest_date = get_latest_date()
    start_date = max(
        (latest_date - pd.DateOffset(months=12)).replace(day=1),
        pd.to_datetime("2024-10-01")
    )
    df_asset_profit = query_table_aggregated(
        table_name="asset_profit_detail",
        aggregates={
            "資産タイプ": "MAX",
            "資産額": "SUM",
            "トータルリターン": "SUM",
            "取得価格": "SUM",
        },
        group_by=["date","資産サブタイプ"],
        start_date=start_date,
        end_date=latest_date,
        filters=None,
        order_by=["date"]
    )

    df_asset_profit_latest = query_table_aggregated(
        table_name="asset_profit_detail",
        aggregates={
            "date": "MAX",
            "資産サブタイプ": "MAX",
            "資産額": "MAX",
        },
        group_by=["資産名"],
        start_date=latest_date,
        end_date=latest_date,
        filters=None,
        order_by=["資産名"]
    )
    #print(df_asset_profit_latest)

    df_asset_sub_type_attribute = get_raw_table("asset_sub_type_attribute")

    df_asset_attribute = get_raw_table("asset_attribute")

    return df_asset_profit, df_asset_profit_latest, df_asset_sub_type_attribute, df_asset_attribute

def get_liquidity_horizon_master_data(df_collection_latest, df_asset_attribute, df_asset_sub_type_attribute):
    # 資産名-資産サブタイプ-償還日-資産額のマスターデータフレーム作成
    df = df_asset_attribute.copy()
    mask = df["償還日"].notna()
    df_maturity_date = df[mask][["資産名","資産サブタイプ","償還日"]].reset_index(drop=True)
    
    df = df_collection_latest.copy()
    mask = df["資産名"].isin(df_maturity_date["資産名"].tolist())
    df_assets = df[mask][["資産名","資産額"]].reset_index(drop=True)
    
    df_master = pd.merge(df_maturity_date.set_index("資産名"), df_assets.set_index("資産名"), on="資産名", how="left")
    df_master.reset_index(inplace=True)

    #min_day = pd.to_datetime("today").normalize()
    #df_master = df_master[df_master["償還日"] <= min_day + pd.DateOffset(months=12)].reset_index(drop=True)
    
    # 資産サブタイプを英語にする
    df_master["資産サブタイプ"] = df_master["資産サブタイプ"].map(
       dict(zip(
        df_asset_sub_type_attribute["項目"],
        df_asset_sub_type_attribute["英語名"]
        ))
    )
    
    return df_master

@cache.cached(timeout=300, make_cache_key=key_generator_with_params)  # 300秒間（5分間）キャッシュを保持する
def liquidity_horizon_detail(graph_id: str, params: Dict[str, Any]):

    print("--- [CACHE MISS] Running heavy calculation for build_dashboard_payload ---")

    # 必要なデータをDBから取得 (ここでは簡易的にすべて読み込むが、最適化余地あり)
    df_collection, df_collection_latest, df_asset_sub_type_attribute, df_asset_attribute  = read_table_from_db()
    df_master = get_liquidity_horizon_master_data(df_collection_latest, df_asset_attribute, df_asset_sub_type_attribute)     
        
    # フィルタリング
    sub_type = params.get("sub_type")

    if sub_type:
        # フィルタ
        df_filtered = df_master[df_master["資産サブタイプ"] == sub_type][["資産名","償還日","資産額"]].reset_index(drop=True)
        df_filtered = df_filtered.sort_values(by="償還日", ascending=True).reset_index(drop=True)
        # 型
        df_filtered[["資産名", "償還日"]] = df_filtered[["資産名", "償還日"]].astype(str)
        df_filtered["資産額"] = df_filtered["資産額"].map(lambda x: f"¥{int(x):,}")
        # 名前
        df_filtered.rename(columns={"資産名": "Asset Name", "償還日": "Maturity Date", "資産額": "Redemption Amount"}, inplace=True)
            
        #print(df_filtered.dtypes)

        fig = go.Figure()
        fig.add_trace(go.Table(
            columnwidth=[4, 1, 1.5],

            header=dict(
                values=list(df_filtered.columns.tolist()),
                align="center",
                line_width=5,
                font=dict(size=22, family='Roboto, sans-serif'),
                height=32,
            ),
            cells=dict(
                values=[df_filtered[col] for col in df_filtered.columns],
                align=["left","right","right"],
                line_width=3,
                font=dict(size=18, family='Roboto, sans-serif'),
                height=30,
            ),
        ))
        fig.update_layout(
            meta={"id": "liquidity_horizon"},
            )

        #fig.show()
        fig_dict = fig.to_dict()
        json_str = json.dumps(fig_dict, default=str)
        return json_str
