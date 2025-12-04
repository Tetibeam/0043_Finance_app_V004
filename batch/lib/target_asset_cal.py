from .target_balance_cal import cal_total_balance
from .decorator import require_columns, require_columns_with_dtype, check_args_types
from ..lib import reference_data_store as urds
import pandas as pd
import numpy as np

def _set_target_rate(df_target_rate, rate_name, dates):
    """
    指定された日付範囲とレート名に基づいて、目標レートの時系列データを生成します。

    Args:
        df_target_rate (pd.DataFrame): 目標レートデータを含むデータフレーム。
                                       "日付" と指定された `rate_name` の列が必要です。
        rate_name (str): 抽出するレートの列名（例: "安全資産", "リスク資産"）。
        dates (pd.DatetimeIndex): レートを計算する日付範囲。

    Returns:
        np.ndarray: 指定された日付範囲に対応する目標レートのNumPy配列。
    """

    df = df_target_rate[['日付', rate_name]].copy()
    df.dropna(inplace=True)

    key_dates = pd.to_datetime(df["日付"].values)
    key_values = df[rate_name].values

    # 日付を整数（days）に変換
    x = (dates - dates[0]).days
    xp = (key_dates - dates[0]).days

    # 線形補間
    target_ratio = np.interp(x, xp, key_values)
    return target_ratio

def _set_loan_interest(df_target_rate, rate_name, dates):
    df = df_target_rate[['日付', rate_name]].copy()
    df.dropna(inplace=True)

    key_dates = pd.to_datetime(df["日付"].values)
    key_values = df[rate_name].values

    dates = pd.to_datetime(dates)

    # searchsortedに使うため int64 に変換して nanosecond を比較値にする
    key_int = key_dates.view('int64')
    date_int = dates.view('int64')

    # ★各 date に対して、key_dates の「直前の位置」を取得
    # side='right' → 同日ならその値を使う
    idx = np.searchsorted(key_int, date_int, side='right') - 1

    # 範囲外（最古の日付より前）の場合は欠損にする（必要に応じて処理変更）
    idx[idx < 0] = 0

    # 前回値をそのまま拾う
    target_ratio = key_values[idx]

    return target_ratio

def _cal_long_col_data(safe_asset, risky_asset, loan_balance,
    safe_total_return, risky_total_return, safe_ratio,
    risky_ratio, safe_return, risky_return, loan_interest, dates):
    """
    指定された資産データと日付に基づいて、長期形式のデータフレームを作成するための列データを生成します。

    Args:
        safe_asset (np.ndarray): 安全資産の日ごとの値。
        risky_asset (np.ndarray): リスク資産の日ごとの値。
        safe_total_return (np.ndarray): 安全資産のトータルリターン。
        risky_total_return (np.ndarray): リスク資産のトータルリターン。
        safe_ratio (np.ndarray): 安全資産の配分比率。
        risky_ratio (np.ndarray): リスク資産の配分比率。
        safe_return (np.ndarray): 安全資産の利回り。
        risky_return (np.ndarray): リスク資産の利回り。
        dates (pd.DatetimeIndex): 日付範囲。

    Returns:
        tuple: date_col, asset_type_col, asset_col, return_col, asset_ratio_col, return_ratio_col
               (それぞれ日付、資産タイプ、資産額、トータルリターン、資産配分率、利回りのNumPy配列)
    """
    # --- 日付列 ---
    #date_col = np.repeat(dates.values, 2)  # 各日を2回繰り返す（安全・リスク）
    date_col = np.repeat(dates.values, 3)  # 各日を3回繰り返す（安全・リスク・負債）
    n_days = len(dates)
 
    # --- 資産タイプ列 ---
    asset_types = ["安全資産", "リスク資産", "負債"]
    #asset_type_col = np.tile(asset_types, n_days)  # 交互に並べる
    asset_type_col = np.tile(asset_types, n_days)

    # --- 資産額列 ---
    #asset_col = np.empty(n_days*2)
    #asset_col[0::2] = safe_asset
    #asset_col[1::2] = risky_asset
    asset_col = np.column_stack([safe_asset, risky_asset, loan_balance]).ravel()

    # --- トータルリターン列 ---
    #return_col = np.empty(n_days*2)
    #return_col[0::2] = safe_total_return
    #return_col[1::2] = risky_total_return
    debt_total_return = np.full(n_days, np.nan)
    return_col = np.column_stack([safe_total_return, risky_total_return, debt_total_return]).ravel()

    # --- 各日パラメータ列 ---
    #asset_ratio_col = np.empty(n_days*2)
    #asset_ratio_col[0::2] = safe_ratio
    #asset_ratio_col[1::2] = risky_ratio
    debt_ratio = np.full(n_days, np.nan)
    asset_ratio_col = np.column_stack([safe_ratio, risky_ratio, debt_ratio]).ravel()

    # 安全資産行に安全資産パラメータ、リスク資産行にリスク資産パラメータ
    #return_ratio_col = np.empty(n_days*2)
    #return_ratio_col[0::2] = safe_return*365
    #return_ratio_col[1::2] = risky_return*365
    return_ratio_col = np.column_stack([safe_return*365, risky_return*365, loan_interest*365]).ravel()

    return date_col, asset_type_col, asset_col, return_col, asset_ratio_col, return_ratio_col

