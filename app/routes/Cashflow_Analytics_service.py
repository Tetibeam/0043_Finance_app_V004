from .Cashflow_Analytics_service_detail import read_table_from_db
from app.utils.data_loader import get_latest_date
from app.utils.dashboard_utility import (
    make_vector, graph_individual_setting,
    make_graph_template, get_map_jp_to_en_sub_type
)

import pandas as pd
import plotly.graph_objects as go
import json


def _build_summary(df_balance, df_emergency_buffer):
    latest = get_latest_date()
    latest_beginning_of_month = latest.replace(day=1) 
    three_month_ago = (latest - pd.DateOffset(months=3)) + pd.offsets.MonthBegin(-1)
    six_month_ago = (latest - pd.DateOffset(months=6)) + pd.offsets.MonthBegin(-1)

    #print(latest, latest_beginning_of_month, three_month_ago)

    df = df_balance.copy()

    # Collection
    df_current = (
        df[
            (df["date"] >= three_month_ago) & (df["date"] < latest_beginning_of_month) &
            (df["収支タイプ"] == "一般収支")
        ].groupby("収支カテゴリー")[["金額","目標"]].sum()
    )
    df_past = (
        df[
            (df["date"] >= six_month_ago) & (df["date"] < three_month_ago) &
            (df["収支タイプ"] == "一般収支")
        ].groupby("収支カテゴリー")[["金額","目標"]].sum()
    )

    # Fire Progress-3m
    fire_progress_current = df_current["金額"].sum() / df_current["目標"].sum()
    fire_progress_past = df_past["金額"].sum() / df_past["目標"].sum()

    # Net Saving-3m
    net_saving_current = df_current["金額"].sum()
    net_saving_past = df_past["金額"].sum()

    # Saving Rate-3m
    saving_rate_current = net_saving_current / df_current.loc["収入", "金額"]
    saving_rate_past = net_saving_past / df_past.loc["収入", "金額"]

    # Financial Runway
    emergency_buffer_current = df_emergency_buffer[
        df_emergency_buffer["date"] == latest_beginning_of_month
    ]["資産額"].iloc[0]
    emergency_buffer_past = df_emergency_buffer[
        df_emergency_buffer["date"] == three_month_ago
    ]["資産額"].iloc[0]

    financial_runway_current = emergency_buffer_current / (abs(df_current.loc["支出", "金額"]) / 3)
    financial_runway_past = emergency_buffer_past / (abs(df_past.loc["支出", "金額"]) / 3)

    #print(fire_progress_current, net_saving_current, saving_rate_current, financial_runway_current)
    #print(fire_progress_past, net_saving_past, saving_rate_past, financial_runway_past)

    latest_str = latest.strftime("%y/%m/%d")
    return {
        "latest_date": latest_str,
        "fire_progress_3m": round(fire_progress_current*100,1),
        "fire_progress_3m_vector": make_vector(fire_progress_current, fire_progress_past),
        "net_saving_3m": round(net_saving_current),
        "net_saving_3m_vector": make_vector(net_saving_current, net_saving_past),
        "saving_rate_3m": round(saving_rate_current*100,1),
        "saving_rate_3m_vector": make_vector(saving_rate_current, saving_rate_past),
        "financial_runway": str(round(financial_runway_current)) + " months",
        "financial_runway_vector": make_vector(financial_runway_current, financial_runway_past),
    }

def _build_target_trajectory(df_balance,):
    # 日付設定
    latest = get_latest_date()
    latest_month = latest.replace(day=1)
    three_month_later = latest_month + pd.DateOffset(months=3)
    nine_month_ago = latest_month - pd.DateOffset(months=9)

    #print(latest_month, three_month_later, nine_month_ago)
    #　データ生成
    mask = (
        (df_balance["date"] >= nine_month_ago) & (df_balance["date"] < three_month_later)&
        (df_balance["収支タイプ"] == "一般収支")
    )
    df_sub = df_balance[mask].groupby(["date","収支カテゴリー"])[["金額","目標"]].sum().reset_index()

    #グラフ
    x_values = (
        df_sub[df_sub["収支カテゴリー"]=="収入"].set_index("date")
        .resample("MS").sum().index.strftime("%y-%m").tolist()
    )
    y1_values = (
        df_sub[df_sub["収支カテゴリー"]=="収入"].set_index("date")
        .resample("MS").sum()["金額"].astype(int).tolist()
    )
    y2_values = (
        df_sub[df_sub["収支カテゴリー"]=="収入"].set_index("date")
        .resample("MS").sum()["目標"].astype(int).tolist()
    )
    y3_values = (
        df_sub[df_sub["収支カテゴリー"]=="支出"].set_index("date")
        .resample("MS").sum()["金額"].astype(int).tolist()
    )
    y4_values = (
        df_sub[df_sub["収支カテゴリー"]=="支出"].set_index("date")
        .resample("MS").sum()["目標"].astype(int).tolist()
    )
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_values, y=y1_values, name="Actual Income",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y2_values, mode="lines+markers", name="Target Income",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=x_values, y=y3_values, name="Actual Expense",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y4_values, mode="lines+markers", name="Target Expense",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))

    fig = graph_individual_setting(fig, "date", "%y-%m", "Income and Expense", "¥", "")
    # metaでID付与
    fig.update_layout(meta={"id": "target_trajectory"})

    #fig.show()

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)

    return json_str

