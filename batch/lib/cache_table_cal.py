import pandas as pd

def _filter_by_date(df, start_date, end_date):
    df = df.copy()
    return df[(df['date'] >= start_date) & (df['date'] <= end_date)]

def _aggregate_asset_period(df, period_type, agg_dict):
    df_agg = (
        df
        .assign(date=df['date'].dt.to_period(period_type))
        .groupby(['date', '資産名'], as_index=False)
        .agg(agg_dict)
    )
    df_agg["date"] = df_agg["date"].dt.to_timestamp()
    df_agg.reset_index(drop=True, inplace=True)
    return df_agg

def _group_date_agg(df, output_list, freq=None, resample_agg_dict=None):
    df_grouped = df.set_index("date").groupby("date")[output_list].sum()
    if freq and resample_agg_dict:
        df_grouped = df_grouped.resample(freq).agg(resample_agg_dict)
    return df_grouped

def _process_single_filters(df, columns_matrix, output_list, freq, resample_agg_dict, rename_func):
    dfs = []
    for col, values in columns_matrix.items():
        for value in values:
            df_tmp = df[df[col] == value]
            df_res = _group_date_agg(df_tmp, output_list, freq, resample_agg_dict)
            new_cols = {c: rename_func(col, value, c) for c in df_res.columns}
            dfs.append(df_res.rename(columns=new_cols))
    return dfs

def _process_category_section(df, start_date, end_date, output_list, columns_matrix, freq, agg_dict, rename_total_map, rename_filter_func):
    df = _filter_by_date(df, start_date, end_date)
    
    # Total
    df_total = _group_date_agg(df, output_list, freq, agg_dict)
    df_total = df_total.rename(columns=rename_total_map)
    
    # Single Filters
    dfs = _process_single_filters(df, columns_matrix, output_list, freq, agg_dict, rename_filter_func)

    # Double Filters
    # ---- ここに2重フィルターの関数をつくって処理を追加します ---- 
    return pd.concat([df_total] + dfs, axis=1)

def _process_category_calculated_columns(df_asset, df_target_res, df_balance_res, table_type):
    # ----
    # すべて共通
    df_calculated = df_asset["資産_実績_資産額"] / df_target_res["資産_目標_資産額"]
    df_calculated.name = "資産_進捗率"
    df_calculated = df_calculated.to_frame()

    if table_type == "MONTHLY" or table_type == "YEARLY":
        df_savings_rate = pd.DataFrame()
        df_savings_rate = df_savings_rate.assign(
            資産_実績_貯蓄率=(
                (df_balance_res["収支_実績"] + df_asset["資産_実績_トータルリターン"].diff()) /
                df_balance_res["収支_実績_収支カテゴリー_収入"]
            )
        )
        df_savings_rate = df_savings_rate.assign(
            資産_目標_貯蓄率=(
                (df_balance_res["収支_目標"] + df_target_res["資産_目標_トータルリターン"].diff()) /
                df_balance_res["収支_目標_収支カテゴリー_収入"]
            )
        )
        df_calculated = pd.concat([df_calculated, df_savings_rate], axis=1)
    return df_calculated
    
def _make_asset_cache_aggregated(df_asset_profit, start_date, end_date, period_type):
    df = _filter_by_date(df_asset_profit, start_date, end_date)
    agg_dict = {
        "資産タイプ": 'first',
        "資産カテゴリー": 'first',
        "資産サブタイプ": 'first',
        "金融機関口座": 'first',
        "資産額": 'last',
        "トータルリターン": 'last',
        '含み損益': 'last',
        '実現損益': 'sum',
        '取得価格': 'last',
    }
    return _aggregate_asset_period(df, period_type, agg_dict)

# 資産名ごとのキャッシュDB用 - LONG型
def make_asset_cache_daily(df_asset_profit, start_date, end_date):
    df = _filter_by_date(df_asset_profit, start_date, end_date)
    df.reset_index(drop=True, inplace=True)
    return df

