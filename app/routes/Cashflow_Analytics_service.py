from .Cashflow_Analytics_service_detail import read_table_from_db
from app.utils.data_loader import get_latest_date
from app.utils.dashboard_utility import make_vector

import pandas as pd


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

def build_Cashflow_Analytics_payload(include_graphs=False, include_summary=False):
    df_balance, df_item_attribute, df_emergency_buffer = read_table_from_db()

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = _build_summary(df_balance,df_emergency_buffer)
        
    if include_graphs:
        result["graphs"] = {
            #"r": _build_asset_tree_map(df_collection,df_item_attribute),
            #"target_deviation": _build_target_deviation(df_collection),
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
    print(_build_summary(df_balance,df_emergency_buffer))
    #print(build_Cashflow_Analytics_payload(include_graphs=False, include_summary=True))