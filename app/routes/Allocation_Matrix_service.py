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
from .Alloction_Matrix_service_detail import (
    liquidity_horizon_detail,
    read_table_from_db,
    get_liquidity_horizon_master_data
)
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

    latest_str = latest.strftime("%y/%m/%d")
    return {
        "latest_date": latest_str,
        "active_growth_capital": round(active_growth_capital*100,1),
        "active_growth_capital_vector": make_vector(active_growth_capital, active_growth_capital_one_month_ago),
        "aggressive_return_exposure": round(aggressive_return_exposure*100,1),
        "aggressive_return_exposure_vector": make_vector(aggressive_return_exposure, aggressive_return_exposure_one_month_ago),
        "emergency_buffer": round(emergency_buffer),
        "emergency_buffer_vector": make_vector(emergency_buffer, emergency_buffer_one_month_ago),
        "debt_exposure_ratio": round(debt_exposure_ratio*100,1),
        "debt_exposure_ratio_vector": make_vector(debt_exposure_ratio, debt_exposure_ratio_one_month_ago),
    }

def _build_asset_tree_map(df_collection, df_item_attribute):
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


    df_tree["parents"] = df_tree["parents"].replace(get_map_jp_to_en_sub_type(df_item_attribute))
    df_tree["labels"] = df_tree["labels"].replace(get_map_jp_to_en_sub_type(df_item_attribute))

    # グラフ生成
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
                '<br><b>Name</b>: %{label}'+
                '<br><b>Amount</b>: ¥%{value}<extra></extra>'
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

def _build_portfolio_efficiency_map(df_collection, df_item_attribute):
    # データフレーム作成
    df = df_collection.copy()
    df.drop(df[df["資産タイプ"] == "負債"].index, inplace=True)
    df_map = pd.DataFrame(index=df["資産サブタイプ"].unique(), columns=["リターン","シャープレシオ","資産額"])

    # 1年間
    latest = df["date"].max()
    one_year_ago = latest - pd.DateOffset(years=1)
    
    # トータルリターン
    for subtype in df_map.index:
        mask = (df["資産サブタイプ"] == subtype)
        df_map.loc[subtype, "リターン"], df_map.loc[subtype, "資産額"] = cal_total_return(df[mask], subtype, one_year_ago, latest)
    # シャープレシオ
    for subtype in df_map.index:
        mask = (df["資産サブタイプ"] == subtype)
        df_map.loc[subtype, "シャープレシオ"] = cal_sharpe_ratio(
            df[mask], subtype, one_year_ago, latest, df_item_attribute,
            df_map.loc[subtype, "リターン"], df_map.loc["日本国債", "リターン"])
    #print(df_map)
    
    # 名称変換
    df_map.index = df_map.index.map(get_map_jp_to_en_sub_type(df_item_attribute))
    
    #print(df_map)
    # グラフ生成
    df_map.reset_index(names=["資産サブタイプ"], inplace=True)
    x_values = df_map["リターン"].astype(float).tolist()
    y_values = df_map["シャープレシオ"].astype(float).tolist()
    labels = df_map["資産サブタイプ"].tolist()
    # ---- バブルサイズ正規化（推奨）----
    size_values = df_map["資産額"].abs().astype(int)
    size_scaled = np.sqrt(size_values)  # √でボラを抑える
    size_scaled = size_scaled * (80 / size_scaled.max())  # maxが80pxになるよう調整

    fig = go.Figure(
        data=go.Scatter(
            x=x_values,
            y=y_values,
            mode="markers",
            marker=dict(
                size=size_scaled,
                color=size_scaled,
                colorscale="Blues",
                colorbar=dict(tickprefix="¥",ticksuffix="M",tickformat=",.0f"),
                showscale=True,
                opacity=0.7,
                sizemode="diameter"
            ),
            text=labels,
            customdata=size_values,
            hovertemplate =
                '<br><b>Name</b>: %{text}'+
                '<br><b>Return</b>: %{x:.1%}'+
                '<br><b>Sharpe Ratio</b>: %{y:.1f}'+
                '<br><b>Asset Size</b>: ¥%{customdata:,}<extra></extra>'
        )
    )
    fig = graph_individual_setting(
        fig,
        x_title="Return",
        y_title="Sharpe Ratio",
        x_tickformat=".1%",
        y_tickformat=".1f",
        y_tickprefix=""
    )
    fig.update_layout(
        meta={"id": "portfolio_efficiency_map"}
    )

    #fig.show()

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    return json_str

