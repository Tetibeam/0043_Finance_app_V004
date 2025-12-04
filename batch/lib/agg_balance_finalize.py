from ..lib import reference_data_store as urds
import pandas as pd
import itertools
from .decorator import require_columns, check_args_types


def fill_missing_dates(start_date, end_date, df):
    items = ['車検A', '給与', '車検B', 'ポイント', 'NTT', '車', '年金', '児童手当', '生活費',
            '子供費用', 'ローン返済', 'ローン一括', '所得税還付', '特典', '家電', 'ふるさと納税',
            '固定資産税', '自動車税', '子供', '年末調整', '賞与', '退職金', '贈与']

    all_combinations = pd.DataFrame(
        list(itertools.product(pd.date_range(start_date, end_date, freq="D"), items)),
        columns=["date", "収支項目"]

    )
    df_full = pd.merge(all_combinations, df, on=["date", "収支項目"], how="left")
    df_full["金額"] = df_full["金額"].fillna(0)
    return df_full

def add_type_and_category(df):
    df["収支タイプ"] = pd.Series(dtype="object")
    df["収支カテゴリー"] = pd.Series(dtype="object")
    item_cols = df["収支項目"].unique().tolist()
    df_tmp = urds.df_balance_type_and_category

    for item in item_cols:
        type = df_tmp.loc[df_tmp["収支項目"] == item, "収支タイプ"].iloc[0]
        category = df_tmp.loc[df_tmp["収支項目"] == item, "収支カテゴリー"].iloc[0]
        df.loc[df["収支項目"] == item, "収支タイプ"] = type
        df.loc[df["収支項目"] == item, "収支カテゴリー"] = category
    return df

def add_target(start_date, end_date, df):
    mask = (df["date"] >= start_date) & (df["date"] <= end_date)
    df = df[mask]

    mask = (urds.df_balance_target["date"] >= start_date) & (urds.df_balance_target["date"] <= end_date)
    df_target = urds.df_balance_target[mask]
    df_target = df_target[~df_target["収支項目"].str.contains("年金拠出", na=False)]
    df_target.loc[df_target["収支カテゴリー"] == "支出", "目標"] *= -1

    df_merge = pd.merge(df, df_target,on=["date","収支項目","収支タイプ","収支カテゴリー"],how="outer")
    return df_merge

@check_args_types({0: pd.Timestamp, 1: pd.Timestamp})
@require_columns(["date", "収支項目", "金額",'内容', '保有金融機関', '大項目', '中項目', 'メモ'], df_arg_index=2)
def finalize_data(start_date, end_date, df):
    df_finalized = df.copy()
    # 不要列を削除し、日付順に並び替えます
    df_removed = df_finalized.drop(['内容', '保有金融機関', '大項目', '中項目', 'メモ'], axis=1)\
        .sort_values(["date"])
    # 同じ日付、収支項目については合計にします。
    df_unify = df_removed.groupby(["date", "収支項目"], as_index=False)["金額"].sum()
    # 空いている日付はゼロを埋めます。
    df_filled_missing_dates = fill_missing_dates(start_date, end_date, df_unify)
    # 収支タイプと収支カテゴリーを追加します。
    df_add_type = add_type_and_category(df_filled_missing_dates)
    # 目標の列を追加します。
    df_add_target = add_target(start_date, end_date, df_add_type)

    return df_add_target
