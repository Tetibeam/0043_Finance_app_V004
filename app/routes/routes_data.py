from flask import Blueprint, request, jsonify, current_app
import os
import io
import pandas as pd
import sqlite3
from werkzeug.exceptions import BadRequest, InternalServerError
from app.utils.data_loader import update_from_csv,replace_to_table

data_bp = Blueprint("data", __name__, url_prefix="/api/data")

@data_bp.route("/upload/all", methods=["POST"])
def upload_all():
    # 1. ファイルの取得
    required_keys = [
        "file_asset_profit_detail", "file_balance_detail",
        "file_target_asset_profit", "file_target_parameter", "file_target_rate"
    ]
    missing = [k for k in required_keys if k not in request.files]
    if missing:
        raise BadRequest(f"Missing required files: {', '.join(missing)}")

    try:
        # 2. バイナリを読み取って Parquet → DataFrame
        dfs = {}
        for key in required_keys:
            file_storage = request.files[key]     # FileStorage object
            binary = file_storage.read()          # バイナリ読み込み

            # Parquet はバイナリから直接 DataFrame にできる
            dfs[key] = pd.read_parquet(io.BytesIO(binary))

    except Exception as e:
        return jsonify({"error": f"Failed to read parquet: {e}"}), 500

    try:
        # 3. DataFrame を DB に書き込む
        replace_to_table(dfs["file_asset_profit_detail"], "asset_profit_detail")
        replace_to_table(dfs["file_balance_detail"], "balance_detail")
        replace_to_table(dfs["file_target_asset_profit"], "target_asset_profit")
        replace_to_table(dfs["file_target_parameter"], "target_parameter")
        replace_to_table(dfs["file_target_rate"], "target_rate")
    
    except Exception as e:
        return jsonify({"error": f"DB write failed: {e}"}), 500

    # 4. 完了レスポンス
    return jsonify({
        "status": "success",
        "rows": {
            "asset_profit_detail": len(dfs["file_asset_profit_detail"]),
            "balance_detail": len(dfs["file_balance_detail"]),
            "target_asset_profit": len(dfs["file_target_asset_profit"]),
            "target_parameter": len(dfs["file_target_parameter"]),
            "target_rate": len(dfs["file_target_rate"])    
        }
    })
