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

    latest_str = latest.strftime("%y/%m/%d")
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

def _build_asset_tree_map(df_collection, df_asset_sub_type_attribute):
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

    jp_to_en = dict(zip(
        df_asset_sub_type_attribute["資産タイプとサブタイプ"],
        df_asset_sub_type_attribute["英語名"]
    ))

    df_tree["parents"] = df_tree["parents"].replace(jp_to_en)
    df_tree["labels"] = df_tree["labels"].replace(jp_to_en)

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

def _set_return(df_map, df, latest, one_year_ago):
    df_sub = df_map.copy()
    subtypes= df_map.index.tolist()

    for subtype in subtypes:
        mask = (df["資産サブタイプ"] == subtype)
        latest_return = df.loc[mask & (df["date"] == latest), "トータルリターン"].iloc[0]
        one_year_ago_return = df.loc[mask & (df["date"] == one_year_ago), "トータルリターン"].iloc[0]
        mean_asset = df[df["資産サブタイプ"] == subtype]["資産額"].mean()
        df_sub.loc[subtype, "リターン"] = (
            (latest_return - one_year_ago_return) / mean_asset
        )
        df_sub.loc[subtype, "資産額"] = mean_asset
    # ソーシャルレンディング
    #latest_return = df.loc[(df["資産サブタイプ"] == "預入金") & (df["date"] == latest), "トータルリターン"].iloc[0]
    #one_year_ago_return = df.loc[(df["資産サブタイプ"] == "預入金") & (df["date"] == one_year_ago), "トータルリターン"].iloc[0]
    #mean_asset = df[df["資産サブタイプ"] == "ソーシャルレンディング"]["資産額"].mean()
    #df_sub.loc["ソーシャルレンディング", "リターン"] = (
    #    (latest_return - one_year_ago_return) / mean_asset
    #)
    #df_sub.loc["預入金", "リターン"] = 0.0

    return df_sub

def _set_sharp_ratio(df_map, df, latest, one_year_ago):
    df_sub = df_map.copy()
    # 安全資産のシャープレシオはゼロ
    types = [
        "ポイント", "定期預金/仕組預金", "日本国債", "普通預金/MRF", "現金/電子マネー", "確定年金", "預入金"
    ]
    df_sub.loc[types, "シャープレシオ"] = 0.0

    # 市場価格のあるのは、標準シャープレシオを計算する
    types = ["確定拠出年金", "国内株式", "投資信託"]
    df.set_index("date", inplace=True)
    risk_free_rate = df_sub.loc["日本国債", "リターン"]
    for type in types:
        mask = (df["資産サブタイプ"] == type)
        # ボラティリティ計算
        df_tmp=pd.DataFrame()
        df_tmp["前日の現在価値"] = df[mask]["資産額"].shift(1)
        df_tmp["その日の積立額"] = df[mask]["取得価格"].diff()
        df_tmp["その日の現在価値"] = df[mask]["資産額"]
        df_tmp["その日のリターン"] = (df_tmp["その日の現在価値"] - df_tmp["前日の現在価値"] - df_tmp["その日の積立額"]) / df_tmp["前日の現在価値"]
        daily_volatility = df_tmp["その日のリターン"].dropna().std()
        annualized_volatility = daily_volatility * np.sqrt(250)
        # シャープレシオ計算
        df_sub.loc[type, "シャープレシオ"] = (
            (df_sub.loc[type, "リターン"] - risk_free_rate) / annualized_volatility
        )
        #print(annualized_volatility)
    # その他は応用シャープレシオ
    expected_volatility = 2 / 25 # 遅延リスク
    df_sub.loc["ソーシャルレンディング", "シャープレシオ"] = (
        (df_sub.loc["ソーシャルレンディング", "リターン"] - risk_free_rate) / expected_volatility
    )
    expected_volatility = 0.75
    df_sub.loc["セキュリティートークン", "シャープレシオ"] = (
        (df_sub.loc["セキュリティートークン", "リターン"] - risk_free_rate) / expected_volatility
    )
    expected_volatility = 0.01
    df_sub.loc["円建社債", "シャープレシオ"] = (
        (df_sub.loc["円建社債", "リターン"] - risk_free_rate) / expected_volatility
    )
    expected_volatility = 0.15
    df_sub.loc["外貨普通預金", "シャープレシオ"] = (
        (df_sub.loc["外貨普通預金", "リターン"] - risk_free_rate) / expected_volatility
    )
    df_sub.loc["暗号資産", "シャープレシオ"] = 0.0
   
    return df_sub

