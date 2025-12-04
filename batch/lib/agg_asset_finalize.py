import pandas as pd
import numpy as np
import numpy_financial as npf
from monthdelta import monthmod
import datetime
from ..lib import reference_data_store as urds
from .decorator import require_columns
from .main_helper import safe_pipe
from .file_io import save_csv
import subprocess
from .agg_settings import PATH_ASSET_TYPE_AND_CATEGORY

def check_not_registered_columns_before_finalize(df):
    latest_date = df["date"].max()
    asset_name_list_latest = df[df["date"] == latest_date]["資産名"].to_list()
    master_df = urds.df_asset_type_and_category
    asset_name_list_ref = master_df["資産名"].to_list()

    diff_list = list(set(asset_name_list_latest) - set(asset_name_list_ref))
    if diff_list:
        try:
            new_rows = pd.DataFrame({"資産名": diff_list})
            updated_master_df = pd.concat([master_df, new_rows], ignore_index=True)
            urds.df_asset_type_and_category = updated_master_df

            save_csv(updated_master_df, PATH_ASSET_TYPE_AND_CATEGORY)
            subprocess.Popen(['start', '', PATH_ASSET_TYPE_AND_CATEGORY], shell=True)
        except Exception as e:
            print(f"マスタファイルを開けませんでした: {e}")
        raise ValueError(
            f"以下の資産名がマスタ未登録です: {diff_list}。"
            "マスタの資産タイプ,資産カテゴリー,資産サブタイプ、データを修正してください。"
        )

def add_columns(df):
    df_added = df.copy()
    df_added["資産タイプ"] = pd.Series(dtype="object")
    df_added["資産カテゴリー"] = pd.Series(dtype="object")
    df_added["資産サブタイプ"] = pd.Series(dtype="object")
    df_added["トータルリターン"] = np.nan
    return df_added

def fill_missing_dates_forward(df, df_asset_profit):
    # 全日付のDataFrameを作る
    start_date = df_asset_profit["date"].max()
    all_dates = pd.DataFrame({"date": pd.date_range(start_date, df["date"].max())})
    
    # 各資産ごとに処理
    results = []
    for asset, g in df.groupby("資産名"):

        merged = pd.merge_asof(all_dates, g.sort_values("date"), on="date", direction="backward")
        merged["資産名"] = asset

        min_date = g["date"].min()
        merged = merged[merged["date"] >= min_date]

        results.append(merged)
    filled = pd.concat(results, ignore_index=True)

    df_before = df[df["date"] < start_date]
    df_updated = pd.concat([df_before, filled], ignore_index=True)
    df_filled_final = df_updated.sort_values(["date","資産名"]).reset_index(drop=True)
    return df_filled_final

def fill_missing_asset_name(df, df_asset_profit):
    df_data = df.copy()
    df_data.reset_index(drop=True, inplace=True)
    df_ref = urds.df_asset_type_and_category.copy()

    end_date = df_asset_profit["date"].max()
    dfs = []
    for date in pd.date_range(start="2024-12-01", end=end_date):
        asset_list_data = df_data[df_data["date"] == date]["資産名"].to_list()
        asset_list_ref = df_ref["資産名"].to_list()
        diff_list = list(set(asset_list_ref) - set(asset_list_data))
        df_add = pd.DataFrame({\
            "date": date,"資産名": diff_list,\
            "資産タイプ":np.nan,"資産カテゴリー":np.nan,"資産サブタイプ":np.nan,\
            "金融機関口座":np.nan,"資産額": 0.0,"トータルリターン":np.nan,\
            "含み損益":np.nan,"実現損益":np.nan,"取得価格":0.0})
        dfs.append(df_add)
    df_result = pd.concat(dfs, ignore_index=True)
    df_final = pd.concat([df_data, df_result],axis=0)
    return df_final

def fill_missing_others_fast(df):
    df_filled = df.copy()
    df_ref = urds.df_asset_type_and_category

    # mapping dict
    type_map      = df_ref.set_index("資産名")["資産タイプ"]
    category_map  = df_ref.set_index("資産名")["資産カテゴリー"]
    subtype_map   = df_ref.set_index("資産名")["資産サブタイプ"]
    account_map   = df_ref.set_index("資産名")["金融機関口座"]

    # 資産名が None の行はスキップするための mask
    mask = df_filled["資産名"].notna()

    # 更新対象の行だけ map する
    df_filled.loc[mask, "資産タイプ"]      = df_filled.loc[mask, "資産名"].map(type_map)
    df_filled.loc[mask, "資産カテゴリー"]  = df_filled.loc[mask, "資産名"].map(category_map)
    df_filled.loc[mask, "資産サブタイプ"]  = df_filled.loc[mask, "資産名"].map(subtype_map)
    df_filled.loc[mask, "金融機関口座"]    = df_filled.loc[mask, "資産名"].map(account_map)

    return df_filled

def fill_missing_others(df):
    df_filled = df.copy()
    item_cols = df_filled["資産名"].dropna().unique().tolist()
    df_tmp = urds.df_asset_type_and_category
    #display(item_cols)
    for item in item_cols:
        type = df_tmp.loc[df_tmp["資産名"] == item, "資産タイプ"].iloc[0]
        category = df_tmp.loc[df_tmp["資産名"] == item, "資産カテゴリー"].iloc[0]
        subtype = df_tmp.loc[df_tmp["資産名"] == item, "資産サブタイプ"].iloc[0]
        account = df_tmp.loc[df_tmp["資産名"] == item, "金融機関口座"].iloc[0]

        df_filled.loc[df["資産名"] == item, "資産タイプ"] = type
        df_filled.loc[df["資産名"] == item, "資産カテゴリー"] = category
        df_filled.loc[df["資産名"] == item, "資産サブタイプ"] = subtype
        df_filled.loc[df["資産名"] == item, "金融機関口座"] = subtype
    return df_filled

def cal_pension(df, df_asset_profit):
    df_cal = df.copy()
    start_date_PersonalPension = datetime.date(2012,3,28)
    start_date = df_asset_profit["date"].max().date()
    end_date = df_cal["date"].max().date()
    for date in pd.date_range(start=start_date, end=end_date):
        rel_delta, remainder = monthmod(start_date_PersonalPension, date.date())
        value_asset = npf.fv(0.0111/12, rel_delta.months, -20412, 0)
        value_acquisition = 20412 * rel_delta.months
        mask = (df_cal["資産サブタイプ"] == "確定年金") & (df_cal["date"] == date)
        df_cal.loc[mask, "資産額"] = value_asset
        df_cal.loc[mask, "取得価格"] = value_acquisition
    return df_cal

@require_columns(["date", "資産額", "取得価格","金融機関口座","資産名"], df_arg_index=0)
def finalize_clean_data(df, df_asset_profit):
    # 資産タイプ、資産カテゴリー、資産サブタイプ、トータルリターン列を追加する
    df_added = add_columns(df)

    # 元ファイルと結合します
    df_merged = pd.concat([df_asset_profit, df_added], axis=0)

    df_finalized =  (
        df_merged
        .pipe(safe_pipe(fill_missing_dates_forward, df_asset_profit, debug=False))
        .pipe(safe_pipe(fill_missing_asset_name, df_asset_profit, debug=False))
        .pipe(safe_pipe(fill_missing_others_fast, debug=False))
        .pipe(safe_pipe(cal_pension, df_asset_profit, debug=False))
    )
    return df_finalized


