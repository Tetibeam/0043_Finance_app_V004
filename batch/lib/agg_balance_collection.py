import pandas as pd
from .reference_data_store import BALANCE_RULES
from .decorator import require_columns, check_args_types

def filter_and_clean_raw(start_date, end_date, df):
    df_filtered = df.drop(["計算対象", "振替", "ID"], axis=1)
    df_filtered = df_filtered.rename(columns={"日付": "date","金額（円）":"金額"})
    df_filtered["date"] = pd.to_datetime(df_filtered["date"], format="%Y/%m/%d")
    df_filtered = df_filtered[(df_filtered["date"] >= start_date) & (df_filtered["date"] <= end_date)]

    return df_filtered.sort_values("date")

def single_filter_df_by_value(df_raw, filter_col, filter_value):
    return df_raw[df_raw[filter_col].str.contains(filter_value, na=False,regex=False)]

def single_filter_df_exact_match_by_value(df_raw, filter_col, filter_value):
    return df_raw[df_raw[filter_col] == filter_value]

def double_filter_df_by_value(df_raw, filter_col1, filter_value1, filter_col2, filter_value2):
    return df_raw[(df_raw[filter_col1].str.contains(filter_value1, na=False,regex=False)) &
                  (df_raw[filter_col2].str.contains(filter_value2, na=False,regex=False))]

def set_detail_from_raw(df_detail, df_filtered, item):
    df = df_filtered.copy()
    df["収支項目"] = item
    return pd.concat([df_detail, df], ignore_index=True)

@require_columns(["date", "金額", "保有金融機関", "大項目", "中項目", "内容", "メモ"], df_arg_index=1)
def collect_balance(df_balance_detail, df_raw):
    def combine(*dfs):
        dfs = [d for d in dfs if d is not None and not d.empty]
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    for category, conditions in BALANCE_RULES.items():
        dfs = []
        for cond in conditions:
            if len(cond) == 2 and isinstance(cond[0], str):
                dfs.append(single_filter_df_by_value(df_raw, cond[0], cond[1]))
            else:
                dfs.append(double_filter_df_by_value(df_raw, cond[0][0], cond[0][1], cond[1][0], cond[1][1]))

        df_tmp = combine(*dfs)
        df_balance_detail = set_detail_from_raw(df_balance_detail, df_tmp, category)

    return df_balance_detail

def collect_living_adjust(df_balance_detail):
    accounts = ["PayPayカード", "Amazon.co.jp", "楽天市場", "Yahoo!ショッピング", "さとふる", "楽天市場(my Rakuten)"]
    items = ["子供費用","子供","家電","ふるさと納税","固定資産税","自動車税"]

    df_Living_adjust = pd.DataFrame()
    for item in items:
        for account in accounts:
            df = single_filter_df_exact_match_by_value(df_balance_detail, "収支項目", item)
            df = single_filter_df_by_value(df, "保有金融機関", account)
            df_Living_adjust = pd.concat([df_Living_adjust, df], axis=0)
            #display(df)
    monthly_sum = (
        df_Living_adjust.groupby(df_Living_adjust["date"].dt.to_period("M"))["金額"]
        .sum()
        .reset_index()
    )
    monthly_sum["金額"] = -monthly_sum["金額"]
    monthly_sum["date"] = monthly_sum["date"].dt.to_timestamp() + pd.offsets.MonthBegin(1)
    df_balance_detail = set_detail_from_raw(df_balance_detail, monthly_sum, "生活費")
    return df_balance_detail

@check_args_types({1: pd.Timestamp, 2: pd.Timestamp})
def collect_year_end_tax_adjustment(df_balance_detail, start_date, end_date):
    dates = pd.date_range(start_date, end_date)
    # 年ごとの年末調整額を辞書で管理
    bonus_dict = {
        2025: 250000,
        2026: 0,
    }
    df = pd.DataFrame({"date": dates[(dates.month == 1) & (dates.day == 25)]})
    df["収支項目"] = "年末調整"
    df["金額"] = df["date"].dt.year.map(bonus_dict).fillna(0.0)
    df_balance_detail = set_detail_from_raw(df_balance_detail, df, "年末調整")

    df = pd.DataFrame({"date": dates[(dates.month == 1) & (dates.day == 25)]})
    # 年ごとに辞書から金額を取得
    df["収支項目"] = "給与"
    df["金額"] = df["date"].dt.year.map(bonus_dict).fillna(0.0)*-1
    df_balance_detail = set_detail_from_raw(df_balance_detail, df, "給与")
    return df_balance_detail

def collect_points(df_balance_detail, df_asset_profit):
    df = df_asset_profit[df_asset_profit["資産サブタイプ"] == "ポイント"].copy()
    df = df.groupby(df["date"])["資産額"].sum()
    df = df.diff().reset_index().fillna(0.0)
    df = df.rename(columns={"資産額":"金額"})

    df_balance_detail = set_detail_from_raw(df_balance_detail, df, "ポイント")

    return df_balance_detail
