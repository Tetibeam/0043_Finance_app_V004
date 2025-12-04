import pandas as pd
import numpy as np
from ..lib import reference_data_store as urds
from .agg_balance_collection import single_filter_df_by_value, double_filter_df_by_value
from .main_helper import safe_pipe

# 対象：国内株式、投資信託、確定年金、確定拠出年金、セキュリティートークン
# 含み損益を計算
# 特徴：取得価格がある
def set_unrealized_profit(df):
    asset_sub_type = ["国内株式","投資信託","確定年金","確定拠出年金","セキュリティートークン"]

    mask = df["取得価格"].notna()&\
        (df["取得価格"] != 0)&\
        df["資産サブタイプ"].isin(asset_sub_type)&\
        ~df["金融機関口座"].str.contains("ALTERNA",na=False)&\
        ~df["資産名"].str.contains("スミセイDCたのしみ年金10年",na=False)

    df_unrealized = (
        df[mask]
        .copy()
        .assign(
            含み損益=lambda x: x["資産額"] - x["取得価格"]
        )
        .merge(
            urds.df_offset_unrealized[["資産名", "オフセット値"]],
            on="資産名",
            how="left"
        )
    )
    df_unrealized["含み損益"] -= df_unrealized["オフセット値"].fillna(0)
    df_unrealized.drop(columns=["オフセット値"], inplace=True)

    # インデックス更新
    df_source = df.set_index(["date", "資産名"])
    df_source.update(df_unrealized.set_index(["date", "資産名"]))
    df_source.reset_index(inplace=True)

    return df_source.sort_values(["date", "資産名"])

def _get_asset_name(accounts, asset_name_key, sub_type_filters=None):
    # 基本的な安全対策
    if pd.isna(asset_name_key) or not isinstance(asset_name_key, str):
        return None

    # フィルタ条件を動的に作る
    if sub_type_filters:
        mask_sub_type = urds.df_asset_type_and_category["資産サブタイプ"].isin(sub_type_filters)
    else:
        mask_sub_type = True
    mask_name = mask_sub_type & urds.df_asset_type_and_category["資産名"].str.contains(asset_name_key, na=False)

    if pd.isna(accounts) or not isinstance(accounts, str) or accounts.strip() == "":
        # 銀行名が空 ⇒ 金融機関口座を絞り込まない（全件対象）
        mask_account = True
    else:
        mask_account = urds.df_asset_type_and_category["金融機関口座"].str.contains(accounts, na=False)

    # 条件適用
    df_sub = urds.df_asset_type_and_category[mask_account & mask_name]

    # 結果
    if not df_sub.empty:
        return df_sub.iloc[0]["資産名"]
    else:
        return None

# 対象：普通預金、定期預金、仕組預金
# 預金の実現損益を計算
# 特徴：収支データに登録されている
def _cal_realized_ordinary_deposit(df_asset_profit, df_balance_raw):
    # 普通預金
    df_in = single_filter_df_by_value(df_balance_raw, "中項目", "利息-普通預金")
    df_in = df_in.groupby(["date", "保有金融機関"], as_index=False)["金額"].sum()

    df_out = single_filter_df_by_value(df_balance_raw, "中項目", "租税公課-普通預金")
    df_out = df_out.groupby(["date", "保有金融機関"], as_index=False)["金額"].sum()

    df_merged = pd.merge(df_in, df_out, on=["date", "保有金融機関"], how="outer", suffixes=("_x", "_y"))
    df_merged["実現損益"] = df_merged["金額_x"].fillna(0) + df_merged["金額_y"].fillna(0)

    df_reg = df_merged[["date", "保有金融機関", "実現損益"]].copy()

    df_reg["資産名"] = df_reg["保有金融機関"].apply(lambda x: _get_asset_name(x, "普通"))

    df_reg.drop("保有金融機関",axis=1, inplace=True)
    df_reg.set_index(["date", "資産名"], inplace=True)

    df_asset_profit_update = df_asset_profit.set_index(["date", "資産名"])

    df_asset_profit_update.update(df_reg)
    df_asset_profit_update = df_asset_profit_update.reset_index()
    return df_asset_profit_update

