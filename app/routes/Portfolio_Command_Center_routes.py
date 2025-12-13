from flask import Blueprint, current_app,jsonify,make_response
from .Portfolio_Command_Center_service import build_PCC_payload
from werkzeug.exceptions import InternalServerError
from .routes_helper import apply_etag
import os

Portfolio_Command_Center_bp = Blueprint("Portfolio_Command_Center", __name__, url_prefix="/api/Portfolio_Command_Center")

# API 用ルート
@Portfolio_Command_Center_bp.route("/", methods=["GET"])
def index():
    """
    API root: 簡単なメタ情報を返す
    """
    payload = {
        "service": "Portfolio_Command_Center",
        "version": "1.0",
        "endpoints": {
            "graphs": "/api/Portfolio_Command_Center/graphs",
            "summary": "/api/Portfolio_Command_Center/summary"
        }
    }
    return jsonify(payload)

@Portfolio_Command_Center_bp.route("/graphs", methods=["GET"])
def graphs():
    """
    グラフ用データを返すエンドポイント。
    フロントはここから時系列データ・メタ情報を受け取り描画する。
    """
    try:
        payload = build_PCC_payload(include_graphs=True, include_summary=False)

        return apply_etag(payload)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # ログはアプリ側で出している想定
        raise InternalServerError(description=str(e))


@Portfolio_Command_Center_bp.route("/summary", methods=["GET"])
def summary():
    """
    サマリ（軽量）だけほしいフロントのための簡易エンドポイント。
    """
    try:
        payload = build_PCC_payload(include_graphs=False, include_summary=True)
        return apply_etag(payload)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise InternalServerError(description=str(e))
  