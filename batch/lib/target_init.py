import pandas as pd
from .decorator import require_columns, check_args_types


def make_target_parameter(df_raw, start_date, end_date):
    """
    目標パラメータファイルを読み込み、日付列を処理してデータフレームを準備します。

    Args:
        filepath (str): 目標パラメータファイルのパス。
        start_date (str): デフォルトの開始日（"TBD"の場合に適用）。
        end_date (str): デフォルトの終了日（"TBD"の場合に適用）。

    Returns:
        pd.DataFrame: 処理された目標パラメータデータフレーム。
    """
    df = df_raw.copy()
    df["開始日"] = df["開始日"].replace("TBD", start_date)
    df["終了日"] = df["終了日"].replace("TBD", end_date)

    date_cols = ["開始日", "終了日", "特定日"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], format="%Y-%m-%d",errors="raise")
    return df

def make_cross_df(df_items, start_date, end_date):
    """
    日付範囲と項目データフレームをクロス結合し、すべての日付と項目の組み合わせを含むデータフレームを作成します。

    Args:
        df_items (pd.DataFrame): クロス結合する項目データフレーム。
                                 "繰り返し設定"、"日"、"月"などの列が含まれていることを想定しています。
        start_date (str): 日付範囲の開始日。
        end_date (str): 日付範囲の終了日。

    Returns:
        pd.DataFrame: 日付と項目をクロス結合したデータフレーム。
    """
    dates = pd.date_range(start_date, end_date)
    df_dates = pd.DataFrame({"日付": dates})

    df_items_copy = df_items.copy()
    df_cross = df_dates.merge(df_items_copy, how='cross')
    return df_cross


