import pandas as pd
import numpy as np

def cal_total_return(df, sub_type, start_date, end_date):
    
    total_return = df.loc[df["date"] == end_date, "トータルリターン"].values[0] - df.loc[df["date"] == start_date, "トータルリターン"].values[0]
    total_asset = df.loc[(df["date"] >= start_date) & (df["date"] <= end_date), "資産額"].mean()
    return  total_return/total_asset, total_asset

def cal_sharpe_ratio(
    df, sub_type,start_date, end_date, df_asset_sub_type_attribute,
    total_return, risk_free_rate):

    df_ref = df_asset_sub_type_attribute.copy()
    df_ref["リスク"] = df_ref["リスク"].astype(float)
    annualized_volatility = df_ref.loc[
        df_ref["項目"] == sub_type, "リスク"
    ].values[0]
    if np.isnan(annualized_volatility):
        df_tmp=pd.DataFrame()
        #print(sub_type,"計算")
        df_tmp["前日の現在価値"] = df.loc[(df["date"] >= start_date) & (df["date"] <= end_date),"資産額"].shift(1)
        df_tmp["その日の積立額"] = df.loc[(df["date"] >= start_date) & (df["date"] <= end_date),"取得価格"].diff()
        df_tmp["その日の現在価値"] = df.loc[(df["date"] >= start_date) & (df["date"] <= end_date),"資産額"]

        df_tmp["その日のリターン"] = (df_tmp["その日の現在価値"] - df_tmp["前日の現在価値"] - df_tmp["その日の積立額"]) / df_tmp["前日の現在価値"]
        daily_volatility = df_tmp["その日のリターン"].dropna().std()
        annualized_volatility = daily_volatility * np.sqrt(250)

    # シャープレシオ計算
    #print(sub_type,total_return,risk_free_rate,annualized_volatility)
    if annualized_volatility == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = (total_return - risk_free_rate) / annualized_volatility
    return sharpe_ratio
