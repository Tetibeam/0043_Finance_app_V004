import pandas as pd
import os
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
from concurrent.futures import ProcessPoolExecutor, as_completed
from .decorator import check_args_types, require_columns, require_columns_with_dtype

#V002
def process_single_pdf(date, PATH_ASSET_RAW_DATA):
    fname = date.strftime("%y%m%d")
    file_path = os.path.join(PATH_ASSET_RAW_DATA, fname + ".pdf")
    tables_by_file = []

    if not os.path.exists(file_path):
        print(f"[WARN] PDF not found: {file_path}")
        return fname, tables_by_file

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                try:
                    tables = page.find_tables()
                    #if "251110" in file_path:
                    #    print(file_path, page_idx, len(tables))
                except Exception as e:
                    print(f"[ERROR] Failed to detect tables in {fname} page {page_idx}: {e}")
                    continue

                for table in tables:
                    try:
                        data = table.extract()
                    except Exception as e:
                        print(f"[ERROR] Failed to extract table in {fname} page {page_idx}: {e}")
                        continue

                    if not data or not data[0]:
                        continue

                    header = data[0]
                    if "預⾦・現⾦・暗号資産" not in header:
                        tables_by_file.append(data)

    except PDFSyntaxError as e:
        print(f"[ERROR] Corrupted PDF (syntax error): {file_path}")
        print("        Details:", e)
    except Exception as e:
        print(f"[ERROR] Unexpected error while reading PDF: {file_path}")
        print("        Details:", e)

    return fname, tables_by_file

@check_args_types({0: pd.Timestamp, 1: pd.Timestamp})
def load_asset_raw_from_pdf(start_date, end_date, PATH_ASSET_RAW_DATA, max_workers=None):
    all_tables_by_file = {}
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    # --- 重要：WindowsではProcessPoolExecutor を mainブロック内で実行すること ---
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_pdf, date, PATH_ASSET_RAW_DATA): date
            for date in dates
        }

        for future in as_completed(futures):
            fname, tables = future.result()
            if tables:
                all_tables_by_file[fname] = tables

    return all_tables_by_file

def get_asset_raw_from_table(all_tables_by_file):
    if not isinstance(all_tables_by_file, dict):
        raise TypeError("all_tables_by_file は dict を期待しています")

    # 資産名、現在価値、取得価格などをサーチして取得する
    df_raw_data = pd.DataFrame(columns=["date","資産名","金融機関口座","資産額","取得価格","保有数","評価損益","平均取得単価"])
    for file, file_data in all_tables_by_file.items():
        for table in file_data:
            # ---- (1) table 構造チェック ----
            if not table or not table[0]:
                continue
            # ---- (2) ヘッダー判定 ----
            try:
                if table[0][0] == "預⾦‧現⾦‧暗号資産":
                    continue
            except Exception:
                continue
            # ---- (3) DataFrame 変換 ----
            try:
                df_table = pd.DataFrame(table[1:], columns=table[0])
            except Exception as e:
                print(f"[ERROR] Failed to convert table in {file}: {e}")
                continue

            # 新しい一時データフレーム（共通カラム構成で作る）
            tmp_df = pd.DataFrame(columns=df_raw_data.columns)

            # 各列をスキャンして、対応する標準カラムにマッピング
            col_map = {
                ("種類‧名称", "種類・名称", "銘柄名", "名称"): "資産名",
                ("保有⾦融機関",): "金融機関口座",
                ("残⾼", "評価額", "現在価値", "現在の価値"): "資産額",
                ("取得価額",): "取得価格",
                ("保有数",): "保有数",
                ("評価損益",): "評価損益",
                ("平均取得単価",): "平均取得単価"
            }

            for key_tuple, target_col in col_map.items():
                for col in key_tuple:
                    if col in df_table.columns:
                        tmp_df[target_col] = df_table[col]
                        break  # 見つかったら次へ（重複防止）

            # ---- (5) 日付追加 ----
            try:
                tmp_df["date"] = pd.to_datetime(file, format="%y%m%d")
            except Exception:
                print(f"[ERROR] Invalid date format in file name: {file}")
                continue
            # ---- (6) tmp_df が実質空ならスキップ ----
            if tmp_df.dropna(how="all").empty:
                continue
            # ---- (7) カラム全 NaN drop（初回はしない）----
            bad_cols = df_raw_data.columns[df_raw_data.isna().all()]
            if len(bad_cols) > 0:
                df_raw_data = df_raw_data.drop(columns=bad_cols)

            df_raw_data = pd.concat([df_raw_data, tmp_df], ignore_index=True)

    return df_raw_data
