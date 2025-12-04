from .target_init import make_target_parameter, make_cross_df
import pandas as pd
import numpy as np
from .decorator import require_columns, require_columns_with_dtype, check_args_types

def _set_monthly_balance_by_repeat_setting(df_cross: pd.DataFrame, verbose: bool=False):
    df = df_cross[df_cross["繰り返し設定"] == "MONTHLY"].copy()
    if df.empty:
        if verbose:
            print(f"[INFO] 該当データなし: 繰り返し設定=MONTHLY")
        return pd.DataFrame(columns=df_cross.columns)

    # --- 各繰り返し設定に応じたマスク作成 ---
    mask_period = (df["日付"] >= df["開始日"]) & (df["日付"] <= df["終了日"])
    mask_repeat = df["日付"].dt.day == df["日"]

    df["目標"] = np.where(mask_period & mask_repeat, df["目標"], 0)
    # --- 結果とログ ---
    if verbose:
        n_active = (mask_period & mask_repeat).sum()
        print(f"[INFO] {"MONTHLY"}: {len(df):,}行中 {n_active:,}行が有効期間・繰り返し日に該当")
    return df

def _set_annually_balance_by_repeat_setting(df_cross: pd.DataFrame, verbose: bool=False):
    df = df_cross[df_cross["繰り返し設定"] == "ANNUALLY"].copy()
    if df.empty:
        if verbose:
            print(f"[INFO] 該当データなし: 繰り返し設定=ANNUALLY")
        return pd.DataFrame(columns=df_cross.columns)

    # --- 各繰り返し設定に応じたマスク作成 ---
    mask_period = (df["日付"] >= df["開始日"]) & (df["日付"] <= df["終了日"])
    mask_repeat = (df["日付"].dt.day == df["日"]) & (df["日付"].dt.month == df["月"])

    df["目標"] = np.where(mask_period & mask_repeat, df["目標"], 0)
    # --- 結果とログ ---
    if verbose:
        n_active = (mask_period & mask_repeat).sum()
        print(f"[INFO] {"ANNUALLY"}: {len(df):,}行中 {n_active:,}行が有効期間・繰り返し日に該当")
    return df

def _set_every_2_years_balance_by_repeat_setting(df_cross: pd.DataFrame, verbose: bool=False):
    df = df_cross[df_cross["繰り返し設定"] == "EVERY 2 YEARS"].copy()
    if df.empty:
        if verbose:
            print(f"[INFO] 該当データなし: 繰り返し設定=EVERY 2 YEARS")
        return pd.DataFrame(columns=df_cross.columns)

    # --- 各繰り返し設定に応じたマスク作成 ---
    mask_period = (df["日付"] >= df["開始日"]) & (df["日付"] <= df["終了日"])
    mask_repeat = (
        (df["日付"].dt.month == df["月"]) &
        (df["日付"].dt.day == df["日"]) &
        ((df["日付"].dt.year - df["開始日"].dt.year) % 2 == 0)
    )

    df["目標"] = np.where(mask_period & mask_repeat, df["目標"], 0)
    # --- 結果とログ ---
    if verbose:
        n_active = (mask_period & mask_repeat).sum()
        print(f"[INFO] {"EVERY 2 YEARS"}: {len(df):,}行中 {n_active:,}行が有効期間・繰り返し日に該当")
    return df

def _set_every_3_years_balance_by_repeat_setting(df_cross: pd.DataFrame, verbose: bool=False):
    df = df_cross[df_cross["繰り返し設定"] == "EVERY 3 YEARS"].copy()
    if df.empty:
        if verbose:
            print(f"[INFO] 該当データなし: 繰り返し設定=EVERY 3 YEARS")
        return pd.DataFrame(columns=df_cross.columns)

    # --- 各繰り返し設定に応じたマスク作成 ---
    mask_period = (df["日付"] >= df["開始日"]) & (df["日付"] <= df["終了日"])
    mask_repeat = (
        (df["日付"].dt.month == df["月"]) &
        (df["日付"].dt.day == df["日"]) &
        ((df["日付"].dt.year - df["開始日"].dt.year) % 3 == 0)
    )

    df["目標"] = np.where(mask_period & mask_repeat, df["目標"], 0)
    # --- 結果とログ ---
    if verbose:
        n_active = (mask_period & mask_repeat).sum()
        print(f"[INFO] {"EVERY 3 YEARS"}: {len(df):,}行中 {n_active:,}行が有効期間・繰り返し日に該当")
    return df