def _build_liquidity_pyramid(df_collection, df_item_attribute):
    #データの生成
    latest = df_collection["date"].max()
    df = df_collection[df_collection["date"] == latest]
    df_ref = df_item_attribute.copy()

    tiers = [
        {'name': 'Tier 4: Long-Term / Illiquid Assets (Defined Contribution etc.)','color': '#5AB4EA',
        'value': df[df["資産サブタイプ"].isin(
            df_ref[df_ref["流動性"] == "非流動性資産"]["項目"].tolist()
        )]["資産額"].sum().astype(int) },

        {'name': 'Tier 3: Committed / Frictional Capital (Investment Trust etc.)',
        'value': df[df["資産サブタイプ"].isin(
            df_ref[df_ref["流動性"] == "市場性有価証券"]["項目"].tolist()
        )]["資産額"].sum().astype(int), 'color': '#377EB8'},
        
        {'name': 'Tier 2: Accessible Investment Buffer (Time Deposits etc.)',
        'value': df[df["資産サブタイプ"].isin(
            df_ref[df_ref["流動性"] == "市場確実性資産"]["項目"].tolist()
        )]["資産額"].sum().astype(int), 'color': '#1F4E79'},
        
        {'name': 'Tier 1: Immediate Defense Capital (Cash Reserves etc.)',
        'value': df[df["資産サブタイプ"].isin(
            df_ref[df_ref["流動性"] == "即時流動性資産"]["項目"].tolist()
        )]["資産額"].sum().astype(int), 'color': '#002D62'}
    ]
    total_assets = sum(t['value'] for t in tiers)

    fig = go.Figure()

    for i, tier in enumerate(tiers):
        # 棒の幅（資産額）
        bar_width = tier['value']
        
        # 棒の左側のブランク（幅の計算）
        # 全体幅 - 棒の幅 を 2で割ることで、左右の余白を等しくする
        blank_width = (total_assets - bar_width) *0.5
        
        # ティアの高さ（Y軸のカテゴリ）
        tier_category = tier['name'].split(':')[0] # Tier 1, Tier 2...

        # 1. 左側のブランク（透明な棒）
        fig.add_trace(go.Bar(
            y=[tier_category],
            x=[blank_width],
            orientation='h',
            marker=dict(color='rgba(0,0,0,0)'), # 透明に設定
            showlegend=False,
            hoverinfo='skip'
        ))

        # 2. 資産額を表すバー
        fig.add_trace(go.Bar(
            y=[tier_category],
            x=[bar_width],
            orientation='h',
            name=tier['name'],
            text=f'¥{tier["value"]:,}<br>{tier["value"] / total_assets:.1%}', # バー上に金額を表示
            textposition='inside',
            insidetextanchor='middle',
            marker=dict(color=tier['color']),
            customdata=[[tier['name'], tier['value'] / total_assets]],
            hovertemplate = 
                '<b>%{customdata[0]}</b>'+
                '<br>Assets: ¥%{x:,}'+
                '<br>Ratio: %{customdata[1]:.1f}%<extra></extra>',
            
        ))

    # 積み上げ棒グラフとして結合
    fig.update_layout(barmode='stack')
    fig.update_traces(
        textposition='auto',
        textfont=dict(
            family="Arial, sans-serif", # 任意のフォントファミリーを指定
            size=14,                     # 任意のサイズを指定
            color="white"                # テキストの色を指定（背景色に応じて）
        ),
    )

    fig.update_layout(
        xaxis=dict(
            range=[total_assets*0.2, total_assets*0.8], # 最大値の115%までX軸の範囲を広げる
            showgrid=False,
            zeroline=False,
            showticklabels=False,  # X軸ラベルを非表示
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            autorange="reversed", # Tier 4を上にするため反転
        ),
        legend=dict(
            x=0.02, 
            y=0.98,   
            xanchor='left',
            yanchor='top',
            xref="container",yref="container",
        ),
        
        margin=dict(r=0, l=60, t=90, b=10), 
    )

    #fig.show()
    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    return json_str

def _build_true_risk_exposure_flow(df_collection):
    pass