def _cal_realized_hybrid_deposit(df_asset_profit, df_balance_raw):
    # ハイブリッド預金
    df_in = single_filter_df_by_value(df_balance_raw, "中項目", "利息-ハイブリ")
    df_in = df_in.groupby(["date", "保有金融機関"], as_index=False)["金額"].sum()

    df_out = single_filter_df_by_value(df_balance_raw, "中項目", "租税公課-ハイブリ")
    df_out = df_out.groupby(["date", "保有金融機関"], as_index=False)["金額"].sum()

    df_merged = pd.merge(df_in, df_out, on=["date", "保有金融機関"], how="outer", suffixes=("_x", "_y"))
    df_merged["実現損益"] = df_merged["金額_x"].fillna(0) + df_merged["金額_y"].fillna(0)

    df_reg = df_merged[["date", "保有金融機関", "実現損益"]].copy()
    df_reg["資産名"] = df_reg["保有金融機関"].apply(lambda x: _get_asset_name(x, "ハイブリッド"))
    df_reg.drop("保有金融機関",axis=1, inplace=True)

    df_reg.set_index(["date", "資産名"], inplace=True)
    df_asset_profit_update = df_asset_profit.set_index(["date", "資産名"])
    df_asset_profit_update.update(df_reg)
    df_asset_profit_update = df_asset_profit_update.reset_index()
    return df_asset_profit_update

def _cal_realized_fixed_deposit(df_asset_profit, df_balance_raw):
    # 利息
    df_in = single_filter_df_by_value(df_balance_raw, "中項目", "利息-定期預金")
    df_in = df_in.groupby(["date", "保有金融機関"], as_index=False)["金額"].sum()
    df_out = single_filter_df_by_value(df_balance_raw, "中項目", "租税公課-定期預金")
    df_out = df_out.groupby(["date", "保有金融機関"], as_index=False)["金額"].sum()

    df_merged = pd.merge(df_in, df_out, on=["date", "保有金融機関"], how="outer", suffixes=("_x", "_y"))
    df_merged["実現損益"] = df_merged["金額_x"].fillna(0) + df_merged["金額_y"].fillna(0)

    df_merged = df_merged[["date", "保有金融機関", "実現損益"]]
    df_merged["資産名"] = df_merged["保有金融機関"].apply(lambda x: _get_asset_name(x, "定期"))
    df_reg_interest = df_merged[["date", "実現損益", "資産名"]]

    # 償還
    df_in = single_filter_df_by_value(df_balance_raw, "中項目", "償還-定期預金").copy()
    df_in["メモ"]= pd.to_numeric(df_in["メモ"],errors="coerce").astype("int64")

    df_in["資産名"] = pd.Series(dtype="object")
    df_in["実現損益"] = np.nan

    mask_account = df_in["保有金融機関"] == "新生銀行"
    df_in.loc[mask_account & df_in["内容"].str.contains("300005"),"資産名"] = "スタートアップ円定期預金(新生銀行)"
    df_in.loc[mask_account & df_in["内容"].str.contains("300109"),"資産名"] = "円定期預金(新生銀行)"

    df_in.loc[~mask_account, "資産名"] = df_in.loc[~mask_account,"保有金融機関"].apply(lambda x: _get_asset_name(x, "定期"))

    df_in = df_in.groupby(["date", "保有金融機関","資産名"], as_index=False)[["金額","メモ"]].sum()
    df_in["実現損益"] = df_in["金額"] - df_in["メモ"]
    df_reg_redemption = df_in[["date", "実現損益", "資産名"]]

    df_result = pd.merge(df_reg_interest,df_reg_redemption,on=["date","資産名"],how="outer")
    df_result["実現損益"] = df_result["実現損益_x"].fillna(0) + df_result["実現損益_y"].fillna(0)
    df_result.drop(["実現損益_x","実現損益_y"],axis=1)

    df_result.set_index(["date", "資産名"], inplace=True)
    df_asset_profit_update = df_asset_profit.set_index(["date", "資産名"])
    df_asset_profit_update.update(df_result)
    df_asset_profit_update = df_asset_profit_update.reset_index()
    return df_asset_profit_update

