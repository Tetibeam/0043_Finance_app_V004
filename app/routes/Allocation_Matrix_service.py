from app.utils.data_loader import (
    get_latest_date,
    query_table_aggregated,
)
from typing import Dict, Any
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json

def _read_table_from_db():
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
            "資産カテゴリー": "MAX",
            "資産額": "SUM",
            "トータルリターン": "SUM",
            "取得価格": "SUM"
        },
        group_by=["date","資産サブタイプ"],
        start_date=start_date,
        end_date=latest_date,
        filters=None,
        order_by=["date"]
    )
    #print(df_asset_profit)
    return df_asset_profit

def _make_vector(current, previous):
    if previous == 0:
        return 0
    rate = current / previous
    if rate > 1.005:
        return 1
    elif rate < 0.995:
        return -1
    else:
        return 0

def _build_summary(df_collection) -> Dict[str, float]:
    latest = get_latest_date()
    one_month_ago = latest - pd.DateOffset(months=1)
    df = df_collection.copy()
    
    total_asset = df[df["資産タイプ"].isin(["リスク資産", "安全資産"])].groupby("date")["資産額"].sum().loc[latest]
    total_asset_one_month_ago = df[df["資産タイプ"].isin(["リスク資産", "安全資産"])].groupby("date")["資産額"].sum().loc[one_month_ago]
    
    active_growth_capital = (
        df[df["資産タイプ"] == "リスク資産"].groupby("date")["資産額"].sum().loc[latest]/
        total_asset
    )
    active_growth_capital_one_month_ago = (
        df[df["資産タイプ"] == "リスク資産"].groupby("date")["資産額"].sum().loc[one_month_ago]/
        total_asset_one_month_ago
    )

    aggressive_return_exposure = (
        df[df["資産サブタイプ"].isin(
            ["国内株式", "投資信託", "ソーシャルレンディング", "セキュリティートークン", "暗号資産"]
        )].groupby("date")["資産額"].sum().loc[latest]/
        total_asset
    )
    aggressive_return_exposure_one_month_ago = (
        df[df["資産サブタイプ"].isin(
            ["国内株式", "投資信託", "ソーシャルレンディング", "セキュリティートークン", "暗号資産"]
        )].groupby("date")["資産額"].sum().loc[one_month_ago]/
        total_asset_one_month_ago
    )
    
    emergency_buffer = (
        df[df["資産サブタイプ"].isin(["現金", "普通預金/MRF"])].groupby("date")["資産額"].sum().loc[latest]
    )
    emergency_buffer_one_month_ago = (
        df[df["資産サブタイプ"].isin(["現金", "普通預金/MRF"])].groupby("date")["資産額"].sum().loc[one_month_ago]
    )
    debt_exposure_ratio = (
        df[df["資産タイプ"] == "負債"].groupby("date")["資産額"].sum().loc[latest]/
        total_asset*-1
    )
    debt_exposure_ratio_one_month_ago = (
        df[df["資産タイプ"] == "負債"].groupby("date")["資産額"].sum().loc[one_month_ago]/
        total_asset_one_month_ago*-1
    )

    latest_str = latest.strftime("%Y/%m/%d")
    return {
        "latest_date": latest_str,
        "active_growth_capital": round(active_growth_capital*100,1),
        "active_growth_capital_vector": _make_vector(active_growth_capital, active_growth_capital_one_month_ago),
        "aggressive_return_exposure": round(aggressive_return_exposure*100,1),
        "aggressive_return_exposure_vector": _make_vector(aggressive_return_exposure, aggressive_return_exposure_one_month_ago),
        "emergency_buffer": round(emergency_buffer),
        "emergency_buffer_vector": _make_vector(emergency_buffer, emergency_buffer_one_month_ago),
        "debt_exposure_ratio": round(debt_exposure_ratio*100,1),
        "debt_exposure_ratio_vector": _make_vector(debt_exposure_ratio, debt_exposure_ratio_one_month_ago),
    }

def _make_graph_template():
    theme = go.layout.Template(
        layout=go.Layout(
            autosize=True, margin=dict(l=50,r=30,t=10,b=40),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
            font=dict(family="Inter, Roboto", size=14, color="#DDDDDD"),

            xaxis=dict(
                title=dict(font_size=12),
                title_standoff=16,
                tickfont=dict(size=10),
                showgrid=True,
                gridcolor="#444444",
                zeroline=False,
                color="#cccccc"
            ),
            
            yaxis=dict(
                title=dict(font_size=12),
                title_standoff=16,
                separatethousands=False,
                tickfont=dict(size=10),
                showgrid=True,
                gridcolor="#444444",
                zeroline=False,
                color="#cccccc"
            ),
            
            legend=dict(
                visible=True,
                orientation="h",
                yanchor="top",
                y=1.2,
                xanchor="right",
                x=1,
            ),
            colorway=["#4E79A7", "#F28E2B"],
            
        )
    )
    pio.templates["dark_dashboard"] = theme
    pio.templates.default = "plotly_dark+dark_dashboard"