def _build_liquidity_horizon(df_collection_latest, df_asset_attribute, df_item_attribute):
    df_master = get_liquidity_horizon_master_data(df_collection_latest, df_asset_attribute, df_item_attribute)
    min_day = pd.to_datetime("today").normalize()

    # 月別のまとめてグラフ化
    df_monthly = df_master.copy()
    df_monthly = df_monthly[
        (df_monthly["償還日"] >= min_day) & (df_monthly["償還日"] <= min_day + pd.DateOffset(months=12))
    ].reset_index(drop=True)
    df_monthly['償還日'] = pd.to_datetime(df_monthly['償還日']).dt.to_period('M').dt.to_timestamp('M')
    all_months = pd.date_range(start=min_day, end=min_day + pd.DateOffset(months=12), freq="ME")
    #print(df_monthly)

    # サブタイプごとにグラフを描く
    sub_types = df_monthly["資産サブタイプ"].unique().tolist()
    #print(sub_types)
    fig = go.Figure()
    for sub_type in sub_types:
        df_sub = df_monthly[df_monthly["資産サブタイプ"] == sub_type].copy()
        df_sub = df_sub.groupby('償還日')[['資産額']].sum()
        df_sub = df_sub.reindex(all_months, fill_value=0)
        #print(df_sub)
        x_values = df_sub.index.tolist()
        y_values = df_sub['資産額'].tolist()
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            name=sub_type,
            customdata=[sub_type]*len(x_values),
            hovertemplate = 
                '<b>%{customdata}</b>'+
                '<br>Assets: ¥%{y:,}'+
                '<extra></extra>',
        ))
    fig = graph_individual_setting(
        fig, x_title="償還日",x_tickformat="%y-%m",y_title="償還額", y_tickprefix="¥",y_tickformat=""
    )
    fig.update_layout(
        meta={"id": "liquidity_horizon"},
        barmode="stack",
        colorway=px.colors.sequential.Blues[3:],
        xaxis=dict(
            range=[min_day-pd.DateOffset(months=1), min_day + pd.DateOffset(months=12)],
        ),
    )
    #fig.show()   
    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict, default=str)
    return json_str

#@cache.cached(timeout=300)  # 300秒間（5分間）キャッシュを保持する
def build_Allocation_Matrix_payload(include_graphs: bool = True, include_summary: bool = True) -> Dict[str, Any]:

    print("--- [CACHE MISS] Running heavy calculation for build_Allocation_Matrix_payload ---")
    
    # DBから必要データを読み込みます
    df_collection, df_collection_latest, df_item_attribute, df_asset_attribute  = read_table_from_db()

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = _build_summary(df_collection)
        
    if include_graphs:
        result["graphs"] = {
            "asset_tree_map": _build_asset_tree_map(df_collection,df_item_attribute),
            "target_deviation": _build_target_deviation(df_collection),
            "portfolio_efficiency_map": _build_portfolio_efficiency_map(df_collection,df_item_attribute),
            "liquidity_pyramid": _build_liquidity_pyramid(df_collection,df_item_attribute),
            "true_risk_exposure_flow": _build_true_risk_exposure_flow(df_collection),
            "liquidity_horizon": _build_liquidity_horizon(df_collection_latest, df_asset_attribute, df_item_attribute)
        }
    return result

def get_Allocation_Matrix_details(graph_id: str, params: Dict[str, Any]) -> Dict[str, Any]:

    # 再利用性を考慮して、graph_id で分岐
    if graph_id == "liquidity_horizon":
        return liquidity_horizon_detail(graph_id, params)

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
    df_collection, df_collection_latest, df_item_attribute, df_asset_attribute = read_table_from_db()
    #print(build_Allocation_Matrix_payload(include_graphs=False, include_summary=True))
    
    #print(_build_summary(df_collection))
    #_build_asset_tree_map(df_collection,df_item_attribute)
    #_build_target_deviation(df_collection)
    #_build_portfolio_efficiency_map(df_collection,df_item_attribute)
    #_build_liquidity_pyramid(df_collection,df_item_attribute)
    #_build_true_risk_exposure_flow(df_collection)
    #_build_liquidity_horizon(df_collection_latest, df_asset_attribute,df_item_attribute)
    #get_graph_details("liquidity_horizon", {"sub_type": "Time Deposits"})
    #print(df)