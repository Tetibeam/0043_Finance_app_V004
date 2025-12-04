from .exceptions import FileFormatError, MissingFileError, RawDataError
from .file_io import load_csv
import pandas as pd
import os


def get_latest_date_agg(df_asset_profit):
    if "date" not in df_asset_profit.columns:
        raise FileFormatError("Missing 'date' column in asset profit data.")

    if df_asset_profit.empty:
        raise RawDataError("Asset profit dataframe is empty.")

    latest = df_asset_profit["date"].max()
    if pd.isna(latest):
        raise RawDataError("'date' column contains no valid dates.")
    return latest

def get_latest_date_raw(path):
    if not os.path.exists(path):
        raise MissingFileError(f"Raw data directory not found: {path}")

    files = os.listdir(path)

    targets = []
    for f in files:
        name, ext = os.path.splitext(f)
        if len(name) == 6 and name.isdigit():  # yyMMdd
            targets.append(name)

    if not targets:
        raise RawDataError(f"No valid raw data files found in: {path}")

    latest_str = max(targets)
    return pd.to_datetime(latest_str, format="%y%m%d")

def load_balance_raw_file(start_year, end_year, path):
    dfs = []
    for year in range(start_year, end_year):
        filepath = os.path.join(path, f"{year}.csv")

        try:
            df = load_csv(filepath)
            dfs.append(df)
        except MissingFileError:
            # 年単位の欠損は想定エラーとしてログのみ
            print(f"[WARN] Missing balance file: {filepath}")
            continue
        except Exception as e:
            raise RawDataError(f"Failed to load balance file: {filepath}\n{e}")

    if not dfs:
        raise RawDataError("No balance data could be loaded.")

    return pd.concat(dfs, ignore_index=True)