def _graph_individual_setting(fig, x_title, x_tickformat, y_title, y_tickprefix, y_tickformat):
    fig.update_xaxes(
        title = dict(text = x_title),
        tickformat=x_tickformat
    )
    fig.update_yaxes(
        title = dict(text = y_title),
        tickprefix=y_tickprefix,
        tickformat=y_tickformat,
    )
    return fig

def _build_asset_tree_map(df_collection):
    #データフレーム作成
    latest = df_collection["date"].max()
    df = df_collection[df_collection["date"] == latest][["資産サブタイプ","資産タイプ","資産額"]]
    df.drop(df[df["資産タイプ"] == "負債"].index, inplace=True)
    df_tree = df.rename(columns={"資産サブタイプ":"labels", "資産タイプ":"parents", "資産額":"values"})

    list = []
    for label in ["安全資産","リスク資産"]:
        list.append({
            "labels":label,
            "parents":"総資産",
            "values":df_tree[df_tree["parents"] == label]["values"].sum()
        })
    list.append({
        "labels":"総資産",
        "parents":"",
        "values":df_tree["values"].sum()
    })
    df_tree = pd.concat([df_tree, pd.DataFrame(list)], ignore_index=True)

    df_tree["parents"] = df_tree["parents"].replace({
        "安全資産":"Defensive Assets",
        "リスク資産":"Aggressive Growth Assets",
        "総資産":"Gross Assets",
    })

    df_tree["labels"] = df_tree["labels"].replace({
        "総資産":"Gross Assets",
        "安全資産":"Defensive Assets",
        "リスク資産":"Aggressive Growth Assets",
        "現金/電子マネー":"Cash",
        "普通預金/MRF":"Cash Reserves",
        "定期預金/仕組預金":"Time Deposits",
        "確定年金":"Real Estate",
        "日本国債":"Securities",
        "預入金":"Cash Deposits",
        "ポイント":"Loyalty Rewards",
        "投資信託":"Investment Trust",
        "ソーシャルレンディング":"P2P Lending",
        "セキュリティートークン":"Tokenized Real Estate",
        "確定拠出年金":"Defined Contribution Plan",
        "暗号資産":"Digital Assets",
        "円建社債":"Fixed Income",
        "国内株式":"Domestic Equity",
    })

    #データフレーム作成
    labels = df_tree["labels"].tolist()
    parents = df_tree["parents"].tolist()
    values = df_tree["values"].astype(int).tolist()

    fig = go.Figure(
        go.Treemap(
            labels=labels, parents=parents, values=values,
            visible=True, branchvalues ="total", marker_colorscale = 'Blues',
            textinfo = "label+percent parent+percent entry",
            textfont_size= 14,hoverlabel_font_size = 14,
            hovertemplate =
                '<br><i>Name</i>: %{label}'+
                '<br><i>Amount</i>: ¥%{value}<extra></extra>'
        )
    )
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
    )
    
    fig.update_layout(meta={"id": "asset_tree_map"})

    #fig.show()

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    return json_str

def _build_target_deviation(df_collection):
    pass
def _build_portfolio_efficiency_map(df_collection):
    pass
def _build_liquidity_pyramid(df_collection):
    pass
def _build_true_risk_exposure_flow(df_collection):
    pass
def _build_rebalancing_workbench(df_collection):
    pass
def build_dashboard_payload(include_graphs: bool = True, include_summary: bool = True) -> Dict[str, Any]:
    # DBから必要データを読み込みます
    df_collection = _read_table_from_db()

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = _build_summary(df_collection)
        
    if include_graphs:
        _make_graph_template()

        result["graphs"] = {
            "asset_tree_map": _build_asset_tree_map(df_collection),
            "target_deviation": _build_target_deviation(df_collection),
            "portfolio_efficiency_map": _build_portfolio_efficiency_map(df_collection),
            "liquidity_pyramid": _build_liquidity_pyramid(df_collection),
            "true_risk_exposure_flow": _build_true_risk_exposure_flow(df_collection),
            "rebalancing_workbench": _build_rebalancing_workbench(df_collection)
        }
    return result

if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
    # DBマネージャーの初期化
    from app.utils.db_manager import init_db
    init_db(base_dir)
    df = _read_table_from_db()
    #print(df)
    #print(_build_summary(df))
    _build_asset_tree_map(df)
    _build_target_deviation(df)
    _build_portfolio_efficiency_map(df)
    _build_liquidity_pyramid(df)
    _build_true_risk_exposure_flow(df)
    _build_rebalancing_workbench(df)