def _cal_target_data(safe_ratio, risky_ratio, safe_return, risky_return, loan_interest, df_balance, INITIAL_ASSET, INITIAL_LOAN, dates):
    """
    目標資産データを計算します。

    Args:
        safe_ratio (np.ndarray): 安全資産の配分比率の時系列データ。
        risky_ratio (np.ndarray): リスク資産の配分比率の時系列データ。
        safe_return (np.ndarray): 安全資産の利回りの時系列データ。
        risky_return (np.ndarray): リスク資産の利回りの時系列データ。
        df_balance (pd.DataFrame): 収支データを含むデータフレーム。
        INITIAL_ASSET (float): 初期資産額。
        dates (pd.DatetimeIndex): 計算対象となる日付範囲。

    Returns:
        pd.DataFrame: 日付、資産タイプ、資産額、資産配分率、トータルリターン、利回りを含む長期形式のデータフレーム。
    """
    n_days = len(dates)
    # --- 計算用配列 ---
    asset = np.zeros(n_days)
    safe_asset = np.zeros(n_days)
    risky_asset = np.zeros(n_days)
    total_return = np.zeros(n_days)
    safe_total_return = np.zeros(n_days)
    risky_total_return = np.zeros(n_days)
    loan_balance = np.zeros(n_days)
    mask = df_balance["収支項目"].isin(["ローン返済", "ローン一括"])
    loan_repayment = df_balance[mask].groupby("date")["目標"].sum().values
    #print(loan_repayment)

    # --- 初日設定 ---
    asset[0] = INITIAL_ASSET
    safe_asset[0] = asset[0] * safe_ratio[0]
    risky_asset[0] = asset[0] * risky_ratio[0]
    total_return[0] = 0
    loan_balance[0] = INITIAL_LOAN

    # --- 収支設定 ---
    balance_cash = cal_total_balance(df_balance, dates)

    # --- 日次再帰計算 ---
    for i in range(1, n_days):
        # 前日資産 + 収支
        prev_total = asset[i-1] + balance_cash[i-1]
        prev_loan_balance = loan_balance[i-1]

        # 安全資産・リスク資産に配分
        safe_asset[i] = prev_total * safe_ratio[i]
        risky_asset[i] = prev_total * risky_ratio[i]

        # トータルリターン
        safe_total_return[i] = safe_asset[i] * safe_return[i]
        risky_total_return[i] = risky_asset[i] * risky_return[i]

        # 当日資産額 = 前日資産 + 収支 + 当日リターン
        asset[i] = prev_total + safe_total_return[i] +risky_total_return[i]
        loan_balance[i] = (
            prev_loan_balance +                     # 前日残高
            (prev_loan_balance * loan_interest[i])  # 利息払い
            + loan_repayment[i]                     # 貸返済
        )
        if loan_balance[i] > 0:
            loan_balance[i] = 0

    safe_total_return = np.cumsum(safe_total_return)
    risky_total_return = np.cumsum(risky_total_return)

    # --- long型データフレーム作成 ---
    date_col, asset_type_col, asset_col, return_col, asset_ratio_col, return_ratio_col =\
        _cal_long_col_data(
            safe_asset, risky_asset, loan_balance, safe_total_return, risky_total_return,
            safe_ratio, risky_ratio, safe_return, risky_return, loan_interest, dates
        )
    df_long = pd.DataFrame({
        "date": date_col,
        "資産タイプ": asset_type_col,
        "資産額": asset_col,
        "資産配分率": asset_ratio_col,
        "トータルリターン": return_col,
        "利回り": return_ratio_col,
    })
    return df_long

@check_args_types({1: str, 2: str, 3: float})
def build_asset_profit_target(df_balance, start_date, end_date, initial_asset, initial_loan):
    
    df_rate =  urds.df_target_rate.sort_values("日付")
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    risky_ratio = _set_target_rate(df_rate, "リスク資産配分率", dates)
    safe_ratio = 1 - risky_ratio

    safe_return = _set_target_rate(df_rate, "安全資産利回り", dates) / 365
    risky_return = _set_target_rate(df_rate, "リスク資産利回り", dates) / 365

    loan_interest = _set_loan_interest(df_rate, "ローン金利", dates) / 365
    
    return _cal_target_data(
        safe_ratio, risky_ratio,
        safe_return, risky_return,
        loan_interest, df_balance,
        initial_asset, initial_loan, dates
    )