def _build_portfolio_efficiency_map(df_collection, df_asset_sub_type_attribute):
    # データフレーム作成
    df = df_collection.copy()
    df.drop(df[df["資産タイプ"] == "負債"].index, inplace=True)
    df_map = pd.DataFrame(index=df["資産サブタイプ"].unique(), columns=["リターン","シャープレシオ","資産額"])

    # 厳密に1年間にフィルタ
    latest = df["date"].max()
    one_year_ago = latest - pd.DateOffset(years=1)
    df = df[df["date"] >= one_year_ago]
    #print(latest, one_year_ago)

    df_map = _set_return(df_map, df, latest, one_year_ago)
    df_map = _set_sharp_ratio(df_map, df, latest, one_year_ago)

    jp_to_en = dict(zip(
        df_asset_sub_type_attribute["資産タイプとサブタイプ"],
        df_asset_sub_type_attribute["英語名"]
    ))

    # 名称変換
    df_map.index = df_map.index.map(jp_to_en)

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
    _graph_individual_setting(
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

def _build_liquidity_pyramid(df_collection, df_asset_sub_type_attribute):
    #データの生成
    latest = df_collection["date"].max()
    df = df_collection[df_collection["date"] == latest]
    df_ref = df_asset_sub_type_attribute.copy()

    tiers = [
        {'name': 'Tier 4: Long-Term / Illiquid Assets (Defined Contribution etc.)','color': '#5AB4EA',
        'value': df[df["資産サブタイプ"].isin(
            df_ref[df_ref["流動性"] == "非流動性資産"]["資産タイプとサブタイプ"].tolist()
        )]["資産額"].sum().astype(int) },

        {'name': 'Tier 3: Committed / Frictional Capital (Investment Trust etc.)',
        'value': df[df["資産サブタイプ"].isin(
            df_ref[df_ref["流動性"] == "市場性有価証券"]["資産タイプとサブタイプ"].tolist()
        )]["資産額"].sum().astype(int), 'color': '#377EB8'},
        
        {'name': 'Tier 2: Accessible Investment Buffer (Time Deposits etc.)',
        'value': df[df["資産サブタイプ"].isin(
            df_ref[df_ref["流動性"] == "市場確実性資産"]["資産タイプとサブタイプ"].tolist()
        )]["資産額"].sum().astype(int), 'color': '#1F4E79'},
        
        {'name': 'Tier 1: Immediate Defense Capital (Cash Reserves etc.)',
        'value': df[df["資産サブタイプ"].isin(
            df_ref[df_ref["流動性"] == "即時流動性資産"]["資産タイプとサブタイプ"].tolist()
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

def _build_liquidity_horizon(df_collection_latest, df_asset_attribute,df_asset_sub_type_attribute):
    # 資産名 - 資産サブタイプ - 資産額 - 償還日のデータセットを作る
    df_master = _get_liquidity_horizon_data(df_collection_latest, df_asset_attribute, df_asset_sub_type_attribute)
    
    # 償還日を月毎にする
    df_monthly = df_master.copy()
    df_monthly['償還日'] = pd.to_datetime(df_monthly['償還日']).dt.to_period('M').dt.to_timestamp('M')

    # 月別にする
    min_day = pd.to_datetime("today").normalize()
    all_months = pd.date_range(start=min_day, end=min_day + pd.DateOffset(months=12), freq="ME")
    # 資産サブタイプを英語にする
    #jp_to_en = dict(zip(
    #    df_asset_sub_type_attribute["資産タイプとサブタイプ"],
    #    df_asset_sub_type_attribute["英語名"]
    #))
    #df_monthly["資産サブタイプ"] = df_monthly["資産サブタイプ"].map(jp_to_en)
    
    # サブタイプごとにグラフを描く
    sub_types = df_monthly["資産サブタイプ"].unique().tolist()
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
    fig = _graph_individual_setting(
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

def build_dashboard_payload(include_graphs: bool = True, include_summary: bool = True) -> Dict[str, Any]:
    # DBから必要データを読み込みます
    df_collection, df_collection_latest, df_asset_sub_type_attribute, df_asset_attribute  = _read_table_from_db()

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = _build_summary(df_collection)
        
    if include_graphs:
        _make_graph_template()

        result["graphs"] = {
            "asset_tree_map": _build_asset_tree_map(df_collection,df_asset_sub_type_attribute),
            "target_deviation": _build_target_deviation(df_collection),
            "portfolio_efficiency_map": _build_portfolio_efficiency_map(df_collection,df_asset_sub_type_attribute),
            "liquidity_pyramid": _build_liquidity_pyramid(df_collection,df_asset_sub_type_attribute),
            "true_risk_exposure_flow": _build_true_risk_exposure_flow(df_collection),
            "liquidity_horizon": _build_liquidity_horizon(df_collection_latest, df_asset_attribute, df_asset_sub_type_attribute)
        }
    return result

def _get_liquidity_horizon_data(df_collection_latest, df_asset_attribute, df_asset_sub_type_attribute):
    # 資産名-資産サブタイプ-償還日-資産額のマスターデータフレーム作成
    df = df_asset_attribute.copy()
    mask = df["償還日"].notna()
    df_maturity_date = df[mask][["資産名","資産サブタイプ","償還日"]].reset_index(drop=True)
    
    df = df_collection_latest.copy()
    mask = df["資産名"].isin(df_maturity_date["資産名"].tolist())
    df_assets = df[mask][["資産名","資産額"]].reset_index(drop=True)
    
    df_master = pd.merge(df_maturity_date.set_index("資産名"), df_assets.set_index("資産名"), on="資産名", how="left")
    df_master.reset_index(inplace=True)
    min_day = pd.to_datetime("today").normalize()
    df_master = df_master[df_master["償還日"] <= min_day + pd.DateOffset(months=12)].reset_index(drop=True)
    # 資産サブタイプを英語にする
    jp_to_en = dict(zip(
        df_asset_sub_type_attribute["資産タイプとサブタイプ"],
        df_asset_sub_type_attribute["英語名"]
    ))
    df_master["資産サブタイプ"] = df_master["資産サブタイプ"].map(jp_to_en)

    return df_master

def get_graph_details(graph_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    # 再利用性を考慮して、graph_id で分岐
    if graph_id == "liquidity_horizon":
        # 必要なデータをDBから取得 (ここでは簡易的にすべて読み込むが、最適化余地あり)
        df_collection, df_collection_latest, df_asset_sub_type_attribute, df_asset_attribute  = _read_table_from_db()
        df_master = _get_liquidity_horizon_data(df_collection_latest, df_asset_attribute, df_asset_sub_type_attribute)     
        
        # フィルタリング
        sub_type = params.get("sub_type")

        if sub_type:
            # フィルタ
            df_filtered = df_master[df_master["資産サブタイプ"] == sub_type].reset_index(drop=True)
            # 型
            df_filtered[["資産名", "資産サブタイプ", "償還日"]] = df_filtered[["資産名", "資産サブタイプ", "償還日"]].astype(str)
            df_filtered["資産額"] = df_filtered["資産額"].map(lambda x: f"¥{int(x):,}")
            
            #print(df_filtered.dtypes)

            fig = go.Figure()
            fig.add_trace(go.Table(
                header=dict(values=list(df_filtered.columns.tolist())),
                cells=dict(values=[df_filtered[col] for col in df_filtered.columns])
            ))
            fig.update_layout(
                meta={"id": "liquidity_horizon"},
            )
            #fig.show()
            fig_dict = fig.to_dict()
            json_str = json.dumps(fig_dict, default=str)
            return json_str

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
    df_collection, df_collection_latest, df_asset_sub_type_attribute, df_asset_attribute = _read_table_from_db()
    #print(_build_summary(df_collection))
    #_build_asset_tree_map(df_collection,df_asset_sub_type_attribute)
    #_build_target_deviation(df_collection)
    #_build_portfolio_efficiency_map(df_collection,df_asset_sub_type_attribute)
    #_build_liquidity_pyramid(df_collection,df_asset_sub_type_attribute)
    #_build_true_risk_exposure_flow(df_collection)
    #_build_liquidity_horizon(df_collection_latest, df_asset_attribute,df_asset_sub_type_attribute)
    print(get_graph_details("liquidity_horizon", {"sub_type": "Time Deposits"}))
    #print(df)