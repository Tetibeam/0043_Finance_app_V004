from .utils.make_target import make_target_main
from .utils.asset_aggregation import make_asset_main
from .utils.balance_aggregation import make_balance_main
from .utils.profit_aggregation import make_profit_main
from .utils.make_cache import make_cache_main


from .lib.file_io import load_parquet, save_csv, load_csv
from .lib.agg_settings import PATH_ASSET_PROFIT_DETAIL, PATH_BALANCE_DETAIL
PATH_ASSET_PROFIT_DETAIL_DEV = "G:/マイドライブ/AssetManager/total/output/asset_detail_test2.parquet"

import os
import requests
import pandas as pd
import logging
import argparse
from app.utils.db_manager import init_db
from pathlib import Path

# APIベースURL
API_BASE = os.environ.get("API_BASE_URL", "http://localhost:5000")

# データソース
from batch.lib.agg_settings import (
    PATH_ASSET_PROFIT_DETAIL_TEST2, PATH_BALANCE_DETAIL
)
from batch.lib.target_settings import PATH_TARGET_ASSET_PROFIT, PATH_TARGET_PARAMETER, PATH_TARGET_RATE

# ロガーの設定
logger = logging.getLogger(__name__)

def update_master_file(args):
    """
    データを更新し、マスターファイルを更新する。
    """
    logger.info("Master update started.")
    try:
        # データ更新しマスターファイルを保存する
        make_target_main()
        if args == "with_aggregation":
            make_asset_main()
            make_balance_main()
        make_profit_main()

        logger.info("Master files update finished.")

    except Exception as e:
        logger.error(f"Master files update failed: {e}")
        raise

def get_latest_date_from_api():
    """
    APIから最新日付を取得する。
    """
    logger.info("Get latest date from API started.")
    try:
        # APIをたたいて、DBの最新日付を取得する
        res = requests.get(f"{API_BASE}/api/Portfolio_Command_Center/summary", timeout=10)
        res.raise_for_status() # エラーチェック
        data = res.json()
        latest_date = pd.to_datetime(data["summary"]["latest_date"])# - pd.Timedelta(days=1)
        logger.info(f"Latest date from API: {latest_date}")
        return latest_date
    except Exception as e:
        logger.error(f"Get latest date from API failed: {e}")
        raise

def update_db():
    """
    APIへデータをアップロードしてDBを更新する。
    """
    logger.info("Update db started.")
    try:
        # ---------------------------------------------------------
        # APIへデータをアップロードしてDBを更新する
        # ---------------------------------------------------------
        upload_url = f"{API_BASE}/api/data/upload/all"
        logger.info(f"Uploading data to {upload_url}...")

        try:
            # with 文で複数ファイルを同時に開く
            with open(PATH_ASSET_PROFIT_DETAIL_TEST2, "rb") as asset_profit_detail,\
                open(PATH_BALANCE_DETAIL, "rb") as balance_detail,\
                open(PATH_TARGET_ASSET_PROFIT, "rb") as target_asset_profit,\
                open(PATH_TARGET_PARAMETER, "rb") as target_parameter,\
                open(PATH_TARGET_RATE, "rb") as target_rate:

                files = {
                    "file_asset_profit_detail": ("file_asset_profit_detail", asset_profit_detail, "application/octet-stream"),
                    "file_balance_detail": ("file_balance_detail", balance_detail, "application/octet-stream"),
                    "file_target_asset_profit": ("file_target_asset_profit", target_asset_profit, "application/octet-stream"),
                    "file_target_parameter": ("file_target_parameter", target_parameter, "application/octet-stream"),
                    "file_target_rate": ("file_target_rate", target_rate, "application/octet-stream"),
                }
            
                resp = requests.post(upload_url, files=files, timeout=30)
                resp.raise_for_status()
                result = resp.json()
                logger.info(f"Upload successful: {result}")

        except Exception as e:
            logger.error(f"Failed to upload cache data: {e}")
            raise

    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

if __name__ == "__main__":
    # ロガーの設定を追加
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # --- 引数定義 ---
    parser = argparse.ArgumentParser(description="DB updater")
    parser.add_argument(
        "--mode",
        choices=["with_aggregation", "without_aggregation"],
        default="with_aggregation",
        help="実行モードを指定 (with_aggregation|wtihout_aggregation)"
    )

    args = parser.parse_args()
    
    #master files(incl. for master/ cache)
    update_master_file(args.mode)

    #latest_date = get_latest_date_from_api()

    # cache db
    update_db()

    