def _set_specific_balance_by_repeat_setting(df_cross: pd.DataFrame, verbose: bool=False):
    df = df_cross[df_cross["繰り返し設定"] == "SPECIFIC"].copy()
    if df.empty:
        if verbose:
            print(f"[INFO] 該当データなし: 繰り返し設定=SPECIFIC")
        return pd.DataFrame(columns=df_cross.columns)

    # --- 各繰り返し設定に応じたマスク作成 ---
    if "特定日" not in df.columns:
        raise ValueError("SPECIFIC設定には '特定日' 列が必要です。")
    mask_period = True
    mask_repeat = df["日付"] == df["特定日"]

    df["目標"] = np.where(mask_period & mask_repeat, df["目標"], 0)
    # --- 結果とログ ---
    if verbose:
        n_active = (mask_period & mask_repeat).sum()
        print(f"[INFO] {"SPECIFIC"}: {len(df):,}行中 {n_active:,}行が有効期間・繰り返し日に該当")
    return df

@require_columns(["繰り返し設定", "開始日", "終了日", "月", "日", "特定日"], df_arg_index=0)
@require_columns_with_dtype({"繰り返し設定": object, "開始日": "datetime64[ns]","終了日": "datetime64[ns]",
                             "月": "float64", "日": "float64", "特定日": "datetime64[ns]"}, df_arg_index=0)
def _cal_balance_target(df_cross):
    FUNCTIONS = [
        _set_monthly_balance_by_repeat_setting,
        _set_annually_balance_by_repeat_setting,
        _set_every_2_years_balance_by_repeat_setting,
        _set_every_3_years_balance_by_repeat_setting,
        _set_specific_balance_by_repeat_setting,
    ]
    df = pd.DataFrame()
    df = pd.concat([fn(df_cross, False) for fn in FUNCTIONS], ignore_index=True)
    
    return df

def _clear_duplicated_balance_data(df_balance):
    """
    重複する収支データをクリアし、目標値が0でないデータを優先します。
    同一日付＋収支項目で非ゼロがある場合はゼロ行を削除し、非ゼロがない場合はゼロ1行を残す。

    Args:
        df_balance (pd.DataFrame): 収支データを含むデータフレーム。
                                   "日付", "収支項目", "目標" の列が必要です。

    Returns:
        pd.DataFrame: 重複がクリアされたデータフレーム。
    """
    df = df_balance.copy()

    nonzero_keys = df.loc[df['目標'] != 0, ['日付','収支項目']].drop_duplicates()

    df_zero = df[df['目標'] == 0]
    df_zero = df_zero.merge(nonzero_keys, on=['日付','収支項目'], how='left', indicator=True)
    df_zero = df_zero[df_zero['_merge'] == 'left_only'].drop(columns=['_merge'])
    df_zero = df_zero.drop_duplicates(subset=['日付','収支項目'])

    df_nonzero = df[df['目標'] != 0]
    df_final = pd.concat([df_nonzero, df_zero], axis=0)
    df_final = df_final.sort_values("日付")

    return df_final

def _finalize_balance(df_balance):
    drop_cols = ['繰り返し設定', '開始日', '終了日', '月', '日', '特定日']
    return (
        df_balance
        .sort_values("日付")
        .rename(columns={"日付": "date"})
        .reset_index(drop=True)
        .drop(columns=drop_cols, errors='ignore')
    )

def cal_total_balance(df_balance, dates):
    """
    指定された日付範囲に基づいて、収支データから日ごとの合計残高を計算します。

    Args:
        df_balance (pd.DataFrame): 収支データを含むデータフレーム。
                                   "日付", "収支カテゴリー", "目標" の列が必要です。
        dates (pd.DatetimeIndex): 計算対象となる日付範囲。

    Returns:
        np.ndarray: 指定された日付範囲に対応する日ごとの合計残高のNumPy配列。
    """
    df = df_balance.copy()

    df_income = df[df["収支カテゴリー"]=="収入"]
    df_income = df_income.groupby("date", as_index=False)["目標"].sum().set_index("date")

    df_expenditure = df[df["収支カテゴリー"]=="支出"]
    df_expenditure = df_expenditure.groupby("date", as_index=False)["目標"].sum().set_index("date")

    df_result = (df_income-df_expenditure).reset_index()

    # --- NumPy配列に変換 ---
    dates_np = df_result["date"].to_numpy()
    target_np = df_result["目標"].to_numpy()

    # ユニーク日付とインデックス取得
    unique_dates, indices = np.unique(dates_np, return_inverse=True)

    # 日付ごとの合計用配列
    balance_cash = np.zeros(len(unique_dates))
    np.add.at(balance_cash, indices, target_np)
    return balance_cash

@require_columns(["開始日", "終了日", "特定日"], df_arg_index=0)
@check_args_types({1: str, 2: str})
def build_balance_target(df_raw, start, end):
    df_items = make_target_parameter(df_raw, start, end)
    if df_items.empty:
        raise ValueError("対象パラメータが空です。start/endの設定や入力データを確認してください。")
    df_cross = make_cross_df(df_items, start, end)

    df_balance = (
        _cal_balance_target(df_cross)
        .pipe(_clear_duplicated_balance_data)
        .pipe(_finalize_balance)
    )
    return df_balance