def _cal_realized_structured_deposit(df_asset_profit, df_balance_raw):
    # 仕組預⾦
    df_in = single_filter_df_by_value(df_balance_raw, "中項目", "利息-仕組預金")
    df_in = df_in.groupby(["date", "保有金融機関"], as_index=False)["金額"].sum()
    df_out = single_filter_df_by_value(df_balance_raw, "中項目", "租税公課-仕組預金")
    df_out = df_out.groupby(["date", "保有金融機関"], as_index=False)["金額"].sum()

    df_merged = pd.merge(df_in, df_out, on=["date", "保有金融機関"], how="outer", suffixes=("_x", "_y"))
    df_merged["実現損益"] = df_merged["金額_x"].fillna(0) + df_merged["金額_y"].fillna(0)

    df_reg = df_merged[["date", "保有金融機関", "実現損益"]].copy()
    df_reg["資産名"] = df_reg["保有金融機関"].apply(lambda x: _get_asset_name(x, "仕組"))
    df_reg.drop("保有金融機関",axis=1, inplace=True)

    df_reg.set_index(["date", "資産名"], inplace=True)
    df_asset_profit_update = df_asset_profit.set_index(["date", "資産名"])
    df_asset_profit_update.update(df_reg)
    df_asset_profit_update = df_asset_profit_update.reset_index()
    return df_asset_profit_update

def set_realized_deposit(df_asset_profit, df_balance_raw):
    return (
        df_asset_profit
        .pipe(safe_pipe(_cal_realized_ordinary_deposit, df_balance_raw))
        .pipe(safe_pipe(_cal_realized_hybrid_deposit, df_balance_raw))
        .pipe(safe_pipe(_cal_realized_fixed_deposit, df_balance_raw))
        .pipe(safe_pipe(_cal_realized_structured_deposit, df_balance_raw))
    )

# 対象：MRF,外貨普通預金
# 利金収益や為替変動による実現損益を計算
# 特徴：収支データに登録されない、取得価格がないため、口座残高のみ
def set_realized_mrf(df_asset_profit):
    df = df_asset_profit
    asset_name_key = ["MRF(静銀ティーエム証券)", "外貨普通預金"]
    dfs = []

    target_mask = df["資産名"].str.contains("MRF\\(静銀ティーエム証券\\)|外貨普通預金", na=False, regex=True)
    df_target = df.loc[target_mask].copy()

    df_target["実現損益"] = (
        df_target.groupby("資産名")["資産額"]
        .diff()
        .where(lambda x: x.abs() < 2000, 0)
        .fillna(0)
    )

    # 元データに反映
    df.set_index(["date", "資産名"], inplace=True)
    df_target.set_index(["date", "資産名"], inplace=True)
    df.update(df_target)
    df.reset_index(inplace=True)

    return df

# 対象：日本国債、円建社債
# 実現損益を計算:利金集計を計算
# 特徴：収支データに登録されている
def set_realized_interest(df_asset_profit,df_balance_raw):
    df_in = single_filter_df_by_value(df_balance_raw, "中項目", "利金収益").copy()

    df_in["保有金融機関"] = pd.Series(dtype="object")
    df_in["資産名"] = df_in.apply(
        lambda row: _get_asset_name(row["保有金融機関"], row["内容"]),
        axis=1
    )

    df_in["実現損益"] = df_in["金額"]
    df_reg = df_in[["date", "資産名", "実現損益"]].copy()

    df_reg.set_index(["date", "資産名"], inplace=True)
    df_asset_profit_update = df_asset_profit.set_index(["date", "資産名"])
    df_asset_profit_update.update(df_reg)
    df_asset_profit_update = df_asset_profit_update.reset_index()
    return df_asset_profit_update