def make_asset_cache_monthly(df_asset_profit, start_date, end_date):
    return _make_asset_cache_aggregated(df_asset_profit, start_date, end_date, 'M')

def make_asset_cache_yearly(df_asset_profit, start_date_yearly, end_date):
    return _make_asset_cache_aggregated(df_asset_profit, start_date_yearly, end_date, 'Y')

# カテゴリーごとのキャッシュDB用 - WIDE型
def make_category_cache_daily(df_asset_profit, df_balance, df_target, start_date, end_date):
    # 資産 - 実績
    df_asset = _process_category_section(
        df_asset_profit, start_date, end_date,
        output_list=["資産額", "トータルリターン", "含み損益", "実現損益", "取得価格"],
        columns_matrix={
            "資産タイプ": df_asset_profit["資産タイプ"].unique().tolist(),
            #"資産カテゴリー": df_asset_profit["資産カテゴリー"].unique().tolist(),
            #"資産サブタイプ": df_asset_profit["資産サブタイプ"].unique().tolist(),
            #"金融機関口座": df_asset_profit["金融機関口座"].unique().tolist()
        },
        freq=None, agg_dict=None,
        rename_total_map=lambda c: f"資産_実績_{c}",
        rename_filter_func=lambda col, val, c: f"資産_実績_{col}_{val}_{c}"
    )

    # 資産 - 目標
    df_target_res = _process_category_section(
        df_target, start_date, end_date,
        output_list=["資産額", "トータルリターン"],
        columns_matrix={"資産タイプ": df_target["資産タイプ"].unique().tolist()},
        freq=None, agg_dict=None,
        rename_total_map=lambda c: f"資産_目標_{c}",
        rename_filter_func=lambda col, val, c: f"資産_目標_{col}_{val}_{c}"
    )

    # 収支
    df_balance_res = _process_category_section(
        df_balance, start_date, end_date,
        output_list=["金額", "目標"],
        columns_matrix={
            "収支タイプ": df_balance["収支タイプ"].unique().tolist(),
            "収支カテゴリー": df_balance["収支カテゴリー"].unique().tolist(),
            #"収支項目": df_balance["収支項目"].unique().tolist()
        },
        freq=None, agg_dict=None,
        rename_total_map={"金額": "収支_実績", "目標": "収支_目標"},
        rename_filter_func=lambda col, val, c: f"収支_実績_{col}_{val}" if c == "金額" else f"収支_目標_{col}_{val}"
    )

    # 計算列の作成
    df_calculated_cols = _process_category_calculated_columns(df_asset, df_target_res, df_balance_res, "DAILY")

    df_total = pd.concat([df_asset, df_target_res, df_balance_res, df_calculated_cols], axis=1)
    df_total.reset_index(inplace=True)

    return df_total

