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

def _build_summary(df_collection) -> Dict[str, float]:
    latest = get_latest_date()    
    latest = latest.strftime("%Y/%m/%d")
    df = df_collection.copy()
    total_asset = df[df["資産タイプ"].isin(["リスク資産", "安全資産"])].groupby("date")["資産額"].sum().loc[latest]
    active_growth_capital = (
        df[df["資産タイプ"] == "リスク資産"].groupby("date")["資産額"].sum().loc[latest]/
        total_asset
    )
    aggressive_return_exposure = (
        df[df["資産サブタイプ"].isin(
            ["国内株式", "投資信託", "ソーシャルレンディング", "セキュリティートークン", "暗号資産"]
        )].groupby("date")["資産額"].sum().loc[latest]/
        total_asset
    )
    emergency_buffer = (
        df[df["資産サブタイプ"].isin(["現金", "普通預金/MRF"])].groupby("date")["資産額"].sum().loc[latest]
    )
    debt_exposure_ratio = (
        df[df["資産タイプ"] == "負債"].groupby("date")["資産額"].sum().loc[latest]/
        total_asset*-1
    )
    
    return {
        "latest_date": latest,
        "active_growth_capital": round(active_growth_capital*100,1),
        "aggressive_return_exposure": round(aggressive_return_exposure*100,1),
        "emergency_buffer": round(emergency_buffer),
        "debt_exposure_ratio": round(debt_exposure_ratio*100,1),
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
    # データフレーム
    df = pd.DataFrame(columns=["生値", "スムージング"])
    df["生値"] = df_collection["実績_資産額"] / df_collection["目標_資産額"]
    df["スムージング"] = df["生値"].rolling(window=30).mean()
    df.fillna(1, inplace=True)

    # PXでグラフ生成
    x_values = df.index.strftime("%Y-%m-%d").tolist()
    y1_values = df["生値"].astype(float).tolist()
    y2_values = df["スムージング"].astype(float).tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values, y=y1_values, mode="lines", name="Actual",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: %{y:.1%}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y2_values, mode="lines", name="Smoothing",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: %{y:.1%}<extra></extra>'
    ))
    fig = _graph_individual_setting(fig, "date", "%Y-%m-%d", "Progress Rate", "", ".0%")
    # metaでID付与
    fig.update_layout(meta={"id": "progress_rate"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def _build_saving_rate(df_collection):
    # データフレーム作成
    df_collection_prev = df_collection.loc[: df_collection.index.max() - pd.offsets.MonthEnd(1)]
    df = pd.DataFrame(columns=["実績_貯蓄率", "目標_貯蓄率"])
    df["実績_貯蓄率"] = (
        (
            df_collection_prev.resample("ME")["金額"].sum() +
            df_collection_prev.resample("ME")["実績_トータルリターン"].last().diff()
        )/
        df_collection_prev[df_collection_prev["収支カテゴリー"] == "収入"].resample("ME")["金額"].sum()
    )
    df["目標_貯蓄率"] = (
        (
            df_collection_prev.resample("ME")["目標"].sum() +
            df_collection_prev.resample("ME")["目標_トータルリターン"].last().diff()
        )/
        df_collection_prev[df_collection_prev["収支カテゴリー"] == "収入"].resample("ME")["目標"].sum()
    )
    df.dropna(inplace=True)
    #print(df)
    # PXでグラフ生成
    x_values = df.index.strftime("%Y-%m").tolist()
    y1_values = df["実績_貯蓄率"].astype(float).tolist()
    y2_values = df["目標_貯蓄率"].astype(float).tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_values, y=y1_values, name="Actual",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: %{y:.1%}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y2_values, mode="lines+markers", name="Target",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: %{y:.1%}<extra></extra>'
    ))
    fig = _graph_individual_setting(fig, "date", "%Y-%m", "Saving Rate", "", ".0%")
    # metaでID付与
    fig.update_layout(meta={"id": "saving_rate"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def _build_total_assets(df_collection):
    # データフレーム生成
    df = df_collection[["実績_資産額", "目標_資産額"]]
    #print(df)
    # PXでグラフ生成
    x_values = df.index.strftime("%Y-%m-%d").tolist()
    y1_values = df["実績_資産額"].astype(int).tolist()
    y2_values = df["目標_資産額"].astype(int).tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values, y=y1_values, mode="lines", name="Actual",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}+<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y2_values, mode="lines", name="Target",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}+<extra></extra>'
    ))
    fig = _graph_individual_setting(fig, "date", "%Y-%m-%d", "Net Assets", "¥", "")
    # metaでID付与
    fig.update_layout(meta={"id": "total_assets"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def _build_total_returns(df_collection):
    # データフレーム生成
    df = df_collection[["実績_トータルリターン", "目標_トータルリターン"]]
    #print(df)
    # PXでグラフ生成
    x_values = df.index.strftime("%Y-%m-%d").tolist()
    y1_values = df["実績_トータルリターン"].astype(int).tolist()
    y2_values = df["目標_トータルリターン"].astype(int).tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values, y=y1_values, mode="lines", name="Actual",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y2_values, mode="lines", name="Target",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig = _graph_individual_setting(fig,"date", "%Y-%m-%d", "Total Returns", "¥", "")

    # metaでID付与
    fig.update_layout(meta={"id": "total_returns"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    #print(json_str)
    return json_str

def _build_general_balance(df_collection):
    df = pd.DataFrame(columns=["実績_一般収支", "目標_一般収支"])
    df["実績_一般収支"] = (
        df_collection[df_collection["収支タイプ"] == "一般収支"].resample("ME")["金額"].sum()
    )
    df["目標_一般収支"] = (
        df_collection[df_collection["収支タイプ"] == "一般収支"].resample("ME")["目標"].sum()
    )

    x_values = df.index.strftime("%Y-%m").tolist()
    y1_values = df["実績_一般収支"].astype(int).tolist()
    y2_values = df["目標_一般収支"].astype(int).tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_values, y=y1_values, name="Actual",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y2_values, mode="lines+markers", name="Target",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))

    fig = _graph_individual_setting(fig, "date", "%Y-%m", "Net Balance", "¥", "")
    # metaでID付与
    fig.update_layout(meta={"id": "general_balance"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def _build_special_balance(df_collection):
    df = pd.DataFrame(columns=["実績_特別収支", "目標_特別収支"])
    df["実績_特別収支"] = (
        df_collection [df_collection["収支タイプ"] == "特別収支"].resample("ME")["金額"].sum().cumsum()
    )
    df["目標_特別収支"] = (
        df_collection [df_collection["収支タイプ"] == "特別収支"].resample("ME")["目標"].sum().cumsum()
    )
    
    x_values = df.index.strftime("%Y-%m").tolist()
    y1_values = df["実績_特別収支"].astype(int).tolist()
    y2_values = df["目標_特別収支"].astype(int).tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values, y=y1_values, mode="lines+markers", fill="tozeroy", name="Actual",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y2_values, mode="lines+markers", name="Target",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))

    fig = _graph_individual_setting(fig, "date", "%Y-%m", "Net Cash - Cumulative", "¥", "")
    # metaでID付与
    fig.update_layout(meta={"id": "special_balance"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def build_dashboard_payload(include_graphs: bool = True, include_summary: bool = True) -> Dict[str, Any]:
    # DBから必要データを読み込みます
    df_collection = _read_table_from_db()

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = _build_summary(df_collection)
        
    if include_graphs:
        _make_graph_template()

        #result["graphs"] = {
            #"asset_tree_map": _build_asset_tree_map(df_collection),
            #"saving_rate": _build_saving_rate(df_collection),
            #"assets": _build_total_assets(df_collection),
            #"returns": _build_total_returns(df_collection),
            #"general_balance": _build_general_balance(df_collection),
            #"special_balance": _build_special_balance(df_collection)
        #}
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
    print(_build_summary(df))
    #_build_progress_rate(df)
    #_build_saving_rate(df)
    #_build_total_assets(df)
    #_build_total_returns(df)
    #_build_general_balance(df)
    #_build_special_balance(df)