# 対象：国内株式、セキュリティートークン
# 配当と売却損益から実現損益を計算
# 特徴：配当は収支データから、売薬損益は取得価格の変動から算出
def set_realized_dividend(df_balance_raw):
    df_in = single_filter_df_by_value(df_balance_raw, "中項目", "配当所得").copy()
    df_in["実現損益"] = df_in["金額"]
    df_in["保有金融機関"] = pd.Series(dtype="object")
    df_in["資産名"] = df_in.apply(
        lambda row: _get_asset_name(row["保有金融機関"], row["メモ"],["国内株式","セキュリティートークン"]),
        axis=1
    )
    return df_in[["date", "資産名", "実現損益"]]

def _set_realized_capital(df_asset_profit,df_balance_raw):
    # 対象資産名
    target_sub_type = ["国内株式","投資信託","セキュリティートークン"]
    df = urds.df_asset_type_and_category.copy()
    mask = df["資産サブタイプ"].isin(target_sub_type) &\
        (df["金融機関口座"] != "ALTERNA") &\
        (df["金融機関口座"] != "FOLIO")
    target_asset = df[mask]["資産名"].to_list()

    df = df_asset_profit.set_index("date")
    df_tmp = pd.DataFrame(columns=["date","資産名","実現損益"])

    for asset in target_asset:
        df_diff = df[df["資産名"] == asset]["取得価格"].diff().fillna(0)
        df_sale = df_diff[df_diff<-5]
        for date, value in df_sale.items():
            mask = (df.index == (date-pd.Timedelta(days=1))) & (df["資産名"] == asset)
            predate_acquisition = df[mask]["取得価格"].iloc[0]
            predate_unrealized_profit = df[mask]["含み損益"].iloc[0]
            gain_loss_on_sale= predate_unrealized_profit * abs(value / predate_acquisition)
            df_tmp.loc[len(df_tmp)] = {"date":date, "資産名":asset, "実現損益":gain_loss_on_sale}
    return df_tmp

def set_realized_dividend_and_capital(df_asset_profit,df_balance_raw):
    # 配当所得
    df_reg_dividend = set_realized_dividend(df_balance_raw)
    # 売却損益
    df_reg_capital = _set_realized_capital(df_asset_profit,df_balance_raw)
    # 結合
    df_reg_dividend_and_capital = pd.merge(
        df_reg_dividend, df_reg_capital, on=["date","資産名"], how="outer", suffixes=["_x","_y"]
    )
    df_reg_dividend_and_capital["実現損益"] = df_reg_dividend_and_capital["実現損益_x"].fillna(0) +\
        df_reg_dividend_and_capital["実現損益_y"].fillna(0)
    df_reg_dividend_and_capital.drop(["実現損益_x", "実現損益_y"],axis=1,inplace=True)

    # 更新
    df = df_asset_profit.set_index(["date", "資産名"])
    df_reg_dividend_and_capital.set_index(["date", "資産名"], inplace=True)
    df.update(df_reg_dividend_and_capital)
    df = df.reset_index()
    return df

def _prepare_in_out(df_balance_raw, account):
    # 入出金額
    if account == "クラウドバンク":
        df_in = double_filter_df_by_value(df_balance_raw, "大項目", "その他", "中項目", "資金移動")
        df_in = single_filter_df_by_value(df_in, "内容", "クラウド")
        df_in["金額"] = df_in["金額"] *-1
        return df_in
    elif account == "ALTERNA":
        df_in = double_filter_df_by_value(df_balance_raw, "大項目", "収入", "中項目", "資金移動")
        df_in = single_filter_df_by_value(df_in, "保有金融機関", account)
        df_out = double_filter_df_by_value(df_balance_raw, "大項目", "その他", "中項目", "資金移動")
        df_out = single_filter_df_by_value(df_out, "内容", "三井物産")
        return pd.concat([df_in,df_out],axis=0)
    else:
        df_in = double_filter_df_by_value(df_balance_raw, "大項目", "収入", "中項目", "資金移動")
        df_in = single_filter_df_by_value(df_in, "保有金融機関", account)
        return df_in