def make_category_cache_monthly(df_asset_profit, df_balance, df_target, start_date, end_date):
    # 資産 - 実績
    df_asset = _process_category_section(
        df_asset_profit, start_date, end_date,
        output_list=["資産額", "トータルリターン", "含み損益", "実現損益", "取得価格"],
        columns_matrix={
            "資産タイプ": df_asset_profit["資産タイプ"].unique().tolist(),
            #"資産カテゴリー": df_asset_profit["資産カテゴリー"].unique().tolist(),
            #"資産サブタイプ": df_asset_profit["資産サブタイプ"].unique().tolist(),
            #"金融機関口座": df_asset_profit["金融機関口座"].unique().tolist()
        },
        freq='ME',
        agg_dict={
            "資産額": "last", "トータルリターン": "last", "含み損益": "last",
            "実現損益": "sum", "取得価格": "last",
        },
        rename_total_map=lambda c: f"資産_実績_{c}",
        rename_filter_func=lambda col, val, c: f"資産_実績_{col}_{val}_{c}"
    )

    # 資産 - 目標
    df_target_res = _process_category_section(
        df_target, start_date, end_date,
        output_list=["資産額", "トータルリターン"],
        columns_matrix={"資産タイプ": df_target["資産タイプ"].unique().tolist()},
        freq='ME',
        agg_dict={"資産額": "last", "トータルリターン": "last"},
        rename_total_map=lambda c: f"資産_目標_{c}",
        rename_filter_func=lambda col, val, c: f"資産_目標_{col}_{val}_{c}"
    )

    # 収支
    df_balance_res = _process_category_section(
        df_balance, start_date, end_date,
        output_list=["金額", "目標"],
        columns_matrix={
            "収支タイプ": df_balance["収支タイプ"].unique().tolist(),
            "収支カテゴリー": df_balance["収支カテゴリー"].unique().tolist(),
            #"収支項目": df_balance["収支項目"].unique().tolist()
        },
        freq='ME',
        agg_dict={"金額": "sum", "目標": "sum"},
        rename_total_map={"金額": "収支_実績", "目標": "収支_目標"},
        rename_filter_func=lambda col, val, c: f"収支_実績_{col}_{val}" if c == "金額" else f"収支_目標_{col}_{val}"
    )
    print(df_balance_res.columns)

    # 計算列の作成
    df_calculated_cols = _process_category_calculated_columns(df_asset, df_target_res, df_balance_res, "MONTHLY")
    df_total = pd.concat([df_asset, df_target_res, df_balance_res, df_calculated_cols], axis=1)
    df_total.reset_index(inplace=True)

    return df_total

def make_category_cache_yearly(df_asset_profit, df_balance, df_target, start_date_yearly, end_date):
    # 資産 - 実績
    df_asset = _process_category_section(
        df_asset_profit, start_date_yearly, end_date,
        output_list=["資産額", "トータルリターン", "含み損益", "実現損益", "取得価格"],
        columns_matrix={
            "資産タイプ": df_asset_profit["資産タイプ"].unique().tolist(),
            #"資産カテゴリー": df_asset_profit["資産カテゴリー"].unique().tolist(),
            #"資産サブタイプ": df_asset_profit["資産サブタイプ"].unique().tolist(),
            #"金融機関口座": df_asset_profit["金融機関口座"].unique().tolist()
        },
        freq='YE',
        agg_dict={
            "資産額": "last", "トータルリターン": "last", "含み損益": "last",
            "実現損益": "sum", "取得価格": "last",
        },
        rename_total_map=lambda c: f"資産_実績_{c}",
        rename_filter_func=lambda col, val, c: f"資産_実績_{col}_{val}_{c}"
    )

    # 資産 - 目標
    df_target_res = _process_category_section(
        df_target, start_date_yearly, end_date,
        output_list=["資産額", "トータルリターン"],
        columns_matrix={"資産タイプ": df_target["資産タイプ"].unique().tolist()},
        freq='YE',
        agg_dict={"資産額": "last", "トータルリターン": "last"},
        rename_total_map=lambda c: f"資産_目標_{c}",
        rename_filter_func=lambda col, val, c: f"資産_目標_{col}_{val}_{c}"
    )

    # 収支
    df_balance_res = _process_category_section(
        df_balance, start_date_yearly, end_date,
        output_list=["金額", "目標"],
        columns_matrix={
            "収支タイプ": df_balance["収支タイプ"].unique().tolist(),
            "収支カテゴリー": df_balance["収支カテゴリー"].unique().tolist(),
            #"収支項目": df_balance["収支項目"].unique().tolist()
        },
        freq='YE',
        agg_dict={"金額": "sum", "目標": "sum"},
        rename_total_map={"金額": "収支_実績", "目標": "収支_目標"},
        rename_filter_func=lambda col, val, c: f"収支_実績_{col}_{val}" if c == "金額" else f"収支_目標_{col}_{val}"
    )

    # 計算列の作成
    df_calculated_cols = _process_category_calculated_columns(df_asset, df_target_res, df_balance_res, "YEARLY")

    df_total = pd.concat([df_asset, df_target_res, df_balance_res, df_calculated_cols], axis=1)
    df_total.reset_index(inplace=True)
    return df_total