def _build_goal_imbalance_map(df_balance,df_item_attribute):
    # 期間設定（3か月）
    latest = get_latest_date()
    latest_month = latest.replace(day=1)
    three_month_ago = latest_month - pd.DateOffset(months=3)

    # 期間分のデータを取得
    mask = (
        (df_balance["date"] >= three_month_ago) & (df_balance["date"] < latest_month) &
        (df_balance["収支タイプ"] == "一般収支")
    )
    df_sub = df_balance[mask].groupby(["収支項目"])[["金額","目標"]].sum().reset_index()
    #print(df_sub)

    # データフレーム作成
    df_sub["diff"] = df_sub["金額"] - df_sub["目標"] #支出も収入もプラスがよい
    df_sub["state"] = df_sub["diff"].apply(
        lambda x: "good" if x >= 0 else "bad"
    )
    max_range = df_sub["diff"].abs().max()
    df_sub["Plot_R"] = df_sub["diff"] + max_range
    df_sub["収支項目"] = df_sub["収支項目"].replace(get_map_jp_to_en_sub_type(df_item_attribute))

    #print(df_sub)

    # 基本設定
    items = df_sub["収支項目"].unique().tolist()
    n_items = len(items)
    items_closed = items + [items[0]]
    
    
    MAX_DEVIATION = max_range
    CENTER_RING_R = max_range
    OUTER_R = max_range * 2
    COLOR_GOOD = 'rgba(100, 200, 100, 0.7)' # 緑系
    COLOR_BAD = 'rgba(255, 100, 100, 0.7)'  # 赤系
    COLOR_LINE = 'rgba(255, 255, 255, 0.8)' # プロット線の色
    POLYGON_COLOR = 'rgba(100, 150, 255, 0.1)'# 青系の半透明で統一
    MARKER_SIZE = 12 # マーカーの大きさ


    # グラフ化
    fig = go.Figure()
    #
    fig.add_trace(go.Scatterpolar(
        r=[CENTER_RING_R] * n_items,
        theta=items,
        fill='toself',
        fillcolor='rgba(255, 150, 150, 0.05)', # 薄い赤の塗りつぶし
        mode='lines',
        line=dict(color='rgba(0,0,0,0)'), # 線は透明
        hoverinfo='none',
        name='Bad Zone'
    ))

    # ポリゴン（レーダーチャートの形状）を追加
    r_values = df_sub['Plot_R'].tolist()
    r_values_closed = r_values + [r_values[0]]
    fig.add_trace(go.Scatterpolar(
        r=r_values_closed,
        theta=items_closed,
        fill='toself',                          # 図形を塗りつぶす
        fillcolor=POLYGON_COLOR,                # ポリゴンの色
        mode='lines+markers',                   # 線とマーカーを表示
        line=dict(color='white', width=2),      # 線を白で強調
        marker=dict(size=MARKER_SIZE, symbol='circle', color='white'),
        name='Actual Deviation Shape'
    ))

    for item in items:
        row = df_sub[df_sub['収支項目'] == item].iloc[0]
        # 良し悪しに応じてマーカーの色を設定
        marker_color = 'lightgreen' if row['state'] == 'good' else 'orangered'

        # プロットライン
        fig.add_trace(go.Scatterpolar(
            r=[row['Plot_R']],
            theta=[item],
            mode='markers',
            marker=dict(size=MARKER_SIZE + 2, color=marker_color, line=dict(width=2, color='white')),
            name=f'{item}: {row["diff"]:.1f} 万円',
            customdata=[f'diff: {row["diff"]:.1f} 万円'],
            showlegend=False # 凡例が煩雑になるため非表示
        ))

    # --- 6. レイアウト設定 ---
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, OUTER_R],
                tickvals=[0, CENTER_RING_R, OUTER_R],
                ticktext=['Max Bad (-12万)', 'Goal (0万)', 'Max Good (+12万)'],
                linecolor='gray',
                gridcolor='lightgray',
                gridwidth=1,
                griddash='dot',
                #gridcolor='white'
            ),
            angularaxis=dict(
                direction="clockwise",
                period=n_items
            )
        ),
        title='Goal Imbalance Map (Central Ring Goal)',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template="plotly_dark" 
    )
    fig.add_trace(go.Scatterpolar(
        r=[CENTER_RING_R] * (n_items + 1), # 長さを合わせる
        theta=items_closed,
        mode='lines',
        # 線を太くし、点線/実線は視認性の良いものを選択
        line=dict(color='yellow', width=5, dash='dot'), 
        hoverinfo='none',
        name='Goal Line (0 Dev)'
    ))

    fig.show()
    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    
    return json_str
    

def build_Cashflow_Analytics_payload(include_graphs=False, include_summary=False):
    df_balance, df_item_attribute, df_emergency_buffer = read_table_from_db()

    result = {"ok":True, "summary": {}, "graphs": {}}
    
    make_graph_template()
    
    if include_summary:
        result["summary"] = _build_summary(df_balance,df_emergency_buffer)
        
    if include_graphs:
        result["graphs"] = {
            "target_trajectory": _build_target_trajectory(df_balance),
            "goal_imbalance_map": _build_goal_imbalance_map(df_balance,df_item_attribute),
            #"portfolio_efficiency_map": _build_portfolio_efficiency_map(df_collection,df_item_attribute),
            #"liquidity_pyramid": _build_liquidity_pyramid(df_collection,df_item_attribute),
            #"true_risk_exposure_flow": _build_true_risk_exposure_flow(df_collection),
            #"liquidity_horizon": _build_liquidity_horizon(df_collection_latest, df_asset_attribute, df_item_attribute)
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

    df_balance, df_item_attribute, df_emergency_buffer = read_table_from_db()
    #print(_build_summary(df_balance,df_emergency_buffer))
    #_build_target_trajectory(df_balance)
    #_build_goal_imbalance_map(df_balance,df_item_attribute)
    #print(build_Cashflow_Analytics_payload(include_graphs=False, include_summary=True))