def set_realized_cloud_funds(df_asset_profit, start_date, end_date, df_balance_raw):
    df_keys = urds.df_asset_type_and_category.copy()
    df_values = df_asset_profit.copy()

    sub_type_list = ["ソーシャルレンディング", "セキュリティートークン"]

    mask = (df_keys["資産サブタイプ"].isin(sub_type_list))&\
        ~df_keys["金融機関口座"].str.contains("SBI ST口座")
    accounts = df_keys[mask]["金融機関口座"].unique().tolist()
    dfs = []
    for account in accounts:
        # 総投資額
        mask = (df_values["資産サブタイプ"].isin(sub_type_list))&\
            df_values["金融機関口座"].str.contains(account)
        df_current_invest = df_values[mask].groupby("date").sum()["資産額"]

        # 口座残高
        mask = (df_keys["資産サブタイプ"] == "預入金")&\
            df_keys["金融機関口座"].str.contains(account)
        df_asset_name = df_keys[mask]["資産名"].to_list()
        mask = df_values["資産名"].isin(df_asset_name)
        df_current_account_balance = df_values[mask].groupby("date").sum()["資産額"]

        # 入出金額
        df_in_out = (
            _prepare_in_out(df_balance_raw, account)
            .drop(["内容","保有金融機関","大項目","中項目","メモ"],axis=1)
            .set_index("date")
            .reindex(pd.date_range(start=start_date, end=end_date, freq ="D"))
            .resample('D').first().fillna(0).cumsum()
            .reindex(df_current_invest.index)
        )
        df_total_in_out = df_in_out["金額"]

        results =(
            (df_current_invest + df_current_account_balance - df_total_in_out)
            .diff().fillna(0)
            .rename("実現損益")
            .reset_index()
        )

        mask = (df_keys["資産サブタイプ"] == "預入金")&\
            df_keys["金融機関口座"].str.contains(account)
        results["資産名"] = df_keys[mask]["資産名"].iloc[0]
        dfs.append(results)

    df_reg = pd.concat(dfs,ignore_index=True)

    df_reg.set_index(["date", "資産名"], inplace=True)
    df = df_asset_profit.set_index(["date", "資産名"])
    df.update(df_reg)
    df = df.reset_index()

    return df

def set_total_returns(df_asset_profit):
    df = df_asset_profit.copy()
    df[["含み損益","実現損益"]] = df[["含み損益","実現損益"]].fillna(0)

    df.set_index("date", inplace=True)

    df["実現損益累積和"] = df.groupby(["資産名","資産サブタイプ"])["実現損益"].cumsum()
    df["トータルリターン"] = df["実現損益累積和"] + df["含み損益"]

    mask = df["資産名"].isna()
    df.loc[mask,"実現損益累積和"] = df[mask].groupby(["資産サブタイプ"])["実現損益"].cumsum()
    df.loc[mask,"トータルリターン"] = df.loc[mask,"実現損益累積和"] + df.loc[mask,"含み損益"]

    df.drop(columns=["実現損益累積和"], inplace=True)
    df.reset_index(inplace=True)
    return df

def _get_loan_interest_rate(date):
    # 2024/10/1 - 2025/1/1: 0.65%
    if date < pd.Timestamp("2025-01-01"):
        return 0.0065
    # 2025/1/1 - 2025/7/1: 0.75%
    elif date < pd.Timestamp("2025-07-01"):
        return 0.0075
    # 2025/7/1 - ... : 1.0%
    else:
        return 0.0100

def set_loan_balance(df_asset_profit, START_DATE, end_date, df_balance):
    df = df_asset_profit.set_index("date").copy()

    mask = df_balance["収支項目"].isin(["ローン返済", "ローン一括"])
    loan_repayment = (
        df_balance[mask]
        .groupby("date")["目標"]
        .sum()
        .reindex(pd.date_range(START_DATE, end_date), fill_value=0)
    )

    current_balance = -22424499.520794038    # 2024/10/1
    dates = loan_repayment.index
    
    debt_mask = df["資産タイプ"] == "負債"
    for d, repayment in loan_repayment.items():
        rate = _get_loan_interest_rate(d)
        daily_interest = current_balance * rate / 365

        new_balance = current_balance + daily_interest - repayment
        new_balance = min(new_balance, 0)
        current_balance = new_balance

        if d in df.index:
            df.loc[debt_mask & (df.index == d), "資産額"] = new_balance

    df.reset_index(inplace=True)
    return df
